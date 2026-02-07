from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Manifest Service - Manages document manifests and canonical storage

Responsibilities:
1. Compute SHA-256 hashes
2. Deduplicate by hash
3. Save files to canonical paths: uploads/pdfs/originals/{sha256}.pdf
4. Create/update manifest files: manifest/{sha256}.json
5. Track original → processed artifact chain
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

from ..contracts import IngestResult, ManifestRecord, SourceSystem

logger = logging.getLogger(__name__)


class ManifestService:
    """
    Manages document manifests and canonical file storage

    File layout:
        uploads/pdfs/originals/{sha256}.pdf     - Immutable originals
        uploads/pdfs/processed/{sha256}/        - Derived artifacts
            repaired.pdf                        - qpdf-repaired version
            ocr.pdf                             - OCR'd version
            pages/0001.txt                      - Cached page text
        manifest/{sha256}.json                  - Audit trail
    """

Optional[def __init__(self, config: dict] = None):
        self.config = config or {}

        # Base paths
        self.storage_root = Path(self.config.get("storage_root", "./uploads"))
        self.manifest_root = Path(self.config.get("manifest_root", "./manifest"))

        # Ensure directories exist
        self.originals_dir = self.storage_root / "pdfs" / "originals"
        self.processed_dir = self.storage_root / "pdfs" / "processed"
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_root.mkdir(parents=True, exist_ok=True)

        logger.info(f"ManifestService initialized: storage={self.storage_root}")

    def ingest(
Optional[self, file_path: str, source_system: SourceSystem, metadata: dict] = None
    ) -> IngestResult:
        """
        Ingest file: hash, dedupe, save to canonical location, create manifest

        Args:
            file_path: Absolute path to file to ingest
            source_system: Origin (app, bwc, legal_library)
            metadata: Optional user metadata

        Returns:
            IngestResult with doc_id and paths
        """
        source_path = Path(file_path)

        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if source_path.stat().st_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        # Compute SHA-256
        sha256 = self._compute_hash(source_path)
        logger.info(f"Computed SHA-256: {sha256[:16]}... for {source_path.name}")

        # Check for duplicate
        is_duplicate, existing_doc_id = self._check_duplicate(sha256)

        if is_duplicate:
            logger.info(f"Duplicate detected: {sha256} (doc_id={existing_doc_id})")
            # TODO: Load existing manifest and return
            # For now, return placeholder
            return IngestResult(
                doc_id=existing_doc_id,
                sha256=sha256,
                filename_original=source_path.name,
                storage_path_original=str(self.originals_dir / f"{sha256}.pdf"),
                file_size_bytes=source_path.stat().st_size,
                source_system=source_system,
                metadata=metadata or {},
                is_duplicate=True,
                duplicate_of_doc_id=existing_doc_id,
            )

        # Save to canonical location
        canonical_path = self.originals_dir / f"{sha256}.pdf"
        shutil.copy2(source_path, canonical_path)
        logger.info(f"Saved to canonical path: {canonical_path}")

        # Create manifest
        manifest = ManifestRecord(
            sha256=sha256,
            original={
                "path": str(canonical_path),
                "bytes": source_path.stat().st_size,
                "filename": source_path.name,
                "uploaded_at": datetime.utcnow().isoformat(),
            },
            timestamps={"ingested_at": datetime.utcnow().isoformat()},
            source_system=source_system.value,
        )

        # Save manifest to disk
        self._save_manifest(sha256, manifest)

        # Insert into database
        # TODO: Import and use database models
        doc_id = self._insert_document_record(
            sha256=sha256,
            filename=source_path.name,
            storage_path=str(canonical_path),
            source_system=source_system,
            metadata=metadata or {},
        )

        manifest.doc_id = doc_id
        self._save_manifest(sha256, manifest)  # Update with doc_id

        return IngestResult(
            doc_id=doc_id,
            sha256=sha256,
            filename_original=source_path.name,
            storage_path_original=str(canonical_path),
            file_size_bytes=source_path.stat().st_size,
            source_system=source_system,
            metadata=metadata or {},
            is_duplicate=False,
        )

    def update_manifest(self, sha256: str, updates: dict):
        """
        Update manifest with new processing artifacts

        Args:
            sha256: Document hash
            updates: Dict with keys like "processed", "extraction", "timestamps"
        """
        manifest = self._load_manifest(sha256)

        if manifest is None:
            logger.warning(f"Manifest not found for {sha256}, creating new")
            manifest = ManifestRecord(sha256=sha256)

        # Deep merge updates
        for key, value in updates.items():
            if key == "processed":
                manifest.processed.update(value)
            elif key == "extraction":
                manifest.extraction.update(value)
            elif key == "timestamps":
                manifest.timestamps.update(value)

        self._save_manifest(sha256, manifest)
        logger.info(f"Updated manifest for {sha256}")

Optional[def get_manifest(self, sha256: str) -> ManifestRecord]:
        """Load manifest by SHA-256"""
        return self._load_manifest(sha256)

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _compute_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Compute SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()

Optional[def _check_duplicate(self, sha256: str) -> tuple[bool, int]]:
        """
        Check if document with this hash already exists

        Returns:
            (is_duplicate, existing_doc_id or None)
        """
        # TODO: Query database for existing document with this SHA
        # For now, check if manifest exists
        manifest_path = self.manifest_root / f"{sha256}.json"
        if manifest_path.exists():
            manifest = self._load_manifest(sha256)
            return (True, manifest.doc_id if manifest else None)
        return (False, None)

    def _insert_document_record(
        self,
        sha256: str,
        filename: str,
        storage_path: str,
        source_system: SourceSystem,
        metadata: dict,
    ) -> int:
        """
        Insert document record into database

        Returns:
            doc_id (primary key)
        """
        # TODO: Import database models and insert
        # For now, return mock ID
        logger.warning("Database insertion not yet implemented, returning mock doc_id")
        return hash(sha256) % 1000000  # Mock ID

    def _save_manifest(self, sha256: str, manifest: ManifestRecord):
        """Save manifest to disk as JSON"""
        manifest_path = self.manifest_root / f"{sha256}.json"

        # Convert dataclass to dict
        manifest_dict = {
            "sha256": manifest.sha256,
            "original": manifest.original,
            "processed": manifest.processed,
            "extraction": manifest.extraction,
            "timestamps": manifest.timestamps,
            "source_system": manifest.source_system,
            "doc_id": manifest.doc_id,
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest_dict, f, indent=2)

        logger.debug(f"Saved manifest: {manifest_path}")

Optional[def _load_manifest(self, sha256: str) -> ManifestRecord]:
        """Load manifest from disk"""
        manifest_path = self.manifest_root / f"{sha256}.json"

        if not manifest_path.exists():
            return None

        with open(manifest_path) as f:
            data = json.load(f)

        return ManifestRecord(
            sha256=data["sha256"],
            original=data.get("original", {}),
            processed=data.get("processed", {}),
            extraction=data.get("extraction", {}),
            timestamps=data.get("timestamps", {}),
            source_system=data.get("source_system", "app"),
            doc_id=data.get("doc_id"),
        )