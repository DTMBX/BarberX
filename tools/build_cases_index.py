import hashlib
import io
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request

# pip install pypdf
from pypdf import PdfReader

OUT_DIR = Path("docs/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST = Path("cases/manifest.json")
INDEX_OUT = OUT_DIR / "index.json"
MAX_SNIPPET_LENGTH = 240

# Maximum snippet length for text previews
MAX_SNIPPET_LENGTH = 240

# Maximum PDF file size in bytes (50 MB) to prevent memory exhaustion
MAX_PDF_SIZE = 50 * 1024 * 1024

# Chunk size for reading PDF data in bytes
CHUNK_SIZE = 8192

# Timeout for PDF downloads in seconds
PDF_DOWNLOAD_TIMEOUT = 60

def clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def fetch_pdf(url: str) -> bytes:
    # Validate URL scheme for security
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme. Only http:// and https:// are allowed: {url}")
    
    req = Request(url, headers={"User-Agent": "BarberCamPreviewIndexer/1.0"})
    with urlopen(req, timeout=PDF_DOWNLOAD_TIMEOUT) as r:
        # Check content length to prevent downloading files that are too large
        content_length = r.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
            except ValueError:
                # If content length is invalid, proceed but enforce size limit during read
                size = None
            
            if size is not None and size > MAX_PDF_SIZE:
                raise ValueError(f"PDF file too large: {size} bytes (max: {MAX_PDF_SIZE})")
        
        # Read data in chunks with size limit
        chunks = []
        total_size = 0
        while True:
            chunk = r.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
            total_size += len(chunk)
            if total_size > MAX_PDF_SIZE:
                raise ValueError(f"PDF file exceeds maximum size of {MAX_PDF_SIZE} bytes")
        
        return b"".join(chunks)

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

def snippet(text: str, max_len: int = MAX_SNIPPET_LENGTH) -> str:
    t = clean_text(text)
    return t[:max_len] + ("…" if len(t) > max_len else "")

if __name__ == "__main__":
    if not MANIFEST.exists():
        print(f"Missing {MANIFEST}. Create cases/manifest.json first.", file=sys.stderr)
        sys.exit(1)

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
            text, pages_with_text = extract_text_from_pdf(pdf)
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
            # Full text is intentionally omitted from the index to keep JSON size manageable.
        })

    INDEX_OUT.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {INDEX_OUT} ({len(index)} records)")
