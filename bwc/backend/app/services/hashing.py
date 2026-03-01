"""SHA-256 hashing utility for evidence files."""

from __future__ import annotations

import hashlib
import hmac


def sha256_hex(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_hex_str(text: str) -> str:
    """Return the lowercase hex SHA-256 digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hmac_sha256(key: str, message: str) -> str:
    """Return HMAC-SHA256 hex digest of *message* using *key*."""
    return hmac.new(
        key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_hmac_sha256(key: str, message: str, signature: str) -> bool:
    """Constant-time HMAC-SHA256 verification."""
    expected = hmac.new(
        key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
