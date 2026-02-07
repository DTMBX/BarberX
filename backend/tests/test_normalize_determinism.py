import hashlib

from backend.tools.law.normalize import canonicalize_bytes


def test_normalize_determinism():
    raw = b"Hello <b>World</b>\r\n\r\n  Extra   spaces"
    a_bytes, a_text = canonicalize_bytes(raw, content_type="text/html")
    b_bytes, b_text = canonicalize_bytes(raw, content_type="text/html")
    assert a_bytes == b_bytes
    assert hashlib.sha256(a_bytes).hexdigest() == hashlib.sha256(b_bytes).hexdigest()
