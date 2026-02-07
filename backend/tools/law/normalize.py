from __future__ import annotations
from typing import Optional

import re
from html.parser import HTMLParser


class _TextStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return "".join(self.parts)


Optional[def canonicalize_bytes(raw: bytes, content_type: str] = None) -> tuple[bytes, str]:
    """Return (canonical_bytes, canonical_text).

    Deterministic rules: normalize newlines to LF, collapse spaces, strip leading/trailing whitespace per line,
    and ensure UTF-8 encoding.
    If HTML-like, strip tags deterministically using HTMLParser.
    """
    try:
        text = raw.decode("utf-8")
    except Exception:
        # binary or unknown; return raw as canonical bytes and empty text
        return raw, ""

    is_html = False
    if content_type and "html" in content_type.lower():
        is_html = True
    if "<html" in text.lower() or "<body" in text.lower() or "<div" in text.lower():
        is_html = True

    if is_html:
        p = _TextStripper()
        p.feed(text)
        canon_text = p.get_text()
    else:
        canon_text = text

    # normalize whitespace deterministically
    # convert CRLF -> LF
    canon_text = canon_text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse multiple spaces
    canon_text = re.sub(r"[ \t]+", " ", canon_text)
    # strip each line
    lines = [ln.strip() for ln in canon_text.split("\n")]
    # remove extraneous empty lines at start/end
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    canon_text = "\n".join(lines)

    canonical_bytes = canon_text.encode("utf-8")
    return canonical_bytes, canon_text