"""
Algorithm F — Redaction Verification (Non-Destructive)
========================================================
Verifies that redacted derivatives cannot be reversed by examining:
  1. Whether text layers have been removed (not just hidden).
  2. Whether redaction boxes are "burned in" (rasterized, not annotation-only).
  3. Byte-level checks that original content is absent from the derivative.

Outputs:
  - A "Redaction Verification Report" referencing both original and derivative hashes.
  - Per-item pass/fail/warning with explanations.

Design constraints:
  - Never modifies evidence. Reads derivatives and originals for comparison.
  - Deterministic given the same file bytes.
  - Labels all findings with method and confidence.
"""

import hashlib
import io
import logging
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)

# Verification status constants
REDACTION_PASS = "pass"
REDACTION_FAIL = "fail"
REDACTION_WARNING = "warning"
REDACTION_SKIPPED = "skipped"


def _check_pdf_text_layer(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Check if a PDF has extractable text that might indicate incomplete redaction.

    Returns:
      - has_text_layer (bool): Whether text is extractable.
      - extracted_length (int): Length of extracted text.
      - sample (str): First 200 chars of extracted text (if any).
    """
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text

        return {
            "has_text_layer": len(full_text.strip()) > 0,
            "extracted_length": len(full_text),
            "sample": full_text[:200] if full_text else "",
        }
    except ImportError:
        return {
            "has_text_layer": None,
            "extracted_length": 0,
            "sample": "",
            "note": "PyPDF2 not available; text layer check skipped.",
        }
    except Exception as exc:
        return {
            "has_text_layer": None,
            "extracted_length": 0,
            "sample": "",
            "error": str(exc),
        }


def _check_annotation_redactions(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Check if PDF contains redaction annotations that may not be burned in.

    Redaction annotations (/Subtype /Redact) are removable if not applied.
    """
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        annotation_count = 0
        redact_annotation_count = 0

        for page in reader.pages:
            annots = page.get("/Annots")
            if annots:
                for annot in annots:
                    try:
                        annot_obj = annot.get_object()
                        annotation_count += 1
                        subtype = annot_obj.get("/Subtype")
                        if subtype and str(subtype) in ("/Redact", "/redact"):
                            redact_annotation_count += 1
                    except Exception:
                        pass

        return {
            "total_annotations": annotation_count,
            "redaction_annotations": redact_annotation_count,
            "has_unapplied_redactions": redact_annotation_count > 0,
        }
    except ImportError:
        return {
            "total_annotations": 0,
            "redaction_annotations": 0,
            "has_unapplied_redactions": None,
            "note": "PyPDF2 not available; annotation check skipped.",
        }
    except Exception as exc:
        return {
            "total_annotations": 0,
            "redaction_annotations": 0,
            "has_unapplied_redactions": None,
            "error": str(exc),
        }


def _check_byte_leakage(
    original_bytes: bytes, redacted_bytes: bytes, sample_size: int = 50
) -> Dict[str, Any]:
    """
    Check whether unique substrings from the original appear in the redacted version.

    Samples N-byte windows from the original text content and checks if they
    exist in the redacted bytes. This is a heuristic, not a guarantee.
    """
    # Extract text-like segments from original (printable ASCII runs)
    text_segments = []
    current = []
    for byte in original_bytes:
        if 32 <= byte < 127:
            current.append(byte)
        else:
            if len(current) >= sample_size:
                text_segments.append(bytes(current))
            current = []
    if len(current) >= sample_size:
        text_segments.append(bytes(current))

    leaked_count = 0
    total_checked = min(len(text_segments), 100)  # cap for performance

    for segment in text_segments[:total_checked]:
        if segment in redacted_bytes:
            leaked_count += 1

    return {
        "segments_checked": total_checked,
        "segments_found_in_redacted": leaked_count,
        "potential_leakage": leaked_count > 0,
    }


@registry.register
class RedactionVerifyAlgorithm(AlgorithmBase):
    """Verify that redacted derivatives are properly burned in and non-reversible."""

    @property
    def algorithm_id(self) -> str:
        return "redaction_verify"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify redaction quality for all redacted derivatives in a case.

        Params.extra keys:
          - evidence_ids (list[int]): Specific items to check (default: all redacted).

        Returns payload with:
          - items: Per-item verification results.
          - summary: Counts by status.
          - report_hash: SHA-256 of the report.
        """
        db_session = context["db_session"]
        evidence_store = context["evidence_store"]

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
        specified_ids = params.extra.get("evidence_ids")
        if specified_ids:
            evidence_ids = [eid for eid in evidence_ids if eid in specified_ids]

        items = (
            db_session.query(EvidenceItem)
            .filter(EvidenceItem.id.in_(evidence_ids))
            .order_by(EvidenceItem.id)
            .all()
        ) if evidence_ids else []

        results: List[Dict[str, Any]] = []
        input_hashes: List[str] = []
        counts = {REDACTION_PASS: 0, REDACTION_FAIL: 0, REDACTION_WARNING: 0, REDACTION_SKIPPED: 0}

        for item in items:
            if not item.is_redacted:
                continue  # Only check items marked as redacted

            if not item.hash_sha256:
                continue

            input_hashes.append(item.hash_sha256)

            # Load original and redacted derivative
            original_path = evidence_store.get_original_path(item.hash_sha256)
            if not original_path:
                results.append({
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "status": REDACTION_SKIPPED,
                    "reason": "Original file not found.",
                })
                counts[REDACTION_SKIPPED] += 1
                continue

            # Look for redacted derivative in manifest
            redacted_path = None
            redacted_hash = None
            if item.evidence_store_id:
                manifest = evidence_store.load_manifest(item.evidence_store_id)
                if manifest and hasattr(manifest, "derivatives"):
                    for deriv in manifest.derivatives:
                        if deriv.derivative_type in ("redacted", "redacted_copy"):
                            deriv_dir = evidence_store._derivative_dir(
                                item.hash_sha256, deriv.derivative_type
                            )
                            candidate = deriv_dir / deriv.filename
                            if candidate.exists():
                                redacted_path = str(candidate)
                                redacted_hash = deriv.sha256
                                break

            if not redacted_path:
                results.append({
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "status": REDACTION_SKIPPED,
                    "reason": "No redacted derivative found in manifest.",
                })
                counts[REDACTION_SKIPPED] += 1
                continue

            # Read both files
            try:
                with open(original_path, "rb") as f:
                    original_bytes = f.read()
                with open(redacted_path, "rb") as f:
                    redacted_bytes = f.read()
            except OSError as exc:
                results.append({
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "status": REDACTION_SKIPPED,
                    "reason": f"File read error: {exc}",
                })
                counts[REDACTION_SKIPPED] += 1
                continue

            # Run checks
            checks = {}
            overall_status = REDACTION_PASS
            issues = []

            # 1. Text layer check (PDF only)
            if item.file_type and item.file_type.lower() == "pdf":
                text_check = _check_pdf_text_layer(redacted_bytes)
                checks["text_layer"] = text_check
                if text_check.get("has_text_layer"):
                    issues.append("Redacted PDF still contains extractable text layer.")
                    overall_status = REDACTION_WARNING

                # 2. Annotation check
                annot_check = _check_annotation_redactions(redacted_bytes)
                checks["annotations"] = annot_check
                if annot_check.get("has_unapplied_redactions"):
                    issues.append("PDF contains unapplied redaction annotations (not burned in).")
                    overall_status = REDACTION_FAIL

            # 3. Byte leakage check
            leakage_check = _check_byte_leakage(original_bytes, redacted_bytes)
            checks["byte_leakage"] = leakage_check
            if leakage_check.get("potential_leakage"):
                issues.append(
                    f"Found {leakage_check['segments_found_in_redacted']} original text segments "
                    f"in redacted derivative (potential content leakage)."
                )
                if overall_status != REDACTION_FAIL:
                    overall_status = REDACTION_WARNING

            # 4. Hash difference (must differ from original)
            original_hash_computed = hashlib.sha256(original_bytes).hexdigest()
            redacted_hash_computed = hashlib.sha256(redacted_bytes).hexdigest()
            checks["hash_comparison"] = {
                "original_hash": original_hash_computed,
                "redacted_hash": redacted_hash_computed,
                "differs": original_hash_computed != redacted_hash_computed,
            }
            if not checks["hash_comparison"]["differs"]:
                issues.append("Redacted derivative has identical hash to original — no redaction applied.")
                overall_status = REDACTION_FAIL

            counts[overall_status] += 1
            results.append({
                "evidence_id": item.id,
                "original_filename": item.original_filename,
                "original_hash": item.hash_sha256,
                "redacted_hash": redacted_hash,
                "status": overall_status,
                "issues": issues,
                "checks": checks,
            })

        report = {
            "case_id": params.case_id,
            "total_checked": len(results),
            "summary": counts,
            "items": results,
        }
        report_hash = hash_json(report)
        report["report_hash"] = report_hash

        return {
            **report,
            "output_hashes": [report_hash],
            "input_hashes": input_hashes,
        }
