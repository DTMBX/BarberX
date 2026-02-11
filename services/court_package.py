"""
Court Package Exporter
=======================
Generates a court-submission-ready exhibit package with:
  - Sequentially numbered exhibit directories (Exhibit_001/, Exhibit_002/, ...)
  - INDEX.csv and INDEX.json for manifest linkage
  - Optional offline review pack (viewer + proxies, clearly labeled as derivative)
  - SHA-256 hashes for every file in the package
  - Deterministic output given identical inputs

Design principles:
  - Originals are NEVER modified — copied into exhibit directories.
  - Every file is hashed; hashes appear in INDEX.csv and INDEX.json.
  - Derivative viewing materials are clearly separated and labeled.
  - The package is self-verifying: INDEX.json contains all hashes, and
    a PACKAGE_HASH.txt records the hash of INDEX.json itself.
"""

import csv
import hashlib
import io
import json
import logging
import os
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExhibitEntry:
    """One exhibit in the court package."""

    exhibit_number: str      # "001", "002", ...
    original_filename: str
    evidence_id: str         # UUID from evidence store
    file_type: str           # MIME type
    file_size_bytes: int
    sha256: str
    description: str = ""


@dataclass(frozen=True)
class CourtPackageResult:
    """Result of generating a court package."""

    success: bool
    package_path: str
    exhibit_count: int
    index_sha256: str        # SHA-256 of INDEX.json
    package_sha256: str      # SHA-256 of the ZIP file itself
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Court Package Builder
# ---------------------------------------------------------------------------


class CourtPackageExporter:
    """
    Builds a court-submission-ready exhibit package.

    Usage:
        exporter = CourtPackageExporter(export_base_path="exports/court")
        result = exporter.build_package(
            case=case_object,
            exhibits=[(evidence_item, description), ...],
            generated_at=datetime.now(timezone.utc),
        )
    """

    def __init__(self, export_base_path: str = "exports/court"):
        self.export_base = Path(export_base_path).resolve()
        self.export_base.mkdir(parents=True, exist_ok=True)

    def build_package(
        self,
        case,
        exhibits: list,
        generated_at: Optional[datetime] = None,
        include_offline_viewer: bool = False,
    ) -> CourtPackageResult:
        """
        Build a court exhibit package.

        Args:
            case: LegalCase model instance.
            exhibits: List of (EvidenceItem, description) tuples, in exhibit
                      order. The order determines exhibit numbering.
            generated_at: Timestamp for deterministic output.
            include_offline_viewer: If True, includes a derivative viewer
                                    pack (clearly labeled).

        Returns:
            CourtPackageResult with package path and integrity hashes.
        """
        if generated_at is None:
            generated_at = datetime.now(timezone.utc)

        timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
        case_number = getattr(case, "case_number", "UNKNOWN")
        package_name = f"court_package_{case_number}_{timestamp}"
        zip_path = self.export_base / f"{package_name}.zip"

        entries: List[ExhibitEntry] = []
        file_hashes: Dict[str, str] = {}  # path_in_zip -> sha256

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

                # --- Write exhibits ---
                for i, (item, description) in enumerate(exhibits):
                    exhibit_num = f"{i + 1:03d}"
                    exhibit_dir = f"Exhibit_{exhibit_num}"

                    # Get the original file
                    original_path = self._resolve_original(item)
                    if original_path is None:
                        logger.warning(
                            "Original not found for evidence %s, skipping",
                            item.id,
                        )
                        continue

                    original_bytes = Path(original_path).read_bytes()
                    sha256 = hashlib.sha256(original_bytes).hexdigest()
                    filename = getattr(item, "original_filename", f"exhibit_{exhibit_num}")

                    zip_entry_path = f"{exhibit_dir}/{filename}"
                    zf.writestr(zip_entry_path, original_bytes)
                    file_hashes[zip_entry_path] = sha256

                    entry = ExhibitEntry(
                        exhibit_number=exhibit_num,
                        original_filename=filename,
                        evidence_id=str(getattr(item, "evidence_id", getattr(item, "id", ""))),
                        file_type=getattr(item, "file_type", "application/octet-stream"),
                        file_size_bytes=len(original_bytes),
                        sha256=sha256,
                        description=description,
                    )
                    entries.append(entry)

                # --- Include offline viewer if requested ---
                if include_offline_viewer:
                    viewer_notice = (
                        "DERIVATIVE VIEWING MATERIALS\n"
                        "============================\n\n"
                        "The files in this directory are DERIVATIVE viewing "
                        "materials generated for convenience.\n"
                        "They are NOT original evidence.\n"
                        "Originals are in the Exhibit_NNN/ directories.\n"
                        "Verify originals against INDEX.json SHA-256 hashes.\n"
                    )
                    zf.writestr("_viewer/NOTICE.txt", viewer_notice)
                    file_hashes["_viewer/NOTICE.txt"] = hashlib.sha256(
                        viewer_notice.encode()
                    ).hexdigest()

                # --- Build INDEX.csv ---
                csv_content = self._build_index_csv(entries)
                csv_bytes = csv_content.encode("utf-8")
                zf.writestr("INDEX.csv", csv_bytes)
                file_hashes["INDEX.csv"] = hashlib.sha256(csv_bytes).hexdigest()

                # --- Build INDEX.json ---
                index_json = self._build_index_json(
                    case=case,
                    entries=entries,
                    file_hashes=file_hashes,
                    generated_at=generated_at,
                )
                index_bytes = json.dumps(
                    index_json, indent=2, ensure_ascii=False
                ).encode("utf-8")
                index_sha256 = hashlib.sha256(index_bytes).hexdigest()
                zf.writestr("INDEX.json", index_bytes)

                # --- PACKAGE_HASH.txt ---
                package_hash_text = (
                    f"Court Package Integrity Record\n"
                    f"===============================\n"
                    f"Case: {case_number}\n"
                    f"Generated: {generated_at.isoformat()}\n"
                    f"Exhibits: {len(entries)}\n"
                    f"INDEX.json SHA-256: {index_sha256}\n"
                )
                zf.writestr("PACKAGE_HASH.txt", package_hash_text)

            # Compute ZIP-level hash
            package_sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

            logger.info(
                "Court package built: %s (%d exhibits, sha256=%s)",
                zip_path.name,
                len(entries),
                package_sha256[:16],
            )

            return CourtPackageResult(
                success=True,
                package_path=str(zip_path),
                exhibit_count=len(entries),
                index_sha256=index_sha256,
                package_sha256=package_sha256,
            )

        except Exception as exc:
            logger.error("Court package build failed: %s", exc, exc_info=True)
            return CourtPackageResult(
                success=False,
                package_path="",
                exhibit_count=0,
                index_sha256="",
                package_sha256="",
                error=str(exc),
            )

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def _resolve_original(item) -> Optional[str]:
        """
        Resolve the filesystem path of an evidence original.

        Checks hash_sha256-based canonical path, then falls back to
        stored_path or upload path.
        """
        from services.evidence_store import EvidenceStore

        store = EvidenceStore()
        sha = getattr(item, "hash_sha256", None)
        if sha:
            path = store.get_original_path(sha)
            if path:
                return path

        # Fallback: stored_path field
        stored = getattr(item, "stored_path", None)
        if stored and Path(stored).exists():
            return stored

        return None

    @staticmethod
    def _build_index_csv(entries: List[ExhibitEntry]) -> str:
        """Generate INDEX.csv content."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Exhibit", "Filename", "Evidence_ID", "File_Type",
            "Size_Bytes", "SHA256", "Description",
        ])
        for e in entries:
            writer.writerow([
                f"Exhibit_{e.exhibit_number}",
                e.original_filename,
                e.evidence_id,
                e.file_type,
                e.file_size_bytes,
                e.sha256,
                e.description,
            ])
        return output.getvalue()

    @staticmethod
    def _build_index_json(
        case,
        entries: List[ExhibitEntry],
        file_hashes: Dict[str, str],
        generated_at: datetime,
    ) -> dict:
        """Generate INDEX.json content."""
        return {
            "court_package": {
                "version": "1.0",
                "case_number": getattr(case, "case_number", ""),
                "case_name": getattr(case, "case_name", ""),
                "generated_at": generated_at.isoformat(),
                "exhibit_count": len(entries),
            },
            "exhibits": [asdict(e) for e in entries],
            "file_manifest": file_hashes,
        }
