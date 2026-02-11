"""
Deterministic Replay Harness
==============================
Re-runs all previously recorded algorithm runs for a case using the exact
stored parameters and compares outputs to the stored result hashes.

If all hashes match → provable reproducibility.
If any hash differs → a verification delta report is emitted.

Design constraints:
  - Uses only stored AlgorithmRun records as the replay manifest.
  - Each replay run uses the same algorithm_id, algorithm_version, and
    params_hash that was recorded at the original execution time.
  - The replay result is an independent artifact: it does not overwrite
    or modify the original run record.
  - All findings are deterministic: identical evidence → identical verdict.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmParams, AlgorithmResult, canonical_json, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ReplayVerdict:
    """Comparison result for a single replayed algorithm run."""
    original_run_id: str
    algorithm_id: str
    algorithm_version: str
    original_result_hash: str
    replay_result_hash: str
    match: bool
    original_params_hash: str
    replay_params_hash: str
    params_match: bool
    original_integrity_check: str
    replay_integrity_check: str
    integrity_match: bool
    replay_success: bool
    replay_error: Optional[str] = None
    delta_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplayReport:
    """Full replay report for a case."""
    case_id: int
    tenant_id: int
    replayed_at: str
    total_runs: int
    matched: int
    mismatched: int
    skipped: int
    errors: int
    all_reproducible: bool
    verdicts: List[ReplayVerdict]
    report_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def finalize(self) -> "ReplayReport":
        """Compute and set the report_hash."""
        d = self.to_dict()
        d.pop("report_hash", None)
        self.report_hash = hash_json(d)
        return self


# ---------------------------------------------------------------------------
# Replay engine
# ---------------------------------------------------------------------------

class ReplayEngine:
    """
    Re-executes recorded algorithm runs and compares outputs.

    Usage:
        engine = ReplayEngine()
        report = engine.replay_case(
            case_id=42,
            tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
        )
    """

    def replay_case(
        self,
        case_id: int,
        tenant_id: int,
        db_session,
        evidence_store,
        audit_stream=None,
        algorithm_filter: Optional[List[str]] = None,
    ) -> ReplayReport:
        """
        Replay all recorded algorithm runs for a case.

        Args:
            case_id: Target case.
            tenant_id: Organization ID for tenant isolation.
            db_session: SQLAlchemy session.
            evidence_store: EvidenceStore instance.
            audit_stream: Optional AuditStream for logging replay events.
            algorithm_filter: If set, only replay these algorithm IDs.

        Returns:
            ReplayReport with per-run verdicts and aggregate summary.
        """
        from models.algorithm_models import AlgorithmRun

        # Ensure all algorithms are registered
        _ensure_algorithms()

        # Fetch original runs, ordered by creation time
        query = (
            AlgorithmRun.query
            .filter_by(case_id=case_id)
            .filter_by(success=True)
            .order_by(AlgorithmRun.created_at.asc())
        )
        if algorithm_filter:
            query = query.filter(AlgorithmRun.algorithm_id.in_(algorithm_filter))

        original_runs = query.all()

        verdicts: List[ReplayVerdict] = []
        matched = 0
        mismatched = 0
        skipped = 0
        errors = 0

        context = {
            "db_session": db_session,
            "evidence_store": evidence_store,
            "audit_stream": audit_stream,
        }

        for run in original_runs:
            verdict = self._replay_single_run(run, context)
            verdicts.append(verdict)

            if verdict.replay_error:
                errors += 1
            elif verdict.match:
                matched += 1
            else:
                mismatched += 1

        report = ReplayReport(
            case_id=case_id,
            tenant_id=tenant_id,
            replayed_at=datetime.now(timezone.utc).isoformat(),
            total_runs=len(original_runs),
            matched=matched,
            mismatched=mismatched,
            skipped=skipped,
            errors=errors,
            all_reproducible=(mismatched == 0 and errors == 0),
            verdicts=verdicts,
        )
        report.finalize()

        # Emit audit event for the replay
        if audit_stream:
            self._emit_replay_audit(report, audit_stream, case_id, tenant_id)

        return report

    def _replay_single_run(
        self,
        original_run,
        context: Dict[str, Any],
    ) -> ReplayVerdict:
        """Replay a single algorithm run and compare hashes."""
        algo = registry.get(original_run.algorithm_id, original_run.algorithm_version)
        if not algo:
            return ReplayVerdict(
                original_run_id=original_run.run_id,
                algorithm_id=original_run.algorithm_id,
                algorithm_version=original_run.algorithm_version,
                original_result_hash=original_run.result_hash or "",
                replay_result_hash="",
                match=False,
                original_params_hash=original_run.params_hash or "",
                replay_params_hash="",
                params_match=False,
                original_integrity_check=original_run.integrity_check or "",
                replay_integrity_check="",
                integrity_match=False,
                replay_success=False,
                replay_error=f"Algorithm {original_run.algorithm_id} v{original_run.algorithm_version} not found in registry.",
            )

        # Reconstruct params from stored data
        try:
            params_dict = json.loads(original_run.payload_json or "{}").get("_params", None)
            if params_dict is None:
                # Reconstruct from run record fields
                params = AlgorithmParams(
                    case_id=original_run.case_id,
                    tenant_id=original_run.tenant_id or 1,
                    actor_id=original_run.actor_id,
                    actor_name="replay",
                    extra={},
                )
            else:
                params = AlgorithmParams(**params_dict)
        except Exception:
            params = AlgorithmParams(
                case_id=original_run.case_id,
                tenant_id=original_run.tenant_id or 1,
                actor_id=original_run.actor_id,
                actor_name="replay",
                extra={},
            )

        # Execute the replay
        try:
            result = algo.run(params, context)
        except Exception as exc:
            return ReplayVerdict(
                original_run_id=original_run.run_id,
                algorithm_id=original_run.algorithm_id,
                algorithm_version=original_run.algorithm_version,
                original_result_hash=original_run.result_hash or "",
                replay_result_hash="",
                match=False,
                original_params_hash=original_run.params_hash or "",
                replay_params_hash="",
                params_match=False,
                original_integrity_check=original_run.integrity_check or "",
                replay_integrity_check="",
                integrity_match=False,
                replay_success=False,
                replay_error=str(exc),
            )

        # Compare hashes
        result_match = (original_run.result_hash or "") == result.result_hash
        params_match = (original_run.params_hash or "") == result.params_hash
        integrity_match = (original_run.integrity_check or "") == result.integrity_check

        delta = {}
        if not result_match:
            delta["result_hash_original"] = original_run.result_hash
            delta["result_hash_replay"] = result.result_hash
        if not integrity_match:
            delta["integrity_original"] = original_run.integrity_check
            delta["integrity_replay"] = result.integrity_check

        return ReplayVerdict(
            original_run_id=original_run.run_id,
            algorithm_id=original_run.algorithm_id,
            algorithm_version=original_run.algorithm_version,
            original_result_hash=original_run.result_hash or "",
            replay_result_hash=result.result_hash,
            match=result_match,
            original_params_hash=original_run.params_hash or "",
            replay_params_hash=result.params_hash,
            params_match=params_match,
            original_integrity_check=original_run.integrity_check or "",
            replay_integrity_check=result.integrity_check,
            integrity_match=integrity_match,
            replay_success=result.success,
            replay_error=result.error,
            delta_details=delta,
        )

    @staticmethod
    def _emit_replay_audit(
        report: ReplayReport,
        audit_stream,
        case_id: int,
        tenant_id: int,
    ) -> None:
        """Emit an audit event recording the replay execution."""
        try:
            audit_stream.record(
                evidence_id=str(case_id),
                action="replay.completed",
                actor_id=None,
                actor_name="replay_engine",
                details={
                    "case_id": case_id,
                    "tenant_id": tenant_id,
                    "total_runs": report.total_runs,
                    "matched": report.matched,
                    "mismatched": report.mismatched,
                    "errors": report.errors,
                    "all_reproducible": report.all_reproducible,
                    "report_hash": report.report_hash,
                },
            )
        except Exception as exc:
            logger.warning("Failed to emit replay audit: %s", exc)


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
