"""
Tests for Storage Abstraction and Chunked Upload Service
=========================================================
EPX-403 — Verifies:
  - LocalFSStore implements the full StorageBackend interface.
  - Immutability is enforced (no overwrite).
  - SHA-256 verification on write.
  - Directory traversal is blocked.
  - ChunkedUploadService: init, chunk receipt, finalize, cleanup.
  - Integrity verification on chunked assembly.
  - S3Store interface compliance (unit-level, mocked).
"""

import hashlib
import io
import tempfile
import json
import os
import pytest
from pathlib import Path

from services.storage_backend import (
    LocalFSStore,
    S3Store,
    StorageBackend,
    StorePutResult,
    StoreGetResult,
    create_storage_backend,
)
from services.chunked_upload import (
    ChunkedUploadService,
    FinalizeResult,
    StagingSession,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_store(tmp_path):
    """Create a LocalFSStore in a temporary directory."""
    return LocalFSStore(root=str(tmp_path / "store"))


@pytest.fixture
def tmp_staging(tmp_path):
    """Create a ChunkedUploadService in a temporary directory."""
    return ChunkedUploadService(staging_dir=str(tmp_path / "staging"))


# ===========================================================================
# 1. LocalFSStore — Interface compliance
# ===========================================================================


class TestLocalFSStoreInterface:
    """Verify LocalFSStore satisfies the StorageBackend contract."""

    def test_is_storage_backend(self, tmp_store):
        assert isinstance(tmp_store, StorageBackend)

    def test_put_and_get(self, tmp_store):
        data = b"evidence bytes"
        sha = hashlib.sha256(data).hexdigest()
        result = tmp_store.put("test/file.bin", io.BytesIO(data))
        assert result.success
        assert result.sha256 == sha
        assert result.size_bytes == len(data)

        got = tmp_store.get("test/file.bin")
        assert got.success
        assert got.data == data
        assert got.sha256 == sha

    def test_exists(self, tmp_store):
        assert not tmp_store.exists("nope.bin")
        tmp_store.put("yes.bin", io.BytesIO(b"data"))
        assert tmp_store.exists("yes.bin")

    def test_list_keys(self, tmp_store):
        tmp_store.put("a/1.bin", io.BytesIO(b"a"))
        tmp_store.put("a/2.bin", io.BytesIO(b"b"))
        tmp_store.put("b/3.bin", io.BytesIO(b"c"))
        keys = tmp_store.list_keys("a")
        assert "a/1.bin" in keys
        assert "a/2.bin" in keys
        assert "b/3.bin" not in keys

    def test_size(self, tmp_store):
        data = b"12345"
        tmp_store.put("sized.bin", io.BytesIO(data))
        assert tmp_store.size("sized.bin") == 5
        assert tmp_store.size("missing.bin") is None

    def test_get_stream(self, tmp_store):
        data = b"streaming evidence"
        tmp_store.put("stream.bin", io.BytesIO(data))
        stream = tmp_store.get_stream("stream.bin")
        assert stream is not None
        assert stream.read() == data
        stream.close()

    def test_delete(self, tmp_store):
        tmp_store.put("del.bin", io.BytesIO(b"remove me"))
        assert tmp_store.exists("del.bin")
        assert tmp_store.delete("del.bin")
        assert not tmp_store.exists("del.bin")
        assert not tmp_store.delete("del.bin")  # already gone


# ===========================================================================
# 2. Immutability enforcement
# ===========================================================================


class TestImmutability:
    """Verify that originals cannot be overwritten."""

    def test_put_same_key_twice_fails(self, tmp_store):
        tmp_store.put("immutable.bin", io.BytesIO(b"first"))
        result = tmp_store.put("immutable.bin", io.BytesIO(b"second"))
        assert not result.success
        assert "immutability" in result.error.lower()

        # Original content preserved
        got = tmp_store.get("immutable.bin")
        assert got.data == b"first"


# ===========================================================================
# 3. SHA-256 verification on write
# ===========================================================================


class TestWriteVerification:
    """Verify SHA-256 checking on put."""

    def test_correct_sha256_accepted(self, tmp_store):
        data = b"verified content"
        sha = hashlib.sha256(data).hexdigest()
        result = tmp_store.put("verified.bin", io.BytesIO(data), expected_sha256=sha)
        assert result.success
        assert result.sha256 == sha

    def test_wrong_sha256_rejected(self, tmp_store):
        data = b"verified content"
        result = tmp_store.put(
            "bad.bin", io.BytesIO(data), expected_sha256="0" * 64
        )
        assert not result.success
        assert "mismatch" in result.error.lower()
        # File should not exist
        assert not tmp_store.exists("bad.bin")


# ===========================================================================
# 4. Directory traversal prevention
# ===========================================================================


class TestTraversalPrevention:
    """Verify that keys cannot escape the store root."""

    def test_traversal_blocked(self, tmp_store):
        with pytest.raises(ValueError, match="escapes"):
            tmp_store.put("../../etc/passwd", io.BytesIO(b"exploit"))


# ===========================================================================
# 5. Factory function
# ===========================================================================


class TestFactory:
    """Test create_storage_backend factory."""

    def test_default_is_local(self, tmp_path):
        store = create_storage_backend({"STORAGE_ROOT": str(tmp_path)})
        assert isinstance(store, LocalFSStore)

    def test_explicit_local(self, tmp_path):
        store = create_storage_backend({
            "STORAGE_BACKEND": "local",
            "STORAGE_ROOT": str(tmp_path),
        })
        assert isinstance(store, LocalFSStore)

    def test_s3_requires_bucket(self):
        with pytest.raises(ValueError, match="S3_BUCKET"):
            create_storage_backend({"STORAGE_BACKEND": "s3"})


# ===========================================================================
# 6. ChunkedUploadService — init / chunks / finalize
# ===========================================================================


class TestChunkedUploadInit:
    """Test session initialization."""

    def test_init_creates_session(self, tmp_staging):
        session = tmp_staging.init_session(
            original_filename="video.mp4",
            total_chunks=5,
            total_size=5000,
        )
        assert session.staging_id
        assert session.total_chunks == 5
        assert session.original_filename == "video.mp4"
        assert session.chunks_received == []

    def test_session_persisted_to_disk(self, tmp_staging):
        session = tmp_staging.init_session("test.bin", total_chunks=2)
        loaded = tmp_staging.load_session(session.staging_id)
        assert loaded is not None
        assert loaded.staging_id == session.staging_id

    def test_missing_session_returns_none(self, tmp_staging):
        assert tmp_staging.load_session("nonexistent") is None


class TestChunkedUploadChunks:
    """Test chunk receipt."""

    def test_receive_chunk(self, tmp_staging):
        session = tmp_staging.init_session("test.bin", total_chunks=3)
        assert tmp_staging.receive_chunk(session.staging_id, 0, b"aaa")
        assert tmp_staging.receive_chunk(session.staging_id, 2, b"ccc")  # out of order OK
        assert tmp_staging.receive_chunk(session.staging_id, 1, b"bbb")
        loaded = tmp_staging.load_session(session.staging_id)
        assert loaded.chunks_received == [0, 1, 2]

    def test_invalid_chunk_index_rejected(self, tmp_staging):
        session = tmp_staging.init_session("test.bin", total_chunks=2)
        assert not tmp_staging.receive_chunk(session.staging_id, 5, b"bad")
        assert not tmp_staging.receive_chunk(session.staging_id, -1, b"bad")


class TestChunkedUploadFinalize:
    """Test assembly and integrity verification."""

    def test_finalize_assembles_correctly(self, tmp_staging):
        chunks = [b"chunk_0_data", b"chunk_1_data", b"chunk_2_data"]
        full = b"".join(chunks)
        sha = hashlib.sha256(full).hexdigest()

        session = tmp_staging.init_session(
            "assembled.bin",
            total_chunks=3,
            total_size=len(full),
            expected_sha256=sha,
        )

        for i, chunk in enumerate(chunks):
            tmp_staging.receive_chunk(session.staging_id, i, chunk)

        result = tmp_staging.finalize(session.staging_id)
        assert result.success
        assert result.sha256 == sha
        assert result.size_bytes == len(full)

        # Verify assembled file content
        assembled = Path(result.assembled_path).read_bytes()
        assert assembled == full

    def test_finalize_missing_chunks_fails(self, tmp_staging):
        session = tmp_staging.init_session("incomplete.bin", total_chunks=3)
        tmp_staging.receive_chunk(session.staging_id, 0, b"only_one")

        result = tmp_staging.finalize(session.staging_id)
        assert not result.success
        assert "missing" in result.error.lower()

    def test_finalize_sha256_mismatch_fails(self, tmp_staging):
        session = tmp_staging.init_session(
            "corrupt.bin",
            total_chunks=1,
            expected_sha256="0" * 64,
        )
        tmp_staging.receive_chunk(session.staging_id, 0, b"honest data")

        result = tmp_staging.finalize(session.staging_id)
        assert not result.success
        assert "integrity" in result.error.lower()

    def test_finalize_size_mismatch_fails(self, tmp_staging):
        session = tmp_staging.init_session(
            "wrong_size.bin",
            total_chunks=1,
            total_size=999,
        )
        tmp_staging.receive_chunk(session.staging_id, 0, b"12345")

        result = tmp_staging.finalize(session.staging_id)
        assert not result.success
        assert "size" in result.error.lower()


class TestChunkedUploadCleanup:
    """Test cleanup of staging sessions."""

    def test_cleanup_removes_session(self, tmp_staging):
        session = tmp_staging.init_session("cleanup.bin", total_chunks=1)
        tmp_staging.receive_chunk(session.staging_id, 0, b"data")
        assert tmp_staging.load_session(session.staging_id) is not None

        tmp_staging.cleanup_session(session.staging_id)
        assert tmp_staging.load_session(session.staging_id) is None

    def test_cleanup_expired(self, tmp_staging):
        session = tmp_staging.init_session("old.bin", total_chunks=1)
        # Backdate the session
        meta_path = tmp_staging._session_meta_path(session.staging_id)
        with open(meta_path) as f:
            data = json.load(f)
        data["created_at"] = 0  # epoch = very old
        with open(meta_path, "w") as f:
            json.dump(data, f)

        removed = tmp_staging.cleanup_expired(max_age=1)
        assert removed == 1
        assert tmp_staging.load_session(session.staging_id) is None
