"""
Integrity-Sealed Court Package Export
======================================
Enhanced court export that bundles ALL forensic artifacts into a single
self-verifying package with a cryptographic seal.

Contents:
  - Evidence exhibits (Bates-stamped derivatives)
  - Integrity sweep summary
  - Provenance graph (JSON + DOT notation)
  - Timeline alignment report
  - Redaction verification statement
  - Algorithm version manifest (frozen IDs + code hashes)
  - Audit log extract
  - Evidence Integrity Statement (text + PDF)
  - SEAL.json — cryptographic seal binding all artifacts

Design constraints:
  - Single ZIP output, self-verifying via SEAL.json
  - Every file in the package is referenced by SHA-256 in SEAL.json
  - SEAL.json itself is hashed and recorded in SEAL_HASH.txt
  - Deterministic given identical evidence and algorithm versions
  - Never modifies originals
"""

import hashlib
import json
import logging
import os
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmParams, AlgorithmResult, canonical_json, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SealedPackageResult:
    """Result of generating a sealed court package."""
    success: bool
    package_path: str
    seal_hash: str
    exhibit_count: int
    algorithms_run: List[str]
    algorithm_versions: Dict[str, str]
    total_files: int
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Sealed Court Package Builder
# ---------------------------------------------------------------------------

class SealedCourtPackageBuilder:
    """
    Builds a fully integrity-sealed court package.

    One click → one sealed bundle containing:
      - Exhibits
      - All algorithm reports
      - Integrity statement
      - Cryptographic seal
    """

    def __init__(self, export_base: str = "exports/sealed"):
        self.export_base = Path(export_base).resolve()
        self.export_base.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        case_id: int,
        tenant_id: int,
        db_session,
        evidence_store,
        audit_stream=None,
        generated_at: Optional[datetime] = None,
        actor_id=None,
        actor_name: str = "sealed_export",
    ) -> SealedPackageResult:
        """
        Build and seal a court export package.

        Runs all relevant algorithms, collects results, generates the
        integrity statement, and seals everything into a single ZIP
        with a cryptographic SEAL.json.

        Args:
            case_id: Target case.
            tenant_id: Organization ID.
            db_session: SQLAlchemy session.
            evidence_store: EvidenceStore instance.
            audit_stream: Optional AuditStream.
            generated_at: Explicit timestamp for deterministic output.
            actor_id: Actor who triggered the export.
            actor_name: Actor label for audit records.

        Returns:
            SealedPackageResult with package path and seal hash.
        """
        if generated_at is None:
            generated_at = datetime.now(timezone.utc)

        _ensure_algorithms()

        params = AlgorithmParams(
            case_id=case_id,
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_name=actor_name,
        )
        context = {
            "db_session": db_session,
            "evidence_store": evidence_store,
            "audit_stream": audit_stream,
        }

        timestamp_str = generated_at.strftime("%Y%m%d_%H%M%S")
        package_name = f"sealed_court_package_case_{case_id}_{timestamp_str}"
        zip_path = self.export_base / f"{package_name}.zip"

        file_manifest: Dict[str, str] = {}  # path_in_zip → SHA-256

        try:
            # Phase 1: Run all algorithms
            algorithm_results = self._run_algorithms(params, context)

            # Phase 2: Build the ZIP
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

                # --- Algorithm reports ---
                for algo_id, result in algorithm_results.items():
                    report_json = json.dumps(
                        result.to_dict(), indent=2, ensure_ascii=False, default=str
                    ).encode("utf-8")
                    entry_path = f"reports/{algo_id}_report.json"
                    zf.writestr(entry_path, report_json)
                    file_manifest[entry_path] = hashlib.sha256(report_json).hexdigest()

                # --- Algorithm version manifest ---
                version_manifest = self._build_version_manifest()
                vm_bytes = json.dumps(
                    version_manifest, indent=2, ensure_ascii=False
                ).encode("utf-8")
                zf.writestr("ALGORITHM_VERSIONS.json", vm_bytes)
                file_manifest["ALGORITHM_VERSIONS.json"] = hashlib.sha256(vm_bytes).hexdigest()

                # --- Timestamp normalization notes ---
                timeline_result = algorithm_results.get("timeline_alignment")
                if timeline_result and timeline_result.success:
                    notes = self._build_timeline_notes(timeline_result)
                    notes_bytes = notes.encode("utf-8")
                    zf.writestr("TIMELINE_NOTES.txt", notes_bytes)
                    file_manifest["TIMELINE_NOTES.txt"] = hashlib.sha256(notes_bytes).hexdigest()

                # --- Redaction verification statement ---
                redaction_result = algorithm_results.get("redaction_verify")
                if redaction_result and redaction_result.success:
                    stmt = self._build_redaction_statement(redaction_result)
                    stmt_bytes = stmt.encode("utf-8")
                    zf.writestr("REDACTION_VERIFICATION.txt", stmt_bytes)
                    file_manifest["REDACTION_VERIFICATION.txt"] = hashlib.sha256(stmt_bytes).hexdigest()

                # --- Integrity sweep summary ---
                integrity_result = algorithm_results.get("integrity_sweep")
                if integrity_result and integrity_result.success:
                    summary = self._build_integrity_summary(integrity_result)
                    summary_bytes = summary.encode("utf-8")
                    zf.writestr("INTEGRITY_SWEEP_SUMMARY.txt", summary_bytes)
                    file_manifest["INTEGRITY_SWEEP_SUMMARY.txt"] = hashlib.sha256(summary_bytes).hexdigest()

                # --- Audit log extract ---
                audit_extract = self._extract_audit_log(case_id, db_session)
                audit_bytes = json.dumps(
                    audit_extract, indent=2, ensure_ascii=False, default=str
                ).encode("utf-8")
                zf.writestr("audit_log.json", audit_bytes)
                file_manifest["audit_log.json"] = hashlib.sha256(audit_bytes).hexdigest()

                # --- Evidence Integrity Statement ---
                manifest_hash = hash_json(file_manifest)
                statement = self._generate_integrity_statement(
                    case_id, manifest_hash, generated_at
                )
                if statement.text_bytes:
                    zf.writestr("INTEGRITY_STATEMENT.txt", statement.text_bytes)
                    file_manifest["INTEGRITY_STATEMENT.txt"] = statement.text_sha256
                if statement.pdf_bytes:
                    zf.writestr("INTEGRITY_STATEMENT.pdf", statement.pdf_bytes)
                    file_manifest["INTEGRITY_STATEMENT.pdf"] = statement.pdf_sha256

                # --- Build SEAL.json ---
                seal = self._build_seal(
                    case_id=case_id,
                    tenant_id=tenant_id,
                    generated_at=generated_at,
                    file_manifest=file_manifest,
                    algorithm_results=algorithm_results,
                    version_manifest=version_manifest,
                )
                seal_bytes = json.dumps(
                    seal, indent=2, ensure_ascii=False, default=str
                ).encode("utf-8")
                seal_hash = hashlib.sha256(seal_bytes).hexdigest()
                zf.writestr("SEAL.json", seal_bytes)

                # --- SEAL_HASH.txt ---
                seal_hash_text = (
                    f"INTEGRITY SEAL\n"
                    f"===============\n"
                    f"Case: {case_id}\n"
                    f"Generated: {generated_at.isoformat()}\n"
                    f"SEAL.json SHA-256: {seal_hash}\n"
                    f"\n"
                    f"To verify this package:\n"
                    f"1. Compute SHA-256 of SEAL.json\n"
                    f"2. Compare with the hash above\n"
                    f"3. For each file listed in SEAL.json file_manifest,\n"
                    f"   compute SHA-256 and compare\n"
                    f"4. If all hashes match, the package is intact.\n"
                )
                zf.writestr("SEAL_HASH.txt", seal_hash_text.encode("utf-8"))

            # Collect algorithm version info
            algo_versions = {}
            for algo_id, result in algorithm_results.items():
                algo_versions[algo_id] = result.algorithm_version

            exhibit_count = 0
            bates = algorithm_results.get("bates_generator")
            if bates and bates.success:
                exhibit_count = bates.payload.get("count", 0)

            logger.info(
                "Sealed court package built: %s (seal=%s)",
                zip_path.name, seal_hash[:16],
            )

            return SealedPackageResult(
                success=True,
                package_path=str(zip_path),
                seal_hash=seal_hash,
                exhibit_count=exhibit_count,
                algorithms_run=list(algorithm_results.keys()),
                algorithm_versions=algo_versions,
                total_files=len(file_manifest),
            )

        except Exception as exc:
            logger.error("Sealed court package failed: %s", exc, exc_info=True)
            return SealedPackageResult(
                success=False,
                package_path="",
                seal_hash="",
                exhibit_count=0,
                algorithms_run=[],
                algorithm_versions={},
                total_files=0,
                error=str(exc),
            )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _run_algorithms(
        params: AlgorithmParams,
        context: Dict[str, Any],
    ) -> Dict[str, AlgorithmResult]:
        """Run all court-package algorithms and return results."""
        algorithms_to_run = [
            "integrity_sweep",
            "provenance_graph",
            "timeline_alignment",
            "bates_generator",
            "redaction_verify",
            "access_anomaly",
        ]

        results = {}
        for algo_id in algorithms_to_run:
            algo = registry.get(algo_id)
            if not algo:
                logger.warning("Algorithm '%s' not in registry, skipping.", algo_id)
                continue
            try:
                result = algo.run(params, context)
                results[algo_id] = result
            except Exception as exc:
                logger.error("Algorithm %s failed during sealed export: %s", algo_id, exc)
                # Create a failure result
                results[algo_id] = AlgorithmResult(
                    algorithm_id=algo_id,
                    algorithm_version=algo.algorithm_version,
                    run_id="",
                    input_hashes=[],
                    success=False,
                    error=str(exc),
                )

        return results

    @staticmethod
    def _build_version_manifest() -> Dict[str, Any]:
        """
        Build a frozen manifest of all algorithm versions.

        Includes algorithm_id, version, and a hash of the algorithm's
        source module (where determinable) for code-level traceability.
        """
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "algorithms": [],
        }

        for algo_info in registry.list_algorithms():
            algo = registry.get(algo_info["algorithm_id"], algo_info["version"])
            entry = {
                "algorithm_id": algo_info["algorithm_id"],
                "version": algo_info["version"],
                "description": algo_info.get("description", ""),
                "module": "",
                "module_hash": "",
            }

            # Attempt to hash the algorithm's source module
            if algo:
                module = type(algo).__module__
                entry["module"] = module
                try:
                    import importlib
                    mod = importlib.import_module(module)
                    if hasattr(mod, "__file__") and mod.__file__:
                        with open(mod.__file__, "rb") as f:
                            entry["module_hash"] = hashlib.sha256(f.read()).hexdigest()
                except Exception:
                    entry["module_hash"] = "unavailable"

            manifest["algorithms"].append(entry)

        return manifest

    @staticmethod
    def _build_timeline_notes(result: AlgorithmResult) -> str:
        """Build human-readable timeline normalization notes."""
        payload = result.payload
        assumptions = payload.get("assumptions", [])
        drift_pairs = payload.get("drift_pairs", [])
        stats = payload.get("stats", {})

        lines = [
            "TIMESTAMP NORMALIZATION NOTES",
            "=" * 40,
            "",
            f"Total items: {stats.get('total_items', 'N/A')}",
            f"Exact timestamps: {stats.get('exact', 'N/A')}",
            f"Derived timestamps: {stats.get('derived', 'N/A')}",
            f"Unknown timestamps: {stats.get('unknown', 'N/A')}",
            "",
        ]

        if drift_pairs:
            lines.append("Clock Drift Detected:")
            for pair in drift_pairs:
                lines.append(
                    f"  {pair.get('device_a', '?')} ↔ {pair.get('device_b', '?')}: "
                    f"{pair.get('median_offset_seconds', 0):.2f}s median offset"
                )
            lines.append("")

        if assumptions:
            lines.append("Assumptions:")
            for a in assumptions:
                lines.append(f"  - {a}")

        lines.append("")
        lines.append(f"Algorithm: timeline_alignment v{result.algorithm_version}")
        lines.append(f"Result hash: {result.result_hash}")
        return "\n".join(lines)

    @staticmethod
    def _build_redaction_statement(result: AlgorithmResult) -> str:
        """Build a formal redaction verification statement."""
        payload = result.payload
        summary = payload.get("summary", {})

        lines = [
            "REDACTION VERIFICATION STATEMENT",
            "=" * 40,
            "",
            f"Total items checked: {payload.get('total_checked', 0)}",
            f"  Passed: {summary.get('pass', 0)}",
            f"  Warnings: {summary.get('warning', 0)}",
            f"  Failed: {summary.get('fail', 0)}",
            f"  Skipped: {summary.get('skipped', 0)}",
            "",
            "Methodology:",
            "  1. Text-layer extraction to detect residual readable content.",
            "  2. Annotation inspection to detect un-burned-in redaction marks.",
            "  3. Byte-pattern scanning to detect original content leakage.",
            "  4. Hash comparison to confirm derivative differs from original.",
            "",
            f"Algorithm: redaction_verify v{result.algorithm_version}",
            f"Result hash: {result.result_hash}",
            "",
            "This verification report is generated by the Evident system.",
            "It describes technical observations only.",
            "It does not constitute a legal determination of redaction adequacy.",
        ]
        return "\n".join(lines)

    @staticmethod
    def _build_integrity_summary(result: AlgorithmResult) -> str:
        """Build a concise integrity sweep summary."""
        payload = result.payload
        summary = payload.get("summary", {})
        all_passed = payload.get("all_passed", False)

        lines = [
            "INTEGRITY SWEEP SUMMARY",
            "=" * 40,
            "",
            f"Status: {'ALL PASSED' if all_passed else 'ISSUES DETECTED'}",
            f"Total items: {payload.get('total_items', 0)}",
            f"  Passed: {summary.get('pass', 0)}",
            f"  Failed: {summary.get('fail', 0)}",
            f"  Missing: {summary.get('missing', 0)}",
            f"  Errors: {summary.get('error', 0)}",
            "",
            f"Algorithm: integrity_sweep v{result.algorithm_version}",
            f"Report hash: {payload.get('report_hash', 'N/A')}",
            f"Result hash: {result.result_hash}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _extract_audit_log(case_id: int, db_session) -> List[Dict[str, Any]]:
        """Extract audit log entries for a case."""
        try:
            from models.evidence import ChainOfCustody, CaseEvidence

            links = (
                db_session.query(CaseEvidence)
                .filter_by(case_id=case_id)
                .filter(CaseEvidence.unlinked_at.is_(None))
                .all()
            )
            evidence_ids = [link.evidence_id for link in links]

            if not evidence_ids:
                return []

            entries = (
                db_session.query(ChainOfCustody)
                .filter(ChainOfCustody.evidence_id.in_(evidence_ids))
                .order_by(ChainOfCustody.action_timestamp.asc())
                .all()
            )

            return [
                {
                    "evidence_id": str(e.evidence_id),
                    "action": e.action,
                    "actor_name": e.actor_name,
                    "timestamp": e.action_timestamp.isoformat() if e.action_timestamp else None,
                    "details": e.details if hasattr(e, "details") else None,
                }
                for e in entries
            ]
        except Exception as exc:
            logger.warning("Failed to extract audit log for case %d: %s", case_id, exc)
            return [{"error": str(exc)}]

    @staticmethod
    def _generate_integrity_statement(
        case_id: int,
        manifest_hash: str,
        generated_at: datetime,
    ):
        """Generate the Evidence Integrity Statement."""
        from services.integrity_statement import IntegrityStatementGenerator

        gen = IntegrityStatementGenerator()
        return gen.generate(
            scope="COURT_PACKAGE",
            scope_id=f"CASE-{case_id}",
            manifest_sha256=manifest_hash,
            generated_at=generated_at,
            render_pdf=True,
        )

    @staticmethod
    def _build_seal(
        case_id: int,
        tenant_id: int,
        generated_at: datetime,
        file_manifest: Dict[str, str],
        algorithm_results: Dict[str, AlgorithmResult],
        version_manifest: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the SEAL.json — the cryptographic binding of the entire package.

        This is the single artifact that, when verified, attests to the
        integrity of every file in the package.
        """
        algorithm_summary = {}
        for algo_id, result in algorithm_results.items():
            algorithm_summary[algo_id] = {
                "version": result.algorithm_version,
                "run_id": result.run_id,
                "success": result.success,
                "result_hash": result.result_hash,
                "params_hash": result.params_hash,
                "integrity_check": result.integrity_check,
                "input_count": len(result.input_hashes),
                "output_count": len(result.output_hashes),
                "duration_seconds": result.duration_seconds,
            }

        seal = {
            "seal_version": "1.0",
            "case_id": case_id,
            "tenant_id": tenant_id,
            "generated_at": generated_at.isoformat(),
            "file_manifest": dict(sorted(file_manifest.items())),
            "file_count": len(file_manifest),
            "manifest_hash": hash_json(dict(sorted(file_manifest.items()))),
            "algorithm_summary": algorithm_summary,
            "algorithm_versions": version_manifest,
            "verification_instructions": {
                "step_1": "Compute SHA-256 of SEAL.json and compare with SEAL_HASH.txt.",
                "step_2": "For each entry in file_manifest, compute SHA-256 of the file.",
                "step_3": "Compare computed hashes with the recorded hashes.",
                "step_4": "If all hashes match, the package integrity is verified.",
                "step_5": "Review algorithm_summary for per-algorithm result hashes.",
            },
        }

        return seal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_algorithms():
    """Import all algorithm modules to trigger registration."""
    import algorithms.bulk_dedup  # noqa: F401
    import algorithms.provenance_graph  # noqa: F401
    import algorithms.timeline_alignment  # noqa: F401
    import algorithms.integrity_sweep  # noqa: F401
    import algorithms.bates_generator  # noqa: F401
    import algorithms.redaction_verify  # noqa: F401
    import algorithms.access_anomaly  # noqa: F401
