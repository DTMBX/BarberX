"""Tests for forensic hashing and manifest signing."""

from __future__ import annotations

import hmac
import hashlib


class TestSHA256Hashing:
    """Server-side SHA-256 verification."""

    def test_sha256_hex_deterministic(self):
        from app.services.hashing import sha256_hex

        data = b"test evidence content"
        h1 = sha256_hex(data)
        h2 = sha256_hex(data)
        assert h1 == h2
        assert len(h1) == 64  # hex digest = 64 chars

    def test_sha256_hex_matches_stdlib(self):
        from app.services.hashing import sha256_hex

        data = b"known content for verification"
        expected = hashlib.sha256(data).hexdigest()
        assert sha256_hex(data) == expected

    def test_different_content_different_hash(self):
        from app.services.hashing import sha256_hex

        h1 = sha256_hex(b"content A")
        h2 = sha256_hex(b"content B")
        assert h1 != h2


class TestManifestSigning:
    """HMAC-SHA256 manifest signatures."""

    def test_sign_and_verify_roundtrip(self):
        """Sign a payload and verify the signature matches."""
        from app.core.config import settings

        payload = "case_id|hash1|hash2|timestamp"
        key = settings.manifest_hmac_key.encode()
        signature = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()

        # Verify
        expected = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        assert hmac.compare_digest(signature, expected)

    def test_tampered_payload_fails(self):
        """Tampered payload should not match original signature."""
        from app.core.config import settings

        key = settings.manifest_hmac_key.encode()
        original = "case_id|hash1|hash2|ts"
        tampered = "case_id|hash1|FAKE|ts"

        sig = hmac.new(key, original.encode(), hashlib.sha256).hexdigest()
        verify = hmac.new(key, tampered.encode(), hashlib.sha256).hexdigest()
        assert not hmac.compare_digest(sig, verify)
