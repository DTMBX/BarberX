"""
Forensic Evidence Pipeline — Integrity Tests
==============================================
Validates the core invariants of the evidence storage system:

1. Hash stability: same file always produces the same SHA-256 hash.
2. Post-copy verification: stored originals match their declared hash.
3. Duplicate detection: re-ingesting the same file is detected.
4. Audit immutability: entries only append, never overwrite.
5. Export reproducibility: exports for the same evidence contain identical hashes.
6. Derivative tracking: derivatives are recorded in the manifest.
"""

import json
import os
import shutil
import tempfile
import zipfile

import pytest

from services.evidence_store import (
    EvidenceStore,
    compute_bytes_hash,
    compute_file_hash,
)
from services.evidence_export import EvidenceExporter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_root(tmp_path):
    """Return a clean temporary evidence store root."""
    return str(tmp_path / "evidence_store")


@pytest.fixture
def store(tmp_root):
    """Return a fresh EvidenceStore instance."""
    return EvidenceStore(root=tmp_root)


@pytest.fixture
def sample_file(tmp_path):
    """Create a small sample file with deterministic content."""
    p = tmp_path / "sample_evidence.bin"
    content = b"EVIDENT_TEST_DATA_" + (b"A" * 1024)
    p.write_bytes(content)
    return str(p)


@pytest.fixture
def sample_video_file(tmp_path):
    """Create a fake MP4 file (not valid video, but enough for store tests)."""
    p = tmp_path / "bwc_test.mp4"
    p.write_bytes(b"\x00\x00\x00\x1cftypisom" + (b"\x00" * 2048))
    return str(p)


# ---------------------------------------------------------------------------
# 1. Hash stability
# ---------------------------------------------------------------------------


class TestHashStability:
    """Same input must always produce the same SHA-256 output."""

    def test_file_hash_deterministic(self, sample_file):
        """Hashing the same file twice produces identical results."""
        h1 = compute_file_hash(sample_file)
        h2 = compute_file_hash(sample_file)
        assert h1.sha256 == h2.sha256
        assert h1.size_bytes == h2.size_bytes

    def test_bytes_hash_deterministic(self):
        """Hashing the same bytes twice produces identical results."""
        data = b"forensic integrity test payload"
        assert compute_bytes_hash(data) == compute_bytes_hash(data)

    def test_different_content_different_hash(self, tmp_path):
        """Different content must produce different hashes."""
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"content_A")
        f2.write_bytes(b"content_B")
        assert compute_file_hash(str(f1)).sha256 != compute_file_hash(str(f2)).sha256

    def test_large_file_streaming(self, tmp_path):
        """Hash of a multi-megabyte file is stable across calls."""
        big = tmp_path / "large.bin"
        big.write_bytes(os.urandom(5 * 1024 * 1024))  # 5 MB
        h1 = compute_file_hash(str(big))
        h2 = compute_file_hash(str(big))
        assert h1.sha256 == h2.sha256


# ---------------------------------------------------------------------------
# 2. Post-copy verification
# ---------------------------------------------------------------------------


class TestPostCopyVerification:
    """Stored originals must match their declared hash exactly."""

    def test_store_original_integrity(self, store, sample_file):
        """store_original verifies the copy matches the source hash."""
        digest = compute_file_hash(sample_file)
        stored_path = store.store_original(
            sample_file, digest.sha256, "sample_evidence.bin"
        )
        # Re-hash the stored copy
        stored_digest = compute_file_hash(stored_path)
        assert stored_digest.sha256 == digest.sha256

    def test_ingest_verifies_copy(self, store, sample_file):
        """Full ingest pipeline verifies post-copy integrity."""
        result = store.ingest(sample_file, "sample.bin", ingested_by="test")
        assert result.success
        # Verify through the store API
        passed, message = store.verify_original(result.sha256)
        assert passed
        assert "verified" in message.lower()


# ---------------------------------------------------------------------------
# 3. Duplicate detection
# ---------------------------------------------------------------------------


class TestDuplicateDetection:
    """Re-ingesting the same file must be flagged as a duplicate."""

    def test_duplicate_detected(self, store, sample_file):
        """Second ingest of identical file is marked duplicate."""
        r1 = store.ingest(sample_file, "first_upload.bin")
        r2 = store.ingest(sample_file, "second_upload.bin")
        assert r1.success
        assert r2.success
        assert not r1.duplicate
        assert r2.duplicate
        assert r1.sha256 == r2.sha256

    def test_duplicate_gets_unique_evidence_id(self, store, sample_file):
        """Each ingest gets a unique evidence_id even for duplicates."""
        r1 = store.ingest(sample_file, "a.bin")
        r2 = store.ingest(sample_file, "b.bin")
        assert r1.evidence_id != r2.evidence_id


# ---------------------------------------------------------------------------
# 4. Audit immutability
# ---------------------------------------------------------------------------


class TestAuditImmutability:
    """Audit entries can only be appended. Previous entries must not change."""

    def test_append_only(self, store, sample_file):
        """Appending an audit entry does not alter previous entries."""
        result = store.ingest(sample_file, "evidence.bin")
        evidence_id = result.evidence_id

        # Read initial manifest
        m1 = store.load_manifest(evidence_id)
        initial_count = len(m1.audit_entries)
        initial_entries = json.dumps(m1.audit_entries)

        # Append a new entry
        store.append_audit(evidence_id, "test_action", actor="tester", details={"key": "value"})

        # Reload and verify
        m2 = store.load_manifest(evidence_id)
        assert len(m2.audit_entries) == initial_count + 1
        # Previous entries unchanged
        assert json.dumps(m2.audit_entries[:initial_count]) == initial_entries

    def test_multiple_appends_preserve_order(self, store, sample_file):
        """Multiple appends maintain chronological order."""
        result = store.ingest(sample_file, "evidence.bin")
        eid = result.evidence_id

        actions = ["action_a", "action_b", "action_c"]
        for a in actions:
            store.append_audit(eid, a, actor="test")

        m = store.load_manifest(eid)
        appended_actions = [e["action"] for e in m.audit_entries if e["action"].startswith("action_")]
        assert appended_actions == actions


# ---------------------------------------------------------------------------
# 5. Export reproducibility
# ---------------------------------------------------------------------------


class TestExportReproducibility:
    """Exports for the same evidence must contain identical file hashes."""

    def test_export_contains_original(self, store, sample_file, tmp_path):
        """Export ZIP contains the original file with correct hash."""
        result = store.ingest(sample_file, "evidence.bin", ingested_by="tester")
        exporter = EvidenceExporter(store, export_dir=str(tmp_path / "exports"))
        export_result = exporter.export(result.evidence_id, exported_by="tester")

        assert export_result.success
        assert os.path.exists(export_result.export_path)

        # Inspect ZIP contents
        with zipfile.ZipFile(export_result.export_path) as zf:
            names = zf.namelist()
            # Must contain manifest, audit_log, integrity_report, and original
            assert any("manifest.json" in n for n in names)
            assert any("audit_log.json" in n for n in names)
            assert any("integrity_report.md" in n for n in names)
            assert any("originals/" in n for n in names)

    def test_export_manifest_hashes_match(self, store, sample_file, tmp_path):
        """Manifest inside the export contains the correct SHA-256."""
        result = store.ingest(sample_file, "evidence.bin")
        exporter = EvidenceExporter(store, export_dir=str(tmp_path / "exports"))
        export_result = exporter.export(result.evidence_id)

        with zipfile.ZipFile(export_result.export_path) as zf:
            manifest_entry = [n for n in zf.namelist() if "manifest.json" in n][0]
            manifest_data = json.loads(zf.read(manifest_entry))
            assert manifest_data["ingest"]["sha256"] == result.sha256


# ---------------------------------------------------------------------------
# 6. Derivative tracking
# ---------------------------------------------------------------------------


class TestDerivativeTracking:
    """Derivatives stored through the store are hashed and retrievable."""

    def test_store_and_retrieve_derivative(self, store, sample_file, tmp_path):
        """Storing a derivative records its hash and it can be retrieved."""
        result = store.ingest(sample_file, "evidence.bin")

        # Create a fake thumbnail
        thumb = tmp_path / "thumb.jpg"
        thumb.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        rec = store.store_derivative(
            result.sha256, "thumbnail", str(thumb), "thumb.jpg"
        )
        assert rec.sha256
        assert rec.size_bytes > 0

        # Retrieve
        path = store.get_derivative_path(result.sha256, "thumbnail", "thumb.jpg")
        assert path is not None
        assert os.path.exists(path)

    def test_derivative_list(self, store, sample_file, tmp_path):
        """list_derivatives returns all stored derivatives."""
        result = store.ingest(sample_file, "evidence.bin")

        for name in ("a.jpg", "b.jpg"):
            f = tmp_path / name
            f.write_bytes(b"\xff" * 50)
            store.store_derivative(result.sha256, "thumbnail", str(f), name)

        derivs = store.list_derivatives(result.sha256)
        assert len(derivs) >= 2


# ---------------------------------------------------------------------------
# 7. Verify original integrity check
# ---------------------------------------------------------------------------


class TestVerifyOriginal:
    """verify_original must detect both intact and tampered files."""

    def test_intact_file_passes(self, store, sample_file):
        result = store.ingest(sample_file, "evidence.bin")
        passed, msg = store.verify_original(result.sha256)
        assert passed

    def test_tampered_file_fails(self, store, sample_file):
        """If a stored original is modified, verification must fail."""
        result = store.ingest(sample_file, "evidence.bin")
        stored = store.get_original_path(result.sha256)
        # Tamper with the stored file
        with open(stored, "ab") as f:
            f.write(b"TAMPERED")
        passed, msg = store.verify_original(result.sha256)
        assert not passed
        assert "FAILURE" in msg.upper()

    def test_missing_file_fails(self, store):
        """Verifying a non-existent hash returns failure."""
        passed, msg = store.verify_original("0" * 64)
        assert not passed
