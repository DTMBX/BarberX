"""
Evidence Manifest Helpers
==========================
Utilities for hash-linking, provenance tracking, and derivative chain management.

All functions are pure / side-effect-free unless explicitly noted.
They operate on data structures, not database sessions.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from algorithms.base import canonical_json, hash_json

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provenance edge
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProvenanceEdge:
    """
    A directed edge in the provenance graph.

    source_hash → target_hash via a transformation.
    """
    source_hash: str          # SHA-256 of the input object
    target_hash: str          # SHA-256 of the output object
    transformation: str       # e.g. "bates_stamp", "redaction", "thumbnail"
    algorithm_id: str         # which algorithm produced this edge
    algorithm_version: str
    run_id: str               # UUID of the algorithm run
    created_at: str           # ISO-8601 UTC
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Manifest stamping
# ---------------------------------------------------------------------------

def compute_manifest_hash(manifest_entries: List[Dict[str, Any]]) -> str:
    """
    Compute a single SHA-256 over an ordered list of manifest entries.

    This creates a Merkle-like commitment: altering any entry changes the hash.
    """
    return hash_json(manifest_entries)


def build_derivative_record(
    original_hash: str,
    derivative_bytes: bytes,
    derivative_type: str,
    algorithm_id: str,
    algorithm_version: str,
    run_id: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a derivative record linking a derived artifact to its original.

    Args:
        original_hash: SHA-256 of the original evidence.
        derivative_bytes: Raw bytes of the derivative.
        derivative_type: Type label (e.g. "bates_stamped", "redacted_copy").
        algorithm_id: Algorithm that produced the derivative.
        algorithm_version: Version of that algorithm.
        run_id: UUID of the algorithm run.
        parameters: Recorded algorithm parameters.

    Returns:
        Dict with all provenance fields and the derivative's SHA-256.
    """
    derivative_hash = hashlib.sha256(derivative_bytes).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    return {
        "original_hash": original_hash,
        "derivative_hash": derivative_hash,
        "derivative_type": derivative_type,
        "size_bytes": len(derivative_bytes),
        "algorithm_id": algorithm_id,
        "algorithm_version": algorithm_version,
        "run_id": run_id,
        "parameters": parameters or {},
        "created_at": now,
    }


def verify_hash(file_path: str, expected_hash: str) -> Dict[str, Any]:
    """
    Recompute SHA-256 of a file and compare against expected hash.

    Returns:
        Dict with 'match' (bool), 'expected', 'computed', 'file_path'.
    """
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        computed = h.hexdigest()
    except (FileNotFoundError, OSError) as exc:
        return {
            "match": False,
            "expected": expected_hash,
            "computed": None,
            "file_path": file_path,
            "error": str(exc),
        }

    return {
        "match": computed == expected_hash,
        "expected": expected_hash,
        "computed": computed,
        "file_path": file_path,
    }


def link_provenance(
    source_hash: str,
    target_hash: str,
    transformation: str,
    algorithm_id: str,
    algorithm_version: str,
    run_id: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> ProvenanceEdge:
    """Create a provenance edge linking source to target."""
    return ProvenanceEdge(
        source_hash=source_hash,
        target_hash=target_hash,
        transformation=transformation,
        algorithm_id=algorithm_id,
        algorithm_version=algorithm_version,
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        parameters=parameters or {},
    )
