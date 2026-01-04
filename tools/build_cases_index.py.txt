import json, re, sys, os, hashlib
from pathlib import Path
from urllib.request import urlopen, Request

# pip install pypdf
from pypdf import PdfReader

OUT_DIR = Path("docs/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST = Path("cases/manifest.json")
INDEX_OUT = OUT_DIR / "index.json"

def clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def fetch_pdf(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "BarberCamPreviewIndexer/1.0"})
    with urlopen(req, timeout=60) as r:
        return r.read()

def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    pages_with_text = 0
    for page in reader.pages:
        t = page.extract_text() or ""
        t = clean_text(t)
        if t:
            pages_with_text += 1
            parts.append(t)
    return ("\n".join(parts), pages_with_text)

def snippet(text: str, max_len: int = 240) -> str:
    t = clean_text(text)
    return t[:max_len] + ("…" if len(t) > max_len else "")

if __name__ == "__main__":
    import io

    if not MANIFEST.exists():
        print(f"Missing {MANIFEST}. Create cases/manifest.json first.", file=sys.stderr)
        sys.exit(2)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    index = []

    for item in manifest:
        url = item["url"]
        title = item.get("title") or item.get("id") or url
        case_id = item.get("id") or title
        tags = item.get("tags", [])

        try:
            pdf = fetch_pdf(url)
        except Exception as e:
            index.append({
                "caseId": case_id,
                "title": title,
                "url": url,
                "tags": tags,
                "ok": False,
                "error": f"download_failed: {e}",
            })
            continue

        # Extract text layer
        try:
            reader = PdfReader(io.BytesIO(pdf))
            all_text = []
            pages_with_text = 0
            for i, page in enumerate(reader.pages):
                t = page.extract_text() or ""
                t = clean_text(t)
                if t:
                    pages_with_text += 1
                    all_text.append(t)
            text = "\n".join(all_text)
        except Exception as e:
            index.append({
                "caseId": case_id,
                "title": title,
                "url": url,
                "tags": tags,
                "ok": False,
                "error": f"parse_failed: {e}",
            })
            continue

        # If no text layer, mark OCR needed (we’ll add OCR pipeline next)
        ocr_needed = pages_with_text == 0

        index.append({
            "caseId": case_id,
            "title": title,
            "url": url,
            "tags": tags,
            "ok": True,
            "ocrNeeded": ocr_needed,
            "textHash": sha1(text) if text else None,
            "snippet": snippet(text) if text else "",
            "text": text,  # NOTE: this makes the JSON big; keep for MVP demo
        })

    INDEX_OUT.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {INDEX_OUT} ({len(index)} records)")
