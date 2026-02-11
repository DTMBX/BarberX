"""
Court-Defensible Evidence Algorithms
======================================
Deterministic, auditable, reproducible algorithms for forensic evidence processing.

All algorithms in this package:
  - Are deterministic: identical inputs + parameters → identical outputs.
  - Never overwrite or mutate original evidence.
  - Produce derivatives that reference the original SHA-256 hash and carry their own.
  - Emit append-only audit events for every run.
  - Label any assistive/ML output with confidence scores and method metadata.
  - Are versioned and registered in a discoverable registry.

Package layout:
  algorithms/
    __init__.py              — This file; public API re-exports.
    base.py                  — AlgorithmBase, AlgorithmResult, AlgorithmParams.
    registry.py              — Discoverable algorithm registry with versioning.
    manifest.py              — Hash-linking and provenance helpers.
    bulk_dedup.py            — (A) Bulk Dedup & Near-Dedup.
    provenance_graph.py      — (B) Provenance Graph Builder.
    timeline_alignment.py    — (C) Cross-Device Timeline Alignment.
    integrity_sweep.py       — (D) Integrity Verification Sweep.
    bates_generator.py       — (E) Bates + Exhibit Set Generator.
    redaction_verify.py      — (F) Redaction Verification.
    access_anomaly.py        — (G) Access Anomaly Detector.
"""

from algorithms.base import AlgorithmBase, AlgorithmResult, AlgorithmParams  # noqa: F401
from algorithms.registry import AlgorithmRegistry, registry  # noqa: F401

__all__ = [
    "AlgorithmBase",
    "AlgorithmResult",
    "AlgorithmParams",
    "AlgorithmRegistry",
    "registry",
]
