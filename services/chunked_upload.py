"""
Chunked Upload Service
=======================
Server-side staging for large file uploads (BWC video, multi-GB evidence).

Flow:
  1. Client POSTs to /upload/chunked/init → gets a staging_id.
  2. Client sends chunks via PUT /upload/chunked/<staging_id>/<chunk_index>.
  3. Client POSTs to /upload/chunked/<staging_id>/finalize → assembles + ingests.

Design principles:
  - Each chunk is hashed independently; final assembly verifies full-file hash.
  - Staging area is cleaned up on success or timeout.
  - No full file held in memory at any point.
  - Resumable: client can re-send a chunk without restarting.
"""

import hashlib
import json
import logging
import os
import shutil
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_STAGING_DIR = "uploads/staging"
CHUNK_SIZE_MAX = 10 * 1024 * 1024   # 10 MiB per chunk
STAGING_TIMEOUT = 3600 * 4           # 4 hours before cleanup


@dataclass
class StagingSession:
    """Metadata for an in-progress chunked upload."""

    staging_id: str
    original_filename: str
    total_chunks: int
    total_size: int               # expected total bytes (0 = unknown)
    expected_sha256: str          # expected final hash ("" = verify on finalize)
    created_at: float             # Unix timestamp
    chunks_received: list         # list of chunk indices received
    uploader_id: Optional[int] = None
    device_label: Optional[str] = None


@dataclass(frozen=True)
class FinalizeResult:
    """Result of finalizing a chunked upload."""

    success: bool
    staging_id: str
    assembled_path: str
    sha256: str
    size_bytes: int
    error: Optional[str] = None


class ChunkedUploadService:
    """
    Manages chunked upload staging, assembly, and cleanup.
    """

    def __init__(self, staging_dir: str = DEFAULT_STAGING_DIR):
        self.staging_dir = Path(staging_dir).resolve()
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, staging_id: str) -> Path:
        return self.staging_dir / staging_id

    def _session_meta_path(self, staging_id: str) -> Path:
        return self._session_dir(staging_id) / "session.json"

    def _chunk_path(self, staging_id: str, chunk_index: int) -> Path:
        return self._session_dir(staging_id) / f"chunk_{chunk_index:06d}"

    # -- session management --------------------------------------------------

    def init_session(
        self,
        original_filename: str,
        total_chunks: int,
        total_size: int = 0,
        expected_sha256: str = "",
        uploader_id: Optional[int] = None,
        device_label: Optional[str] = None,
    ) -> StagingSession:
        """Create a new staging session and return its metadata."""
        staging_id = uuid.uuid4().hex
        session = StagingSession(
            staging_id=staging_id,
            original_filename=original_filename,
            total_chunks=total_chunks,
            total_size=total_size,
            expected_sha256=expected_sha256,
            created_at=time.time(),
            chunks_received=[],
            uploader_id=uploader_id,
            device_label=device_label,
        )

        session_dir = self._session_dir(staging_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        self._save_session(session)

        logger.info(
            "Chunked upload session created: %s (%s, %d chunks)",
            staging_id,
            original_filename,
            total_chunks,
        )
        return session

    def _save_session(self, session: StagingSession) -> None:
        path = self._session_meta_path(session.staging_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(session), f, indent=2)

    def load_session(self, staging_id: str) -> Optional[StagingSession]:
        """Load session metadata, or None if expired/missing."""
        path = self._session_meta_path(staging_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StagingSession(**data)

    # -- chunk handling ------------------------------------------------------

    def receive_chunk(
        self,
        staging_id: str,
        chunk_index: int,
        data: bytes,
    ) -> bool:
        """
        Store a chunk. Returns True on success.

        Chunks can be re-sent (idempotent overwrite). The client is responsible
        for sending chunks in any order.
        """
        session = self.load_session(staging_id)
        if session is None:
            logger.error("Chunk upload: session not found %s", staging_id)
            return False

        if chunk_index < 0 or chunk_index >= session.total_chunks:
            logger.error(
                "Chunk index %d out of range [0, %d) for %s",
                chunk_index, session.total_chunks, staging_id,
            )
            return False

        # Enforce max chunk size
        if len(data) > CHUNK_SIZE_MAX:
            logger.error(
                "Chunk %d exceeds max size (%d > %d) for %s",
                chunk_index, len(data), CHUNK_SIZE_MAX, staging_id,
            )
            return False

        chunk_path = self._chunk_path(staging_id, chunk_index)
        chunk_path.write_bytes(data)

        if chunk_index not in session.chunks_received:
            session.chunks_received.append(chunk_index)
            session.chunks_received.sort()
            self._save_session(session)

        logger.debug(
            "Chunk %d/%d received for %s (%d bytes)",
            chunk_index + 1, session.total_chunks, staging_id, len(data),
        )
        return True

    # -- finalization --------------------------------------------------------

    def finalize(self, staging_id: str) -> FinalizeResult:
        """
        Assemble all chunks into a single file, verify integrity, and return.

        The assembled file is written to the staging directory as
        ``<staging_id>_assembled_<filename>``.
        """
        session = self.load_session(staging_id)
        if session is None:
            return FinalizeResult(
                success=False,
                staging_id=staging_id,
                assembled_path="",
                sha256="",
                size_bytes=0,
                error="Session not found or expired",
            )

        # Check all chunks are present
        expected = set(range(session.total_chunks))
        received = set(session.chunks_received)
        missing = expected - received
        if missing:
            return FinalizeResult(
                success=False,
                staging_id=staging_id,
                assembled_path="",
                sha256="",
                size_bytes=0,
                error=f"Missing chunks: {sorted(missing)}",
            )

        # Assemble
        assembled_path = self._session_dir(staging_id) / session.original_filename
        h = hashlib.sha256()
        size = 0

        try:
            with open(assembled_path, "wb") as out:
                for i in range(session.total_chunks):
                    chunk_data = self._chunk_path(staging_id, i).read_bytes()
                    h.update(chunk_data)
                    out.write(chunk_data)
                    size += len(chunk_data)
        except Exception as exc:
            return FinalizeResult(
                success=False,
                staging_id=staging_id,
                assembled_path="",
                sha256="",
                size_bytes=0,
                error=f"Assembly failed: {exc}",
            )

        actual_sha256 = h.hexdigest()

        # Verify expected hash if provided
        if session.expected_sha256 and actual_sha256 != session.expected_sha256:
            assembled_path.unlink(missing_ok=True)
            return FinalizeResult(
                success=False,
                staging_id=staging_id,
                assembled_path="",
                sha256=actual_sha256,
                size_bytes=size,
                error=(
                    f"Integrity check failed: expected {session.expected_sha256}, "
                    f"got {actual_sha256}"
                ),
            )

        # Verify total size if provided
        if session.total_size and size != session.total_size:
            assembled_path.unlink(missing_ok=True)
            return FinalizeResult(
                success=False,
                staging_id=staging_id,
                assembled_path="",
                sha256=actual_sha256,
                size_bytes=size,
                error=(
                    f"Size mismatch: expected {session.total_size}, got {size}"
                ),
            )

        logger.info(
            "Chunked upload finalized: %s (%s, %d bytes, sha256=%s)",
            staging_id,
            session.original_filename,
            size,
            actual_sha256[:16],
        )

        return FinalizeResult(
            success=True,
            staging_id=staging_id,
            assembled_path=str(assembled_path),
            sha256=actual_sha256,
            size_bytes=size,
        )

    # -- cleanup -------------------------------------------------------------

    def cleanup_session(self, staging_id: str) -> bool:
        """Remove all staging data for a session."""
        session_dir = self._session_dir(staging_id)
        if session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info("Cleaned up staging session: %s", staging_id)
            return True
        return False

    def cleanup_expired(self, max_age: float = STAGING_TIMEOUT) -> int:
        """Remove all sessions older than max_age seconds. Returns count."""
        now = time.time()
        removed = 0
        if not self.staging_dir.exists():
            return 0
        for entry in self.staging_dir.iterdir():
            if entry.is_dir():
                meta = entry / "session.json"
                if meta.exists():
                    try:
                        with open(meta) as f:
                            data = json.load(f)
                        if now - data.get("created_at", 0) > max_age:
                            shutil.rmtree(entry, ignore_errors=True)
                            removed += 1
                    except Exception:
                        pass
        if removed:
            logger.info("Cleaned up %d expired staging sessions.", removed)
        return removed
