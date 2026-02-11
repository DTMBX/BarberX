"""
Court-Ready Evidence Export
============================
Produces a self-contained ZIP archive suitable for court submission.

Package contents:
  evidence_package_<evidence_id>/
    originals/          — Immutable originals
    derivatives/        — Thumbnails, proxies, transcripts
    manifest.json       — Hashes, sizes, relationships, metadata
    audit_log.json      — Full append-only audit trail
    integrity_report.md — Human-readable integrity summary

Design principles:
  - Deterministic: Same inputs → same logical outputs.
  - Self-verifying: Manifest contains hashes for ALL included files.
  - Human-readable: Integrity report is plain Markdown.
  - No external dependencies at read time.
"""

import hashlib
import json
import logging
import os
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from services.evidence_store import (
    EvidenceStore,
    compute_file_hash,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Export data structure
# ---------------------------------------------------------------------------


class EvidenceExportResult:
    """Result of an evidence export operation."""

    def __init__(
        self,
        success: bool,
        export_path: str = "",
        evidence_id: str = "",
        file_count: int = 0,
        total_bytes: int = 0,
        package_sha256: str = "",
        error: Optional[str] = None,
    ):
        self.success = success
        self.export_path = export_path
        self.evidence_id = evidence_id
        self.file_count = file_count
        self.total_bytes = total_bytes
        self.package_sha256 = package_sha256
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "export_path": self.export_path,
            "evidence_id": self.evidence_id,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "package_sha256": self.package_sha256,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Export builder
# ---------------------------------------------------------------------------


class EvidenceExporter:
    """
    Builds court-ready evidence packages from the evidence store.

    Each package is a ZIP file containing originals, derivatives,
    manifest, audit log, and a human-readable integrity report.
    """

    def __init__(self, evidence_store: EvidenceStore, export_dir: str = "exports"):
        self._store = evidence_store
        self._export_dir = Path(export_dir).resolve()
        self._export_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        evidence_id: str,
        include_derivatives: bool = True,
        exported_by: Optional[str] = None,
    ) -> EvidenceExportResult:
        """
        Build and write a court-ready evidence export package.

        Args:
            evidence_id: UUID of the evidence to export.
            include_derivatives: Whether to include thumbnails/proxies.
            exported_by: Name of the user performing the export.

        Returns:
            EvidenceExportResult with path to the ZIP file.
        """
        manifest = self._store.load_manifest(evidence_id)
        if manifest is None:
            return EvidenceExportResult(
                success=False,
                evidence_id=evidence_id,
                error=f"Manifest not found for evidence_id={evidence_id}",
            )

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        package_name = f"evidence_package_{evidence_id[:8]}_{timestamp}"
        zip_path = self._export_dir / f"{package_name}.zip"

        try:
            file_count = 0
            total_bytes = 0
            # Track files added for the integrity report
            included_files: List[Dict] = []

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                prefix = package_name

                # -- 1. Original file --
                original_path = self._store.get_original_path(
                    manifest.ingest.sha256
                )
                if original_path and os.path.exists(original_path):
                    arcname = f"{prefix}/originals/{manifest.ingest.original_filename}"
                    zf.write(original_path, arcname)
                    fsize = os.path.getsize(original_path)
                    file_count += 1
                    total_bytes += fsize
                    included_files.append({
                        "path": arcname,
                        "sha256": manifest.ingest.sha256,
                        "size_bytes": fsize,
                        "type": "original",
                    })

                # -- 2. Derivatives --
                if include_derivatives:
                    for deriv in manifest.derivatives:
                        deriv_path = self._store.get_derivative_path(
                            manifest.ingest.sha256,
                            deriv.derivative_type,
                            deriv.filename,
                        )
                        if deriv_path and os.path.exists(deriv_path):
                            arcname = (
                                f"{prefix}/derivatives/"
                                f"{deriv.derivative_type}/{deriv.filename}"
                            )
                            zf.write(deriv_path, arcname)
                            fsize = os.path.getsize(deriv_path)
                            file_count += 1
                            total_bytes += fsize
                            included_files.append({
                                "path": arcname,
                                "sha256": deriv.sha256,
                                "size_bytes": fsize,
                                "type": f"derivative:{deriv.derivative_type}",
                            })

                # -- 3. Manifest JSON --
                manifest_json = json.dumps(
                    {
                        "evidence_id": manifest.evidence_id,
                        "ingest": {
                            "original_filename": manifest.ingest.original_filename,
                            "mime_type": manifest.ingest.mime_type,
                            "size_bytes": manifest.ingest.size_bytes,
                            "sha256": manifest.ingest.sha256,
                            "ingested_at": manifest.ingest.ingested_at,
                            "ingested_by": manifest.ingest.ingested_by,
                            "device_label": manifest.ingest.device_label,
                        },
                        "derivatives": [
                            {
                                "type": d.derivative_type,
                                "filename": d.filename,
                                "sha256": d.sha256,
                                "size_bytes": d.size_bytes,
                                "created_at": d.created_at,
                            }
                            for d in manifest.derivatives
                        ],
                        "included_files": included_files,
                        "export_metadata": {
                            "exported_at": timestamp,
                            "exported_by": exported_by,
                            "include_derivatives": include_derivatives,
                        },
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                zf.writestr(f"{prefix}/manifest.json", manifest_json)
                file_count += 1
                total_bytes += len(manifest_json.encode("utf-8"))

                # -- 4. Audit log JSON --
                audit_json = json.dumps(
                    {
                        "evidence_id": manifest.evidence_id,
                        "audit_entries": manifest.audit_entries,
                        "entry_count": len(manifest.audit_entries),
                    },
                    indent=2,
                    default=str,
                    ensure_ascii=False,
                )
                zf.writestr(f"{prefix}/audit_log.json", audit_json)
                file_count += 1
                total_bytes += len(audit_json.encode("utf-8"))

                # -- 5. Integrity report (Markdown) --
                report_md = self._build_integrity_report(
                    manifest, included_files, exported_by, timestamp
                )
                zf.writestr(f"{prefix}/integrity_report.md", report_md)
                file_count += 1
                total_bytes += len(report_md.encode("utf-8"))

            # Hash the final package
            package_digest = compute_file_hash(str(zip_path))

            # Record export in audit if possible
            self._store.append_audit(
                evidence_id=evidence_id,
                action="exported",
                actor=exported_by,
                details={
                    "package_path": str(zip_path),
                    "package_sha256": package_digest.sha256,
                    "file_count": file_count,
                    "total_bytes": total_bytes,
                },
            )

            logger.info(
                "Exported evidence %s: %s (%d files, %d bytes, sha256=%s)",
                evidence_id,
                zip_path.name,
                file_count,
                total_bytes,
                package_digest.sha256[:16],
            )

            return EvidenceExportResult(
                success=True,
                export_path=str(zip_path),
                evidence_id=evidence_id,
                file_count=file_count,
                total_bytes=total_bytes,
                package_sha256=package_digest.sha256,
            )

        except Exception as exc:
            logger.error(
                "Export failed for %s: %s", evidence_id, exc, exc_info=True
            )
            # Clean up partial ZIP
            if zip_path.exists():
                zip_path.unlink()
            return EvidenceExportResult(
                success=False,
                evidence_id=evidence_id,
                error=str(exc),
            )

    # -- integrity report generation -----------------------------------------

    @staticmethod
    def _build_integrity_report(
        manifest,
        included_files: List[Dict],
        exported_by: Optional[str],
        timestamp: str,
    ) -> str:
        """Generate a human-readable Markdown integrity report."""
        lines = [
            "# Evidence Integrity Report",
            "",
            f"**Evidence ID:** {manifest.evidence_id}",
            f"**Export Timestamp:** {timestamp}",
            f"**Exported By:** {exported_by or 'system'}",
            "",
            "---",
            "",
            "## Original File",
            "",
            f"- **Filename:** {manifest.ingest.original_filename}",
            f"- **MIME Type:** {manifest.ingest.mime_type}",
            f"- **Size:** {manifest.ingest.size_bytes:,} bytes",
            f"- **SHA-256:** `{manifest.ingest.sha256}`",
            f"- **Ingested At:** {manifest.ingest.ingested_at}",
            f"- **Ingested By:** {manifest.ingest.ingested_by or 'system'}",
        ]

        if manifest.ingest.device_label:
            lines.append(f"- **Device:** {manifest.ingest.device_label}")

        lines.extend([
            "",
            "---",
            "",
            "## Derivatives",
            "",
        ])

        if manifest.derivatives:
            lines.append("| Type | Filename | SHA-256 | Size |")
            lines.append("|------|----------|---------|------|")
            for d in manifest.derivatives:
                lines.append(
                    f"| {d.derivative_type} | {d.filename} | "
                    f"`{d.sha256[:16]}...` | {d.size_bytes:,} bytes |"
                )
        else:
            lines.append("No derivatives included in this export.")

        lines.extend([
            "",
            "---",
            "",
            "## Audit Trail",
            "",
            f"Total entries: {len(manifest.audit_entries)}",
            "",
        ])

        for entry in manifest.audit_entries:
            ts = entry.get("timestamp", "N/A")
            action = entry.get("action", "N/A")
            actor = entry.get("actor", "system")
            lines.append(f"- **{ts}** — {action} (by {actor})")

        lines.extend([
            "",
            "---",
            "",
            "## Package Contents",
            "",
            "| File | Type | SHA-256 | Size |",
            "|------|------|---------|------|",
        ])

        for f in included_files:
            sha_display = f["sha256"][:16] + "..." if f["sha256"] else "N/A"
            lines.append(
                f"| {f['path']} | {f['type']} | `{sha_display}` | "
                f"{f['size_bytes']:,} bytes |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Verification Instructions",
            "",
            "To verify the integrity of the original file:",
            "",
            "```",
            f"certutil -hashfile <original_file> SHA256",
            "```",
            "",
            f"Expected hash: `{manifest.ingest.sha256}`",
            "",
            "Any deviation from this hash indicates the file has been "
            "altered since intake.",
            "",
            "---",
            "",
            f"*Report generated {timestamp} by Evident Technologies*",
        ])

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Case-level export builder
# ---------------------------------------------------------------------------


@dataclass
class CaseExportResult:
    """Result of a case-scoped export."""

    success: bool
    export_path: str = ""
    case_id: int = 0
    evidence_count: int = 0
    file_count: int = 0
    total_bytes: int = 0
    package_sha256: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "export_path": self.export_path,
            "case_id": self.case_id,
            "evidence_count": self.evidence_count,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "package_sha256": self.package_sha256,
            "error": self.error,
        }


class CaseExporter:
    """
    Builds a court-ready case export package containing all linked
    evidence, each with its originals, derivatives, manifest, and
    audit trail, plus a case-level summary.

    The package is a ZIP file structured as:
        case_<number>_<timestamp>/
            case_manifest.json
            case_integrity_report.md
            evidence/
                <evidence_uuid_1>/
                    originals/
                    derivatives/
                    manifest.json
                    audit_log.json
                <evidence_uuid_2>/
                    ...
    """

    def __init__(self, evidence_store: EvidenceStore, export_dir: str = "exports"):
        self._store = evidence_store
        self._export_dir = Path(export_dir).resolve()
        self._export_dir.mkdir(parents=True, exist_ok=True)

    def export_case(
        self,
        case,
        evidence_items,
        exported_by: Optional[str] = None,
    ) -> CaseExportResult:
        """
        Build a case-scoped export package.

        Args:
            case: LegalCase model instance.
            evidence_items: List of EvidenceItem instances linked to the case.
            exported_by: Name/email of the exporting user.

        Returns:
            CaseExportResult with path to the ZIP file.
        """
        case_num = case.case_number or f"case_{case.id}"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        package_name = f"case_{case_num}_{timestamp}"
        zip_path = self._export_dir / f"{package_name}.zip"

        try:
            file_count = 0
            total_bytes = 0
            evidence_summaries = []

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                prefix = package_name

                for item in evidence_items:
                    ev_id = item.evidence_store_id
                    if not ev_id:
                        continue

                    manifest = self._store.load_manifest(ev_id)
                    if manifest is None:
                        evidence_summaries.append({
                            "evidence_id": ev_id,
                            "filename": item.original_filename,
                            "status": "manifest_missing",
                        })
                        continue

                    ev_prefix = f"{prefix}/evidence/{ev_id}"
                    ev_files = []

                    # Original
                    orig_path = self._store.get_original_path(
                        manifest.ingest.sha256
                    )
                    if orig_path and os.path.exists(orig_path):
                        arcname = (
                            f"{ev_prefix}/originals/"
                            f"{manifest.ingest.original_filename}"
                        )
                        zf.write(orig_path, arcname)
                        fsize = os.path.getsize(orig_path)
                        file_count += 1
                        total_bytes += fsize
                        ev_files.append({
                            "path": arcname,
                            "sha256": manifest.ingest.sha256,
                            "size_bytes": fsize,
                            "type": "original",
                        })

                    # Derivatives
                    for deriv in manifest.derivatives:
                        deriv_path = self._store.get_derivative_path(
                            manifest.ingest.sha256,
                            deriv.derivative_type,
                            deriv.filename,
                        )
                        if deriv_path and os.path.exists(deriv_path):
                            arcname = (
                                f"{ev_prefix}/derivatives/"
                                f"{deriv.derivative_type}/{deriv.filename}"
                            )
                            zf.write(deriv_path, arcname)
                            fsize = os.path.getsize(deriv_path)
                            file_count += 1
                            total_bytes += fsize
                            ev_files.append({
                                "path": arcname,
                                "sha256": deriv.sha256,
                                "size_bytes": fsize,
                                "type": f"derivative:{deriv.derivative_type}",
                            })

                    # Per-evidence manifest
                    ev_manifest = json.dumps({
                        "evidence_id": ev_id,
                        "original_filename": manifest.ingest.original_filename,
                        "sha256": manifest.ingest.sha256,
                        "mime_type": manifest.ingest.mime_type,
                        "size_bytes": manifest.ingest.size_bytes,
                        "ingested_at": manifest.ingest.ingested_at,
                        "files_included": ev_files,
                    }, indent=2, ensure_ascii=False)
                    zf.writestr(f"{ev_prefix}/manifest.json", ev_manifest)
                    file_count += 1
                    total_bytes += len(ev_manifest.encode("utf-8"))

                    # Per-evidence audit log
                    audit_json = json.dumps({
                        "evidence_id": ev_id,
                        "audit_entries": manifest.audit_entries,
                        "entry_count": len(manifest.audit_entries),
                    }, indent=2, default=str, ensure_ascii=False)
                    zf.writestr(f"{ev_prefix}/audit_log.json", audit_json)
                    file_count += 1
                    total_bytes += len(audit_json.encode("utf-8"))

                    evidence_summaries.append({
                        "evidence_id": ev_id,
                        "filename": manifest.ingest.original_filename,
                        "sha256": manifest.ingest.sha256,
                        "file_count": len(ev_files),
                        "status": "exported",
                    })

                # Case-level manifest
                case_manifest = json.dumps({
                    "case_number": case.case_number,
                    "case_name": case.case_name,
                    "case_type": case.case_type,
                    "jurisdiction": case.jurisdiction,
                    "jurisdiction_state": getattr(case, "jurisdiction_state", None),
                    "jurisdiction_agency_type": getattr(
                        case, "jurisdiction_agency_type", None
                    ),
                    "incident_number": getattr(case, "incident_number", None),
                    "evidence_count": len(evidence_summaries),
                    "evidence": evidence_summaries,
                    "export_metadata": {
                        "exported_at": timestamp,
                        "exported_by": exported_by,
                        "package_name": package_name,
                    },
                }, indent=2, ensure_ascii=False)
                zf.writestr(f"{prefix}/case_manifest.json", case_manifest)
                file_count += 1
                total_bytes += len(case_manifest.encode("utf-8"))

                # Case-level integrity report
                report_md = self._build_case_report(
                    case, evidence_summaries, exported_by, timestamp
                )
                zf.writestr(
                    f"{prefix}/case_integrity_report.md", report_md
                )
                file_count += 1
                total_bytes += len(report_md.encode("utf-8"))

            # Hash the final ZIP package
            package_digest = compute_file_hash(str(zip_path))

            logger.info(
                "Exported case %s: %s (%d evidence, %d files, %d bytes, "
                "sha256=%s)",
                case_num, zip_path.name, len(evidence_summaries),
                file_count, total_bytes, package_digest.sha256[:16],
            )

            return CaseExportResult(
                success=True,
                export_path=str(zip_path),
                case_id=case.id,
                evidence_count=len(evidence_summaries),
                file_count=file_count,
                total_bytes=total_bytes,
                package_sha256=package_digest.sha256,
            )

        except Exception as exc:
            logger.error(
                "Case export failed for %s: %s",
                case_num, exc, exc_info=True,
            )
            if zip_path.exists():
                zip_path.unlink()
            return CaseExportResult(
                success=False,
                case_id=case.id,
                error=str(exc),
            )

    @staticmethod
    def _build_case_report(
        case,
        evidence_summaries: List[Dict],
        exported_by: Optional[str],
        timestamp: str,
    ) -> str:
        """Generate a case-level integrity report in Markdown."""
        lines = [
            "# Case Export Integrity Report",
            "",
            f"**Case Number:** {case.case_number}",
            f"**Case Name:** {case.case_name}",
            f"**Case Type:** {case.case_type or 'N/A'}",
            f"**Jurisdiction:** {case.jurisdiction or 'N/A'}",
            f"**Export Timestamp:** {timestamp}",
            f"**Exported By:** {exported_by or 'system'}",
            "",
            "---",
            "",
            "## Evidence Items",
            "",
            "| # | Filename | SHA-256 | Status |",
            "|---|----------|---------|--------|",
        ]

        for i, ev in enumerate(evidence_summaries, 1):
            sha = ev.get("sha256", "N/A")
            sha_display = f"`{sha[:16]}...`" if sha and sha != "N/A" else "N/A"
            lines.append(
                f"| {i} | {ev.get('filename', 'N/A')} | "
                f"{sha_display} | {ev.get('status', 'N/A')} |"
            )

        exported_count = sum(
            1 for e in evidence_summaries if e.get("status") == "exported"
        )
        lines.extend([
            "",
            f"**Total evidence items:** {len(evidence_summaries)}",
            f"**Successfully exported:** {exported_count}",
            "",
            "---",
            "",
            "## Verification",
            "",
            "Each evidence item directory contains its own `manifest.json` "
            "and `audit_log.json`. Verify individual items by comparing the "
            "SHA-256 hash of the original file against the value recorded in "
            "the manifest.",
            "",
            "```",
            "certutil -hashfile <original_file> SHA256",
            "```",
            "",
            "---",
            "",
            f"*Report generated {timestamp} by Evident Technologies*",
        ])

        return "\n".join(lines)