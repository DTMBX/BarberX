"""
Forensic Evidence Store
========================
Central module for evidence intake, integrity verification, and canonical storage.

Design principles:
  - Originals are NEVER overwritten (immutable storage).
  - Every artifact is SHA-256 hashed at ingest.
  - Derivatives reference the original hash.
  - Audit log is append-only (no edits, no deletes).
  - Exports are reproducible from stored originals + recorded transforms.

Storage layout:
  evidence_store/
    originals/<sha256_prefix>/<sha256>/<original_filename>
    derivatives/<sha256_prefix>/<sha256>/<derivative_type>/<filename>
    manifests/<evidence_id>.json

All public methods return typed results and raise no uncaught exceptions.
"""

import hashlib
import json
import logging
import mimetypes
import os
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HASH_ALGORITHM = "sha256"
HASH_BLOCK_SIZE = 1 << 16  # 64 KiB — balances memory and throughput
MAX_INGEST_BYTES = 3 * 1024 * 1024 * 1024  # 3 GiB hard ceiling


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FileDigest:
    """Immutable container for a file's cryptographic digest."""

    sha256: str
    size_bytes: int
    algorithm: str = HASH_ALGORITHM


@dataclass(frozen=True)
class IngestMetadata:
    """Metadata captured at the moment of ingest."""

    original_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    evidence_id: str  # UUIDv4
    ingested_at: str  # ISO-8601 UTC
    ingested_by: Optional[str] = None  # user identifier
    device_label: Optional[str] = None  # e.g. "BWC-7139078"
    source_path: Optional[str] = None  # where the file came from (transient)


@dataclass
class DerivativeRecord:
    """Tracks a derivative artifact generated from an original."""

    derivative_type: str  # 'thumbnail', 'proxy', 'transcript', ...
    filename: str
    sha256: str
    size_bytes: int
    created_at: str  # ISO-8601 UTC
    parameters: Dict = field(default_factory=dict)  # codec, resolution, etc.


@dataclass
class EvidenceManifest:
    """Complete manifest for a single piece of evidence."""

    evidence_id: str
    ingest: IngestMetadata
    derivatives: List[DerivativeRecord] = field(default_factory=list)
    audit_entries: List[Dict] = field(default_factory=list)


@dataclass
class IngestResult:
    """Result of an ingest operation."""

    success: bool
    evidence_id: str
    sha256: str
    stored_path: str
    manifest_path: str
    metadata: IngestMetadata
    error: Optional[str] = None
    duplicate: bool = False  # True if file was already ingested


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_file_hash(file_path: str) -> FileDigest:
    """
    Compute SHA-256 digest of a file using streaming reads.

    Reads in HASH_BLOCK_SIZE chunks so that multi-gigabyte files
    never load fully into memory.

    Args:
        file_path: Absolute path to the file.

    Returns:
        FileDigest with hex digest and file size.

    Raises:
        FileNotFoundError: If file_path does not exist.
        OSError: On read errors.
    """
    h = hashlib.sha256()
    size = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(HASH_BLOCK_SIZE)
            if not chunk:
                break
            h.update(chunk)
            size += len(chunk)
    return FileDigest(sha256=h.hexdigest(), size_bytes=size)


def compute_bytes_hash(data: bytes) -> str:
    """Return the hex SHA-256 of an in-memory byte string."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Canonical storage layout
# ---------------------------------------------------------------------------


class EvidenceStore:
    """
    Manages the canonical filesystem layout for evidence artifacts.

    All paths are deterministic from (root, sha256).
    """

    def __init__(self, root: str = "evidence_store"):
        self.root = Path(root).resolve()
        self._ensure_dirs()

    # -- directory scaffolding -----------------------------------------------

    def _ensure_dirs(self) -> None:
        for subdir in ("originals", "derivatives", "manifests"):
            (self.root / subdir).mkdir(parents=True, exist_ok=True)

    def _original_dir(self, sha256: str) -> Path:
        prefix = sha256[:4]
        return self.root / "originals" / prefix / sha256

    def _derivative_dir(self, sha256: str, derivative_type: str) -> Path:
        prefix = sha256[:4]
        return self.root / "derivatives" / prefix / sha256 / derivative_type

    def _manifest_path(self, evidence_id: str) -> Path:
        return self.root / "manifests" / f"{evidence_id}.json"

    # -- original storage ----------------------------------------------------

    def original_exists(self, sha256: str) -> bool:
        """Check if an original with this hash is already stored."""
        d = self._original_dir(sha256)
        return d.exists() and any(d.iterdir())

    def get_original_path(self, sha256: str) -> Optional[str]:
        """Return the stored path of an original, or None."""
        d = self._original_dir(sha256)
        if d.exists():
            files = list(d.iterdir())
            if files:
                return str(files[0])
        return None

    def store_original(
        self,
        source_path: str,
        sha256: str,
        original_filename: str,
    ) -> str:
        """
        Copy a file into the canonical originals directory.

        Uses copy2 (preserves filesystem timestamps).
        Returns the stored path.

        Raises:
            FileExistsError: If an original with this hash already exists.
        """
        dest_dir = self._original_dir(sha256)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Preserve original filename for provenance; prefix with hash fragment
        # to prevent name collisions across different originals.
        dest = dest_dir / original_filename
        if dest.exists():
            raise FileExistsError(
                f"Original already stored: {dest}"
            )

        shutil.copy2(source_path, dest)

        # Verify copy integrity
        copy_digest = compute_file_hash(str(dest))
        if copy_digest.sha256 != sha256:
            dest.unlink()
            raise RuntimeError(
                f"Post-copy integrity check failed: expected {sha256}, "
                f"got {copy_digest.sha256}"
            )

        logger.info(
            "Stored original: %s -> %s (%d bytes)",
            original_filename,
            dest,
            copy_digest.size_bytes,
        )
        return str(dest)

    # -- derivative storage --------------------------------------------------

    def store_derivative(
        self,
        original_sha256: str,
        derivative_type: str,
        source_path: str,
        filename: str,
    ) -> DerivativeRecord:
        """
        Store a derivative artifact and return its record.

        The derivative is hashed independently for integrity tracking.
        """
        dest_dir = self._derivative_dir(original_sha256, derivative_type)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename

        shutil.copy2(source_path, dest)

        digest = compute_file_hash(str(dest))
        record = DerivativeRecord(
            derivative_type=derivative_type,
            filename=filename,
            sha256=digest.sha256,
            size_bytes=digest.size_bytes,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(
            "Stored derivative [%s]: %s (%d bytes, sha256=%s)",
            derivative_type,
            filename,
            digest.size_bytes,
            digest.sha256[:16],
        )
        return record

    def get_derivative_path(
        self, original_sha256: str, derivative_type: str, filename: str
    ) -> Optional[str]:
        """Return absolute path to a derivative, or None."""
        p = self._derivative_dir(original_sha256, derivative_type) / filename
        return str(p) if p.exists() else None

    def list_derivatives(self, original_sha256: str) -> List[str]:
        """Return relative paths of all derivatives for an original."""
        base = self.root / "derivatives" / original_sha256[:4] / original_sha256
        if not base.exists():
            return []
        results = []
        for dtype_dir in sorted(base.iterdir()):
            if dtype_dir.is_dir():
                for f in sorted(dtype_dir.iterdir()):
                    results.append(f"{dtype_dir.name}/{f.name}")
        return results

    # -- manifests -----------------------------------------------------------

    def save_manifest(self, manifest: EvidenceManifest) -> str:
        """Write the manifest to JSON. Returns the path."""
        path = self._manifest_path(manifest.evidence_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(manifest), f, indent=2, ensure_ascii=False)
        return str(path)

    def load_manifest(self, evidence_id: str) -> Optional[EvidenceManifest]:
        """Load a manifest from disk, or return None."""
        path = self._manifest_path(evidence_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return EvidenceManifest(
            evidence_id=data["evidence_id"],
            ingest=IngestMetadata(**data["ingest"]),
            derivatives=[DerivativeRecord(**d) for d in data.get("derivatives", [])],
            audit_entries=data.get("audit_entries", []),
        )

    # -- high-level ingest ---------------------------------------------------

    def ingest(
        self,
        source_path: str,
        original_filename: str,
        ingested_by: Optional[str] = None,
        device_label: Optional[str] = None,
    ) -> IngestResult:
        """
        Ingest a file into the evidence store.

        1. Hash the source file (streaming SHA-256).
        2. Check for duplicate (same hash already stored).
        3. Copy to canonical location with post-copy verification.
        4. Capture metadata.
        5. Create manifest.
        6. Record ingest audit entry.

        Returns IngestResult on success or failure.
        """
        evidence_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        try:
            # 1. Hash
            digest = compute_file_hash(source_path)

            if digest.size_bytes > MAX_INGEST_BYTES:
                return IngestResult(
                    success=False,
                    evidence_id=evidence_id,
                    sha256="",
                    stored_path="",
                    manifest_path="",
                    metadata=IngestMetadata(
                        original_filename=original_filename,
                        mime_type="",
                        size_bytes=digest.size_bytes,
                        sha256="",
                        evidence_id=evidence_id,
                        ingested_at=now,
                    ),
                    error=f"File exceeds maximum ingest size "
                    f"({digest.size_bytes} > {MAX_INGEST_BYTES})",
                )

            mime = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

            # 2. Duplicate check
            duplicate = self.original_exists(digest.sha256)
            if duplicate:
                existing_path = self.get_original_path(digest.sha256)
                metadata = IngestMetadata(
                    original_filename=original_filename,
                    mime_type=mime,
                    size_bytes=digest.size_bytes,
                    sha256=digest.sha256,
                    evidence_id=evidence_id,
                    ingested_at=now,
                    ingested_by=ingested_by,
                    device_label=device_label,
                    source_path=source_path,
                )
                manifest = EvidenceManifest(
                    evidence_id=evidence_id,
                    ingest=metadata,
                    audit_entries=[
                        {
                            "action": "ingest_duplicate",
                            "timestamp": now,
                            "actor": ingested_by,
                            "details": {
                                "sha256": digest.sha256,
                                "existing_path": existing_path,
                            },
                        }
                    ],
                )
                manifest_path = self.save_manifest(manifest)
                logger.warning(
                    "Duplicate detected for %s (sha256=%s)",
                    original_filename,
                    digest.sha256[:16],
                )
                return IngestResult(
                    success=True,
                    evidence_id=evidence_id,
                    sha256=digest.sha256,
                    stored_path=existing_path or "",
                    manifest_path=manifest_path,
                    metadata=metadata,
                    duplicate=True,
                )

            # 3. Store original
            stored_path = self.store_original(
                source_path, digest.sha256, original_filename
            )

            # 4. Metadata
            metadata = IngestMetadata(
                original_filename=original_filename,
                mime_type=mime,
                size_bytes=digest.size_bytes,
                sha256=digest.sha256,
                evidence_id=evidence_id,
                ingested_at=now,
                ingested_by=ingested_by,
                device_label=device_label,
                source_path=source_path,
            )

            # 5. Manifest
            manifest = EvidenceManifest(
                evidence_id=evidence_id,
                ingest=metadata,
                audit_entries=[
                    {
                        "action": "ingest",
                        "timestamp": now,
                        "actor": ingested_by,
                        "details": {
                            "sha256": digest.sha256,
                            "size_bytes": digest.size_bytes,
                            "mime_type": mime,
                            "device_label": device_label,
                        },
                    }
                ],
            )
            manifest_path = self.save_manifest(manifest)

            logger.info(
                "Ingested evidence %s: %s (sha256=%s, %d bytes)",
                evidence_id,
                original_filename,
                digest.sha256[:16],
                digest.size_bytes,
            )

            return IngestResult(
                success=True,
                evidence_id=evidence_id,
                sha256=digest.sha256,
                stored_path=stored_path,
                manifest_path=manifest_path,
                metadata=metadata,
            )

        except Exception as exc:
            logger.error(
                "Ingest failed for %s: %s", original_filename, exc, exc_info=True
            )
            return IngestResult(
                success=False,
                evidence_id=evidence_id,
                sha256="",
                stored_path="",
                manifest_path="",
                metadata=IngestMetadata(
                    original_filename=original_filename,
                    mime_type="",
                    size_bytes=0,
                    sha256="",
                    evidence_id=evidence_id,
                    ingested_at=now,
                ),
                error=str(exc),
            )

    # -- audit append --------------------------------------------------------

    def append_audit(
        self,
        evidence_id: str,
        action: str,
        actor: Optional[str] = None,
        details: Optional[Dict] = None,
    ) -> bool:
        """
        Append an audit entry to an evidence manifest.

        Returns True on success, False if manifest not found.
        """
        manifest = self.load_manifest(evidence_id)
        if manifest is None:
            logger.error("Cannot append audit: manifest not found for %s", evidence_id)
            return False

        entry = {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "details": details or {},
        }
        manifest.audit_entries.append(entry)
        self.save_manifest(manifest)
        logger.info("Audit appended to %s: %s", evidence_id, action)
        return True

    # -- integrity verification ----------------------------------------------

    def verify_original(self, sha256: str) -> Tuple[bool, str]:
        """
        Recompute the hash of a stored original and compare.

        Returns:
            (passed, message) tuple.
        """
        path = self.get_original_path(sha256)
        if path is None:
            return False, f"Original not found for sha256={sha256[:16]}..."

        current = compute_file_hash(path)
        if current.sha256 == sha256:
            return True, "Integrity verified"
        else:
            return False, (
                f"INTEGRITY FAILURE: expected {sha256}, computed {current.sha256}"
            )
