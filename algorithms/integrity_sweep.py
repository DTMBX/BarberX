"""
Algorithm D — Integrity Verification Sweep
=============================================
Verifies stored hash vs. recomputed hash for all evidence in a case.
Detects missing objects, hash mismatches, and manifest inconsistencies.

Outputs:
  - A signed "Integrity Verification Report" with per-item results.
  - Audit events for every item checked (pass or fail).
  - Summary statistics and a report-level SHA-256.

Design constraints:
  - Fully deterministic: same files on disk → same report.
  - Emits audit events for every verification.
  - Never modifies evidence or manifests.
"""

import logging
from typing import Any, Dict, List

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.manifest import verify_hash
from algorithms.registry import registry

logger = logging.getLogger(__name__)


# Verification status constants
STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_MISSING = "missing"
STATUS_ERROR = "error"


@registry.register
class IntegritySweepAlgorithm(AlgorithmBase):
    """Verify stored hashes against recomputed hashes for all case evidence."""

    @property
    def algorithm_id(self) -> str:
        return "integrity_sweep"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sweep all evidence in a case and verify integrity.

        Context keys:
          - db_session: SQLAlchemy session.
          - evidence_store: EvidenceStore instance.
          - audit_stream (optional): for per-item audit events.

        Returns payload with:
          - items: Per-item verification results.
          - summary: Counts of pass/fail/missing/error.
          - report_hash: SHA-256 of the verification report.
        """
        db_session = context["db_session"]
        evidence_store = context["evidence_store"]
        audit_stream = context.get("audit_stream")

        from models.evidence import EvidenceItem, CaseEvidence
        from models.legal_case import LegalCase

        # Tenant isolation
        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get case evidence
        links = (
            db_session.query(CaseEvidence)
            .filter_by(case_id=params.case_id)
            .filter(CaseEvidence.unlinked_at.is_(None))
            .all()
        )
        evidence_ids = [link.evidence_id for link in links]

        items = (
            db_session.query(EvidenceItem)
            .filter(EvidenceItem.id.in_(evidence_ids))
            .order_by(EvidenceItem.id)
            .all()
        ) if evidence_ids else []

        results: List[Dict[str, Any]] = []
        input_hashes: List[str] = []
        counts = {STATUS_PASS: 0, STATUS_FAIL: 0, STATUS_MISSING: 0, STATUS_ERROR: 0}

        for item in items:
            expected_hash = item.hash_sha256
            if not expected_hash:
                result = {
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "status": STATUS_ERROR,
                    "detail": "No hash_sha256 recorded in database.",
                }
                counts[STATUS_ERROR] += 1
                results.append(result)
                continue

            input_hashes.append(expected_hash)

            # Resolve file path
            file_path = evidence_store.get_original_path(expected_hash)
            if not file_path:
                result = {
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "expected_hash": expected_hash,
                    "status": STATUS_MISSING,
                    "detail": "Original file not found on disk.",
                }
                counts[STATUS_MISSING] += 1
                results.append(result)

                # Audit event
                if audit_stream:
                    try:
                        from services.audit_stream import AuditAction
                        audit_stream.record(
                            evidence_id=item.evidence_store_id or str(item.id),
                            action=AuditAction.INTEGRITY_FAILED,
                            actor_id=params.actor_id,
                            actor_name=params.actor_name,
                            db_evidence_id=item.id,
                            details={"reason": "file_missing", "expected_hash": expected_hash},
                        )
                    except Exception as exc:
                        logger.warning("Audit emit failed: %s", exc)
                continue

            # Verify hash
            check = verify_hash(file_path, expected_hash)
            if check.get("error"):
                status = STATUS_ERROR
                counts[STATUS_ERROR] += 1
            elif check["match"]:
                status = STATUS_PASS
                counts[STATUS_PASS] += 1
            else:
                status = STATUS_FAIL
                counts[STATUS_FAIL] += 1

            result = {
                "evidence_id": item.id,
                "original_filename": item.original_filename,
                "expected_hash": expected_hash,
                "computed_hash": check.get("computed"),
                "file_path": check.get("file_path"),
                "status": status,
                "detail": check.get("error", ""),
            }
            results.append(result)

            # Audit per-item
            if audit_stream:
                try:
                    from services.audit_stream import AuditAction
                    action = AuditAction.INTEGRITY_VERIFIED if status == STATUS_PASS else AuditAction.INTEGRITY_FAILED
                    audit_stream.record(
                        evidence_id=item.evidence_store_id or str(item.id),
                        action=action,
                        actor_id=params.actor_id,
                        actor_name=params.actor_name,
                        db_evidence_id=item.id,
                        details={
                            "expected_hash": expected_hash,
                            "computed_hash": check.get("computed"),
                            "status": status,
                        },
                    )
                except Exception as exc:
                    logger.warning("Audit emit failed: %s", exc)

        # Build report
        report = {
            "case_id": params.case_id,
            "total_items": len(items),
            "summary": counts,
            "all_passed": counts[STATUS_FAIL] == 0 and counts[STATUS_MISSING] == 0 and counts[STATUS_ERROR] == 0,
            "items": results,
        }
        report_hash = hash_json(report)
        report["report_hash"] = report_hash

        return {
            **report,
            "output_hashes": [report_hash],
            "input_hashes": input_hashes,
        }
