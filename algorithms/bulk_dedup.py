"""
Algorithm A — Bulk Dedup & Near-Dedup (Court-Safe)
====================================================
Identifies duplicate and near-duplicate evidence items within a case.

Modes:
  1. **Exact dedup** — content-hash (SHA-256) equality.
  2. **Near-dedup** — deterministic perceptual fingerprint comparison
     for images and PDF page renders. Uses average-hash (aHash) which
     is fully deterministic: same pixel grid → same hash.

Design constraints:
  - Never deletes originals; only flags relationships.
  - Outputs a "Dedup Report" referencing hashes and similarity scores.
  - All comparisons are explainable (hash equality or Hamming distance).
  - Perceptual hashing is labeled as "assistive" with confidence.
"""

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from algorithms.base import AlgorithmBase, AlgorithmParams, canonical_json, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Deterministic perceptual hash (average hash)
# ---------------------------------------------------------------------------

def _compute_average_hash(image_bytes: bytes, hash_size: int = 8) -> Optional[str]:
    """
    Compute a deterministic average hash (aHash) for an image.

    Algorithm:
      1. Resize image to (hash_size x hash_size) grayscale.
      2. Compute the mean pixel value.
      3. Each bit = 1 if pixel > mean, else 0.
      4. Return hex string.

    This is fully deterministic: same image bytes → same hash.
    Returns None if image cannot be decoded.
    """
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        pixels = list(img.getdata())
        mean_val = sum(pixels) / len(pixels)
        bits = "".join("1" if p > mean_val else "0" for p in pixels)
        # Convert bit string to hex
        hex_str = hex(int(bits, 2))[2:].zfill(hash_size * hash_size // 4)
        return hex_str
    except Exception as exc:
        logger.debug("Perceptual hash failed: %s", exc)
        return None


def _hamming_distance(hash_a: str, hash_b: str) -> int:
    """Compute Hamming distance between two hex hash strings."""
    if len(hash_a) != len(hash_b):
        return -1
    val_a = int(hash_a, 16)
    val_b = int(hash_b, 16)
    xor = val_a ^ val_b
    return bin(xor).count("1")


def _similarity_score(hamming: int, total_bits: int) -> float:
    """Convert Hamming distance to similarity score (0.0–1.0)."""
    if total_bits == 0:
        return 0.0
    return round(1.0 - (hamming / total_bits), 4)


# ---------------------------------------------------------------------------
# Algorithm implementation
# ---------------------------------------------------------------------------

@registry.register
class BulkDedupAlgorithm(AlgorithmBase):
    """Identify exact and near-duplicate evidence within a case."""

    @property
    def algorithm_id(self) -> str:
        return "bulk_dedup"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run dedup analysis on all evidence in a case.

        Params.extra keys:
          - near_dedup (bool): Enable perceptual near-dedup (default True).
          - similarity_threshold (float): Min similarity for near-match (default 0.85).
          - hash_size (int): Perceptual hash grid size (default 8 → 64-bit hash).

        Context keys:
          - db_session: SQLAlchemy session.
          - evidence_store: EvidenceStore instance.

        Returns payload with:
          - exact_duplicates: List of duplicate groups (each is a list of hashes).
          - near_duplicates: List of near-match pairs with scores.
          - total_items: Count of evidence examined.
          - unique_items: Count of unique hashes.
          - dedup_report_hash: SHA-256 of the report.
        """
        db_session = context["db_session"]
        evidence_store = context["evidence_store"]

        near_dedup = params.extra.get("near_dedup", True)
        similarity_threshold = params.extra.get("similarity_threshold", 0.85)
        hash_size = params.extra.get("hash_size", 8)

        # Query evidence for this case with tenant isolation
        from models.evidence import EvidenceItem, CaseEvidence
        from models.legal_case import LegalCase

        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get active evidence links for this case
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
            .all()
        ) if evidence_ids else []

        # --- Exact dedup ---
        hash_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        input_hashes = []

        for item in items:
            h = item.hash_sha256
            if h:
                input_hashes.append(h)
                hash_groups[h].append({
                    "evidence_id": item.id,
                    "original_filename": item.original_filename,
                    "file_type": item.file_type,
                    "hash_sha256": h,
                })

        exact_duplicates = [
            {"hash": h, "count": len(group), "items": group}
            for h, group in hash_groups.items()
            if len(group) > 1
        ]

        # --- Near-dedup (perceptual, images only) ---
        near_duplicates = []
        if near_dedup:
            image_types = {"jpg", "jpeg", "png", "bmp", "tiff", "webp", "gif"}
            image_items = [
                item for item in items
                if item.file_type and item.file_type.lower() in image_types
            ]

            # Compute perceptual hashes
            phashes: List[Tuple[Dict[str, Any], str]] = []
            for item in image_items:
                file_path = evidence_store.get_original_path(item.hash_sha256)
                if not file_path:
                    continue
                try:
                    with open(file_path, "rb") as f:
                        img_bytes = f.read()
                    phash = _compute_average_hash(img_bytes, hash_size)
                    if phash:
                        phashes.append((
                            {
                                "evidence_id": item.id,
                                "original_filename": item.original_filename,
                                "hash_sha256": item.hash_sha256,
                            },
                            phash,
                        ))
                except Exception as exc:
                    logger.debug("Skipping perceptual hash for %s: %s", item.id, exc)

            # Pairwise comparison
            total_bits = hash_size * hash_size
            for i in range(len(phashes)):
                for j in range(i + 1, len(phashes)):
                    dist = _hamming_distance(phashes[i][1], phashes[j][1])
                    if dist < 0:
                        continue
                    score = _similarity_score(dist, total_bits)
                    if score >= similarity_threshold:
                        near_duplicates.append({
                            "item_a": phashes[i][0],
                            "item_b": phashes[j][0],
                            "hamming_distance": dist,
                            "similarity_score": score,
                            "method": "average_hash",
                            "method_label": "assistive",
                            "hash_size_bits": total_bits,
                            "perceptual_hash_a": phashes[i][1],
                            "perceptual_hash_b": phashes[j][1],
                        })

        # Build report
        report = {
            "case_id": params.case_id,
            "total_items": len(items),
            "unique_hashes": len(hash_groups),
            "exact_duplicate_groups": len(exact_duplicates),
            "near_duplicate_pairs": len(near_duplicates),
            "exact_duplicates": exact_duplicates,
            "near_duplicates": near_duplicates,
            "parameters": {
                "near_dedup_enabled": near_dedup,
                "similarity_threshold": similarity_threshold,
                "hash_size": hash_size,
            },
        }
        report_hash = hash_json(report)
        report["dedup_report_hash"] = report_hash

        return {
            **report,
            "output_hashes": [report_hash],
            "input_hashes": input_hashes,
        }
