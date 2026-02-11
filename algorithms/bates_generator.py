"""
Algorithm E — Bates + Exhibit Set Generator
=============================================
Generates Bates-stamped working copies and exhibit bundles as derivatives.

Outputs:
  - Bates-numbered derivative copies (PDF or images) with their own hashes.
  - An exhibit manifest with deterministic naming.
  - Provenance links from each derivative back to its original.

Design constraints:
  - Originals are NEVER modified. Stamped copies are stored as derivatives.
  - Each derivative carries its own SHA-256 and references the original hash.
  - Bates numbering is deterministic given (case, prefix, start number, sort order).
  - All parameters are recorded for reproducibility.
"""

import hashlib
import io
import logging
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.manifest import build_derivative_record
from algorithms.registry import registry

logger = logging.getLogger(__name__)


def _stamp_text_on_pdf_bytes(
    pdf_bytes: bytes,
    bates_number: str,
    position: str = "bottom_right",
) -> bytes:
    """
    Burn a Bates number onto each page of a PDF.

    Returns new PDF bytes. If PDF manipulation libraries are unavailable,
    returns a minimal text-wrapped derivative.

    This is deterministic: same input bytes + bates_number → same output.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas as rl_canvas
        from PyPDF2 import PdfReader, PdfWriter

        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()

        for page in reader.pages:
            # Create stamp overlay
            packet = io.BytesIO()
            c = rl_canvas.Canvas(packet, pagesize=letter)
            c.setFont("Courier", 9)
            if position == "bottom_right":
                c.drawString(450, 20, bates_number)
            else:
                c.drawString(50, 20, bates_number)
            c.save()
            packet.seek(0)

            stamp_reader = PdfReader(packet)
            page.merge_page(stamp_reader.pages[0])
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    except Exception:
        # Fallback: produce a simple text-marker derivative when PDF
        # stamping libraries are unavailable or the input is not valid PDF.
        logger.info(
            "PDF stamping unavailable or input not valid PDF; "
            "producing text-marker derivative."
        )
        marker = f"[BATES: {bates_number}]\n".encode("utf-8")
        return marker + pdf_bytes


def _generate_bates_number(prefix: str, number: int, width: int = 6) -> str:
    """Generate a deterministic Bates number string. e.g., 'EVIDENT-000001'."""
    return f"{prefix}-{str(number).zfill(width)}"


@registry.register
class BatesGeneratorAlgorithm(AlgorithmBase):
    """Generate Bates-stamped derivatives and exhibit bundles for court production."""

    @property
    def algorithm_id(self) -> str:
        return "bates_generator"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Bates-numbered derivative copies for case evidence.

        Params.extra keys:
          - prefix (str): Bates prefix (default: "EVD").
          - start_number (int): Starting Bates number (default: 1).
          - number_width (int): Zero-pad width (default: 6).
          - stamp_position (str): "bottom_right" or "bottom_left".

        Returns payload with:
          - exhibits: List of exhibit records with bates numbers and hashes.
          - manifest: Exhibit bundle manifest.
          - manifest_hash: SHA-256 of the manifest.
        """
        db_session = context["db_session"]
        evidence_store = context["evidence_store"]

        prefix = params.extra.get("prefix", "EVD")
        start_number = params.extra.get("start_number", 1)
        number_width = params.extra.get("number_width", 6)
        stamp_position = params.extra.get("stamp_position", "bottom_right")

        from models.evidence import EvidenceItem, CaseEvidence
        from models.legal_case import LegalCase

        # Tenant isolation
        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get case evidence, sorted by ID for determinism
        links = (
            db_session.query(CaseEvidence)
            .filter_by(case_id=params.case_id)
            .filter(CaseEvidence.unlinked_at.is_(None))
            .all()
        )
        evidence_ids = sorted([link.evidence_id for link in links])

        items = (
            db_session.query(EvidenceItem)
            .filter(EvidenceItem.id.in_(evidence_ids))
            .order_by(EvidenceItem.id)
            .all()
        ) if evidence_ids else []

        exhibits: List[Dict[str, Any]] = []
        derivative_records: List[Dict[str, Any]] = []
        input_hashes: List[str] = []
        output_hashes: List[str] = []
        current_number = start_number

        for item in items:
            if not item.hash_sha256:
                continue

            input_hashes.append(item.hash_sha256)
            bates_number = _generate_bates_number(prefix, current_number, number_width)

            # Read original file
            file_path = evidence_store.get_original_path(item.hash_sha256)
            if not file_path:
                exhibits.append({
                    "bates_number": bates_number,
                    "evidence_id": item.id,
                    "original_hash": item.hash_sha256,
                    "original_filename": item.original_filename,
                    "status": "skipped",
                    "reason": "Original file not found on disk.",
                })
                current_number += 1
                continue

            try:
                with open(file_path, "rb") as f:
                    original_bytes = f.read()
            except OSError as exc:
                exhibits.append({
                    "bates_number": bates_number,
                    "evidence_id": item.id,
                    "original_hash": item.hash_sha256,
                    "original_filename": item.original_filename,
                    "status": "error",
                    "reason": str(exc),
                })
                current_number += 1
                continue

            # Stamp the derivative
            if item.file_type and item.file_type.lower() == "pdf":
                stamped_bytes = _stamp_text_on_pdf_bytes(
                    original_bytes, bates_number, stamp_position
                )
            else:
                # For non-PDF, prepend bates marker to a copy
                marker = f"[BATES: {bates_number}]\n".encode("utf-8")
                stamped_bytes = marker + original_bytes

            derivative_hash = hashlib.sha256(stamped_bytes).hexdigest()
            output_hashes.append(derivative_hash)

            # Store as derivative
            deriv_filename = f"{bates_number}_{item.original_filename}"
            try:
                evidence_store.store_derivative(
                    evidence_id=item.evidence_store_id,
                    derivative_type="bates_stamped",
                    filename=deriv_filename,
                    data=stamped_bytes,
                    parameters={
                        "bates_number": bates_number,
                        "stamp_position": stamp_position,
                        "algorithm": self.algorithm_id,
                        "algorithm_version": self.algorithm_version,
                    },
                )
            except Exception as exc:
                logger.warning("Failed to store derivative for %s: %s", item.id, exc)

            exhibits.append({
                "bates_number": bates_number,
                "evidence_id": item.id,
                "original_hash": item.hash_sha256,
                "derivative_hash": derivative_hash,
                "original_filename": item.original_filename,
                "derivative_filename": deriv_filename,
                "size_bytes": len(stamped_bytes),
                "status": "generated",
            })

            derivative_records.append(
                build_derivative_record(
                    original_hash=item.hash_sha256,
                    derivative_bytes=stamped_bytes,
                    derivative_type="bates_stamped",
                    algorithm_id=self.algorithm_id,
                    algorithm_version=self.algorithm_version,
                    run_id=params.extra.get("run_id", ""),
                    parameters={"bates_number": bates_number},
                )
            )
            current_number += 1

        # Build manifest
        manifest = {
            "case_id": params.case_id,
            "prefix": prefix,
            "start_number": start_number,
            "end_number": current_number - 1,
            "total_exhibits": len(exhibits),
            "generated_count": sum(1 for e in exhibits if e.get("status") == "generated"),
            "skipped_count": sum(1 for e in exhibits if e.get("status") == "skipped"),
            "error_count": sum(1 for e in exhibits if e.get("status") == "error"),
            "exhibits": exhibits,
            "parameters": {
                "prefix": prefix,
                "start_number": start_number,
                "number_width": number_width,
                "stamp_position": stamp_position,
            },
        }
        manifest_hash = hash_json(manifest)
        manifest["manifest_hash"] = manifest_hash

        return {
            **manifest,
            "output_hashes": output_hashes + [manifest_hash],
            "input_hashes": input_hashes,
        }
