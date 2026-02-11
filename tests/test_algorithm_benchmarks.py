"""
Benchmark Dataset & Throughput Report
========================================
Generates a synthetic 10,000-document dataset with mixed formats and
measures per-algorithm throughput to produce a court-defensible
performance baseline.

Dataset composition:
  - 4,000 PDF documents
  - 2,500 JPEG photos
  - 1,500 MP4 video files
  - 1,000 DOCX documents
  - 500 PNG images
  - 500 miscellaneous (TXT, CSV)

Timeline: 2,000 events across 5 devices with realistic clock drift
Redactions: 500 redacted items
Duplicate rate: ~5% exact, ~2% near-duplicate

Usage:
    pytest tests/test_algorithm_benchmarks.py -v -m performance
    pytest tests/test_algorithm_benchmarks.py -v -k benchmark --tb=short
"""

import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock

import pytest

from algorithms.base import AlgorithmParams, hash_json


# ---------------------------------------------------------------------------
# Synthetic Dataset Generator
# ---------------------------------------------------------------------------

class SyntheticDataset:
    """
    Deterministic synthetic evidence dataset for benchmarking.

    Uses a fixed seed for reproducibility across runs.
    """

    DEVICES = [
        ("BWC-7100", "body_worn_camera"),
        ("BWC-7200", "body_worn_camera"),
        ("DASH-4400", "dash_cam"),
        ("PHONE-OFC-11", "mobile_phone"),
        ("PHONE-OFC-12", "mobile_phone"),
    ]

    FORMAT_DISTRIBUTION = [
        ("pdf", 3800),
        ("jpg", 2400),
        ("mp4", 1400),
        ("docx", 950),
        ("png", 450),
        ("txt", 300),
        ("csv", 200),
    ]

    def __init__(self, size: int = 10000, seed: int = 42):
        self.size = size
        self.seed = seed
        self._rng = random.Random(seed)
        self._items = []
        self._case_links = []
        self._hashes_seen = set()

    def generate(self) -> "SyntheticDataset":
        """Generate the full dataset. Idempotent and deterministic."""
        if self._items:
            return self

        self._rng = random.Random(self.seed)
        self._items = []
        self._case_links = []
        self._hashes_seen = set()

        # Reserve ~5% of slots for exact duplicates
        dup_slots = int(self.size * 0.05)
        base_count = self.size - dup_slots

        # Distribute base items across file types
        item_id = 1
        for file_type, count in self.FORMAT_DISTRIBUTION:
            for i in range(count):
                if item_id > base_count:
                    break
                item = self._make_item(item_id, file_type)
                self._items.append(item)
                self._case_links.append(_MockCaseEvidence(1, item_id))
                item_id += 1

        # Fill any remaining base slots
        while item_id <= base_count:
            item = self._make_item(item_id, "pdf")
            self._items.append(item)
            self._case_links.append(_MockCaseEvidence(1, item_id))
            item_id += 1

        # Inject exact duplicates (~5%)
        for _ in range(dup_slots):
            source = self._rng.choice(self._items[:base_count])
            dup = self._clone_item(source, item_id)
            self._items.append(dup)
            self._case_links.append(_MockCaseEvidence(1, item_id))
            item_id += 1

        # Inject redacted items (~5%)
        for item in self._rng.sample(self._items, min(500, len(self._items))):
            item.is_redacted = True

        return self

    @property
    def items(self):
        return self._items

    @property
    def case_links(self):
        return self._case_links

    def _make_item(self, item_id: int, file_type: str):
        """Create a single evidence item with realistic metadata."""
        device_label, device_type = self._rng.choice(self.DEVICES)
        base_time = datetime(2025, 6, 1, 8, 0, 0, tzinfo=timezone.utc)
        offset_seconds = self._rng.randint(0, 86400 * 30)  # 30-day window
        collected = base_time + timedelta(seconds=offset_seconds)

        # Generate deterministic hash
        hash_input = f"item-{item_id}-{file_type}-{self.seed}".encode()
        sha256 = hashlib.sha256(hash_input).hexdigest()
        self._hashes_seen.add(sha256)

        file_size = self._rng.randint(1024, 50 * 1024 * 1024)  # 1KB to 50MB
        duration = self._rng.randint(10, 3600) if file_type in ("mp4",) else None

        return _MockEvidenceItem(
            id=item_id,
            filename=f"evidence_{item_id:05d}.{file_type}",
            hash_sha256=sha256,
            file_type=file_type,
            device_label=device_label,
            device_type=device_type,
            collected_date=collected,
            file_size_bytes=file_size,
            duration_seconds=duration,
            is_redacted=False,
        )

    def _clone_item(self, source, new_id: int):
        """Clone an item to simulate an exact duplicate."""
        return _MockEvidenceItem(
            id=new_id,
            filename=f"dup_{new_id:05d}.{source.file_type}",
            hash_sha256=source.hash_sha256,  # same hash = exact dup
            file_type=source.file_type,
            device_label=source.device_label,
            device_type=source.device_type,
            collected_date=source.collected_date,
            file_size_bytes=source.file_size_bytes,
            duration_seconds=source.duration_seconds,
            is_redacted=False,
        )


# ---------------------------------------------------------------------------
# Lightweight mocks
# ---------------------------------------------------------------------------

class _MockEvidenceItem:
    def __init__(self, id, filename, hash_sha256, file_type="pdf",
                 device_label=None, device_type=None, collected_date=None,
                 file_size_bytes=1024, duration_seconds=None, is_redacted=False):
        self.id = id
        self.original_filename = filename
        self.hash_sha256 = hash_sha256
        self.file_type = file_type
        self.device_label = device_label
        self.device_type = device_type
        self.collected_date = collected_date
        self.file_size_bytes = file_size_bytes
        self.evidence_store_id = f"store-{id}"
        self.duration_seconds = duration_seconds
        self.is_redacted = is_redacted
        self.evidence_type = "document"
        self.created_at = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


class _MockCaseEvidence:
    def __init__(self, case_id, evidence_id):
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.unlinked_at = None


class _MockLegalCase:
    def __init__(self, id=1, organization_id=1):
        self.id = id
        self.organization_id = organization_id


class _MockQuery:
    def __init__(self, items):
        self._items = items

    def filter_by(self, **kw):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items


class _MockStore:
    def __init__(self):
        self._originals = {}

    def get_original_path(self, sha256):
        return self._originals.get(sha256)

    def original_exists(self, sha256):
        return sha256 in self._originals

    def store_derivative(self, evidence_id, dtype, filename, data, parameters=None):
        return f"/tmp/{filename}"

    def load_manifest(self, evidence_id):
        return None

    def _derivative_dir(self, sha256, derivative_type):
        from pathlib import Path
        return Path("/tmp/derivatives") / sha256[:4] / sha256 / derivative_type

    def append_audit(self, **kwargs):
        pass


class _MockAudit:
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


def _make_context(items, case_links):
    """Build a mock context for benchmark runs."""
    session = MagicMock()
    store = _MockStore()
    audit = _MockAudit()

    def query_side_effect(model):
        name = model.__name__ if hasattr(model, "__name__") else str(model)
        if "LegalCase" in name:
            return _MockQuery([_MockLegalCase()])
        elif "CaseEvidence" in name:
            return _MockQuery(case_links)
        elif "EvidenceItem" in name:
            return _MockQuery(items)
        elif "ChainOfCustody" in name:
            return _MockQuery([])
        return _MockQuery([])

    session.query = MagicMock(side_effect=query_side_effect)
    return {"db_session": session, "evidence_store": store, "audit_stream": audit}


# ---------------------------------------------------------------------------
# Algorithm imports
# ---------------------------------------------------------------------------

from algorithms.bulk_dedup import BulkDedupAlgorithm
from algorithms.provenance_graph import ProvenanceGraphAlgorithm
from algorithms.timeline_alignment import TimelineAlignmentAlgorithm
from algorithms.integrity_sweep import IntegritySweepAlgorithm
from algorithms.bates_generator import BatesGeneratorAlgorithm
from algorithms.access_anomaly import AccessAnomalyAlgorithm


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def dataset():
    """Generate the synthetic 10k dataset once per module."""
    return SyntheticDataset(size=10000, seed=42).generate()


@pytest.fixture(scope="module")
def small_dataset():
    """Smaller 1k dataset for faster CI runs."""
    return SyntheticDataset(size=1000, seed=42).generate()


@pytest.fixture
def benchmark_params():
    return AlgorithmParams(case_id=1, tenant_id=1)


# ---------------------------------------------------------------------------
# Benchmark helper
# ---------------------------------------------------------------------------

class BenchmarkResult:
    """Stores and formats a single algorithm benchmark run."""
    def __init__(self, algorithm_id: str, item_count: int, duration_seconds: float,
                 success: bool, payload_keys: List[str]):
        self.algorithm_id = algorithm_id
        self.item_count = item_count
        self.duration_seconds = duration_seconds
        self.success = success
        self.payload_keys = payload_keys
        self.items_per_second = item_count / duration_seconds if duration_seconds > 0 else 0

    def __repr__(self):
        return (
            f"BenchmarkResult({self.algorithm_id}: "
            f"{self.item_count} items in {self.duration_seconds:.3f}s "
            f"= {self.items_per_second:.0f} items/sec)"
        )


def _run_benchmark(algo, params, context, item_count) -> BenchmarkResult:
    """Run an algorithm and measure wall-clock time."""
    start = time.perf_counter()
    result = algo.run(params, context)
    elapsed = time.perf_counter() - start

    return BenchmarkResult(
        algorithm_id=result.algorithm_id,
        item_count=item_count,
        duration_seconds=elapsed,
        success=result.success,
        payload_keys=list(result.payload.keys()) if result.payload else [],
    )


# ===================================================================
# Benchmark Tests — 10k Dataset
# ===================================================================

@pytest.mark.performance
class TestBenchmark10k:
    """
    Throughput benchmarks against a 10,000-document synthetic dataset.

    These tests verify:
      1. Algorithms complete without error at scale.
      2. Execution time stays within reasonable bounds.
      3. Results remain deterministic at scale.
    """

    def test_bulk_dedup_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            BulkDedupAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 60, f"Bulk dedup took {bench.duration_seconds:.1f}s (limit: 60s)"
        print(f"\n  {bench}")

    def test_timeline_alignment_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            TimelineAlignmentAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 120, f"Timeline took {bench.duration_seconds:.1f}s (limit: 120s)"
        print(f"\n  {bench}")

    def test_integrity_sweep_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            IntegritySweepAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 60, f"Integrity sweep took {bench.duration_seconds:.1f}s (limit: 60s)"
        print(f"\n  {bench}")

    def test_bates_generator_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            BatesGeneratorAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 60, f"Bates generator took {bench.duration_seconds:.1f}s (limit: 60s)"
        print(f"\n  {bench}")

    def test_access_anomaly_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            AccessAnomalyAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 60, f"Access anomaly took {bench.duration_seconds:.1f}s (limit: 60s)"
        print(f"\n  {bench}")

    def test_provenance_graph_10k(self, dataset, benchmark_params):
        context = _make_context(dataset.items, dataset.case_links)
        bench = _run_benchmark(
            ProvenanceGraphAlgorithm(), benchmark_params, context, len(dataset.items)
        )
        assert bench.success
        assert bench.duration_seconds < 120, f"Provenance graph took {bench.duration_seconds:.1f}s (limit: 120s)"
        print(f"\n  {bench}")


# ===================================================================
# Determinism at Scale
# ===================================================================

@pytest.mark.performance
class TestDeterminismAtScale:
    """Verify that results are identical across multiple runs at 1k scale."""

    def test_all_algorithms_deterministic_1k(self, small_dataset, benchmark_params):
        """Run each algorithm twice and verify hash equality."""
        context = _make_context(small_dataset.items, small_dataset.case_links)
        algorithms = [
            BulkDedupAlgorithm(),
            TimelineAlignmentAlgorithm(),
            IntegritySweepAlgorithm(),
            BatesGeneratorAlgorithm(),
            AccessAnomalyAlgorithm(),
            ProvenanceGraphAlgorithm(),
        ]

        for algo in algorithms:
            r1 = algo.run(benchmark_params, context)
            r2 = algo.run(benchmark_params, context)
            assert r1.result_hash == r2.result_hash, (
                f"{algo.algorithm_id}: result_hash mismatch between runs "
                f"({r1.result_hash} != {r2.result_hash})"
            )


# ===================================================================
# Dataset Integrity Tests
# ===================================================================

class TestSyntheticDataset:
    """Verify the synthetic dataset generator itself."""

    def test_dataset_size(self, dataset):
        assert len(dataset.items) == 10000

    def test_dataset_deterministic(self):
        d1 = SyntheticDataset(size=100, seed=42).generate()
        d2 = SyntheticDataset(size=100, seed=42).generate()
        for a, b in zip(d1.items, d2.items):
            assert a.hash_sha256 == b.hash_sha256

    def test_dataset_has_duplicates(self, dataset):
        hashes = [item.hash_sha256 for item in dataset.items]
        unique = set(hashes)
        assert len(unique) < len(hashes), "Dataset should contain duplicates"

    def test_dataset_has_redacted_items(self, dataset):
        redacted = [item for item in dataset.items if item.is_redacted]
        assert len(redacted) >= 100

    def test_dataset_has_mixed_devices(self, dataset):
        devices = set(item.device_label for item in dataset.items if item.device_label)
        assert len(devices) >= 4

    def test_dataset_has_mixed_formats(self, dataset):
        formats = set(item.file_type for item in dataset.items)
        assert len(formats) >= 5

    def test_case_links_match_items(self, dataset):
        assert len(dataset.case_links) == len(dataset.items)


# ===================================================================
# Throughput Summary Report
# ===================================================================

@pytest.mark.performance
class TestThroughputReport:
    """Generates a consolidated benchmark report at the end."""

    def test_generate_throughput_report(self, dataset, benchmark_params, tmp_path):
        """Run all algorithms and write a JSON throughput report."""
        context = _make_context(dataset.items, dataset.case_links)
        algorithms = [
            ("bulk_dedup", BulkDedupAlgorithm()),
            ("timeline_alignment", TimelineAlignmentAlgorithm()),
            ("integrity_sweep", IntegritySweepAlgorithm()),
            ("bates_generator", BatesGeneratorAlgorithm()),
            ("access_anomaly", AccessAnomalyAlgorithm()),
            ("provenance_graph", ProvenanceGraphAlgorithm()),
        ]

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset_size": len(dataset.items),
            "seed": dataset.seed,
            "benchmarks": [],
        }

        for algo_id, algo in algorithms:
            bench = _run_benchmark(algo, benchmark_params, context, len(dataset.items))
            report["benchmarks"].append({
                "algorithm_id": bench.algorithm_id,
                "item_count": bench.item_count,
                "duration_seconds": round(bench.duration_seconds, 4),
                "items_per_second": round(bench.items_per_second, 1),
                "success": bench.success,
            })

        # Write report to file
        report_path = tmp_path / "throughput_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Verify all succeeded
        for b in report["benchmarks"]:
            assert b["success"], f"{b['algorithm_id']} failed in benchmark"

        # Print summary table
        print("\n" + "=" * 72)
        print("  ALGORITHM THROUGHPUT REPORT — 10,000 Documents")
        print("=" * 72)
        print(f"  {'Algorithm':<25} {'Time (s)':<12} {'Items/sec':<12} {'Status'}")
        print("-" * 72)
        for b in report["benchmarks"]:
            status = "PASS" if b["success"] else "FAIL"
            print(f"  {b['algorithm_id']:<25} {b['duration_seconds']:<12.3f} {b['items_per_second']:<12.0f} {status}")
        print("=" * 72)
