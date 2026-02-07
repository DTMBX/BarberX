from __future__ import annotations

try:
    import eyecite

    _HAS_EYECITE = True
except Exception:
    _HAS_EYECITE = False
    # fallback


def _normalize_cite(text: str) -> str:
    return " ".join(text.split())


def extract_citations(text: str) -> list[dict]:
    """Return list of citations dicts with deterministic ordering.

    Each dict: {cite_text, normalized_cite, start_offset, end_offset, target_hint, pinpoint}
    """
    cites = []
    if _HAS_EYECITE:
        # eyecite API: eyecite.get_citations(text) -> list of Citation objects
        try:
            raw = eyecite.get_citations(text)
            for c in raw:
                s = getattr(c, "span", None)
                start, end = (s.start, s.stop) if s else (None, None)
                quote = getattr(c, "text", str(c))
                normalized = _normalize_cite(quote)
                cites.append(
                    {
                        "cite_text": quote,
                        "normalized_cite": normalized,
                        "start_offset": start,
                        "end_offset": end,
                        "target_hint": None,
                        "pinpoint": None,
                    }
                )
        except Exception:
            pass
    if not _HAS_EYECITE:
        # simple regex fallback for patterns like '123 U.S. 456' or '123 F.3d 456'
        import re

        pattern = re.compile(r"\b\d{1,4}\s+[A-Z][A-Za-z0-9\.]{1,10}\s+\d{1,4}\b")
        for m in pattern.finditer(text):
            quote = m.group(0)
            cites.append(
                {
                    "cite_text": quote,
                    "normalized_cite": _normalize_cite(quote),
                    "start_offset": m.start(),
                    "end_offset": m.end(),
                    "target_hint": None,
                    "pinpoint": None,
                }
            )

    # deterministic ordering: by start_offset then cite_text
    cites.sort(key=lambda c: (c["start_offset"] or 0, c["cite_text"]))
    return cites
