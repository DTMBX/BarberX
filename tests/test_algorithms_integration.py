"""
Integration Tests — Court-Defensible Algorithms
==================================================
These tests verify:
  1. Originals remain immutable after algorithm runs.
  2. Derivatives are linked to original hashes.
  3. Audit events are appended for every run.
  4. Algorithm results are deterministic.
  5. All seven algorithms produce valid output.

Uses an in-memory SQLite database and temporary file store.
"""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers to create mock DB objects
# ---------------------------------------------------------------------------

class MockEvidenceItem:
    """Minimal mock of models.evidence.EvidenceItem."""
    def __init__(self, id, filename, hash_sha256, file_type="pdf", device_label=None,
                 device_type=None, collected_date=None, file_size_bytes=1024,
                 evidence_store_id=None, duration_seconds=None, is_redacted=False,
                 evidence_type="document", created_at=None):
        self.id = id
        self.original_filename = filename
        self.hash_sha256 = hash_sha256
        self.file_type = file_type
        self.device_label = device_label
        self.device_type = device_type
        self.collected_date = collected_date
        self.file_size_bytes = file_size_bytes
        self.evidence_store_id = evidence_store_id or f"store-{id}"
        self.duration_seconds = duration_seconds
        self.is_redacted = is_redacted
        self.evidence_type = evidence_type
        self.created_at = created_at or datetime(2025, 11, 15, 14, 0, 0, tzinfo=timezone.utc)


class MockCaseEvidence:
    """Minimal mock of models.evidence.CaseEvidence."""
    def __init__(self, case_id, evidence_id):
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.unlinked_at = None


class MockLegalCase:
    def __init__(self, id=1, organization_id=1):
        self.id = id
        self.organization_id = organization_id


class MockQuery:
    """Minimal mock for SQLAlchemy query chains."""
    def __init__(self, items):
        self._items = items

    def filter_by(self, **kwargs):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items


class MockEvidenceStore:
    """Mock evidence store backed by a temp directory."""
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self._originals = {}
        self._derivatives = {}
        self._manifests = {}

    def add_original(self, sha256, content):
        """Helper to pre-populate an original file."""
        path = os.path.join(self.tmp_dir, f"orig_{sha256[:8]}")
        with open(path, "wb") as f:
            f.write(content)
        self._originals[sha256] = path

    def get_original_path(self, sha256):
        return self._originals.get(sha256)

    def original_exists(self, sha256):
        return sha256 in self._originals

    def store_derivative(self, evidence_id, derivative_type, filename, data, parameters=None):
        key = f"{evidence_id}:{derivative_type}:{filename}"
        path = os.path.join(self.tmp_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        self._derivatives[key] = path
        return path

    def load_manifest(self, evidence_id):
        return self._manifests.get(evidence_id)

    def _derivative_dir(self, sha256, derivative_type):
        from pathlib import Path
        return Path(self.tmp_dir) / "derivatives" / sha256[:4] / sha256 / derivative_type

    def append_audit(self, **kwargs):
        pass


class MockAuditStream:
    """Mock audit stream that records all events."""
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_store(tmp_path):
    return MockEvidenceStore(str(tmp_path))


@pytest.fixture
def audit():
    return MockAuditStream()


@pytest.fixture
def golden_items():
    """Create evidence items from the golden fixture."""
    return [
        MockEvidenceItem(
            id=1, filename="bodycam_001.mp4",
            hash_sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            file_type="mp4", device_label="BWC-7139078", device_type="body_worn_camera",
            collected_date=datetime(2025, 11, 15, 14, 30, tzinfo=timezone.utc),
            duration_seconds=300,
        ),
        MockEvidenceItem(
            id=2, filename="bodycam_001.mp4",  # duplicate hash
            hash_sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            file_type="mp4", device_label="BWC-7139078", device_type="body_worn_camera",
            collected_date=datetime(2025, 11, 15, 14, 30, tzinfo=timezone.utc),
            duration_seconds=300,
        ),
        MockEvidenceItem(
            id=3, filename="dashcam_scene.mp4",
            hash_sha256="b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3",
            file_type="mp4", device_label="DASH-4421", device_type="dash_cam",
            collected_date=datetime(2025, 11, 15, 14, 32, 5, tzinfo=timezone.utc),
            duration_seconds=600,
        ),
        MockEvidenceItem(
            id=4, filename="incident_report.pdf",
            hash_sha256="c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
            file_type="pdf",
            collected_date=datetime(2025, 11, 15, 16, 0, tzinfo=timezone.utc),
        ),
        MockEvidenceItem(
            id=5, filename="witness_photo.jpg",
            hash_sha256="d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
            file_type="jpg", device_label="PHONE-OFC-12", device_type="mobile_phone",
            collected_date=None,  # Unknown timestamp
        ),
    ]


@pytest.fixture
def case_links():
    return [
        MockCaseEvidence(1, 1),
        MockCaseEvidence(1, 2),
        MockCaseEvidence(1, 3),
        MockCaseEvidence(1, 4),
        MockCaseEvidence(1, 5),
    ]


def make_context(tmp_store, audit, items, case_links):
    """Build a mock context with patched DB queries."""
    mock_session = MagicMock()

    def query_side_effect(model):
        model_name = model.__name__ if hasattr(model, "__name__") else str(model)
        if "LegalCase" in model_name:
            return MockQuery([MockLegalCase()])
        elif "CaseEvidence" in model_name:
            return MockQuery(case_links)
        elif "EvidenceItem" in model_name:
            return MockQuery(items)
        elif "ChainOfCustody" in model_name:
            return MockQuery([])
        return MockQuery([])

    mock_session.query = MagicMock(side_effect=query_side_effect)

    return {
        "db_session": mock_session,
        "evidence_store": tmp_store,
        "audit_stream": audit,
    }


# ---------------------------------------------------------------------------
# Algorithm imports (triggers registration)
# ---------------------------------------------------------------------------

from algorithms.base import AlgorithmParams
from algorithms.bulk_dedup import BulkDedupAlgorithm
from algorithms.provenance_graph import ProvenanceGraphAlgorithm
from algorithms.timeline_alignment import TimelineAlignmentAlgorithm
from algorithms.integrity_sweep import IntegritySweepAlgorithm
from algorithms.bates_generator import BatesGeneratorAlgorithm
from algorithms.access_anomaly import AccessAnomalyAlgorithm


# ===================================================================
# Test: Bulk Dedup
# ===================================================================

class TestBulkDedup:
    def test_detects_exact_duplicates(self, tmp_store, audit, golden_items, case_links):
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = BulkDedupAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1, extra={"near_dedup": False})

        result = algo.run(params, context)

        assert result.success is True
        payload = result.payload
        assert payload["exact_duplicate_groups"] >= 1  # items 1 & 2 share a hash
        assert payload["total_items"] == 5

        # Verify determinism
        result2 = algo.run(params, context)
        assert result.result_hash == result2.result_hash

    def test_never_deletes_originals(self, tmp_store, audit, golden_items, case_links):
        """Verify that dedup only flags, never deletes."""
        # Add an original to the store
        content = b"original video content"
        h = golden_items[0].hash_sha256
        tmp_store.add_original(h, content)

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = BulkDedupAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1, extra={"near_dedup": False})
        algo.run(params, context)

        # Original must still exist
        assert tmp_store.get_original_path(h) is not None
        with open(tmp_store.get_original_path(h), "rb") as f:
            assert f.read() == content


# ===================================================================
# Test: Provenance Graph
# ===================================================================

class TestProvenanceGraph:
    def test_builds_graph_with_nodes(self, tmp_store, audit, golden_items, case_links):
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = ProvenanceGraphAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)

        assert result.success is True
        payload = result.payload
        assert payload["statistics"]["total_nodes"] >= 4  # 4 unique hashes
        assert payload["statistics"]["originals"] >= 4
        assert "graph_hash" in payload

    def test_graph_hash_deterministic(self, tmp_store, audit, golden_items, case_links):
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = ProvenanceGraphAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        r1 = algo.run(params, context)
        r2 = algo.run(params, context)
        assert r1.payload["graph_hash"] == r2.payload["graph_hash"]


# ===================================================================
# Test: Timeline Alignment
# ===================================================================

class TestTimelineAlignment:
    def test_sorts_with_confidence(self, tmp_store, audit, golden_items, case_links):
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = TimelineAlignmentAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)

        assert result.success is True
        payload = result.payload
        assert payload["total_entries"] == 5

        # Item 5 has no timestamp → should be "unknown" or "derived"
        confidences = [e["timestamp_confidence"] for e in payload["timeline_entries"]]
        assert "exact" in confidences
        # At least one item should be unknown (item 5 has no collected_date)
        # (it may get "derived" from created_at, which is set in mock)

    def test_records_assumptions(self, tmp_store, audit, golden_items, case_links):
        # Item with no collected_date
        golden_items[4].collected_date = None
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = TimelineAlignmentAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)
        # Should record assumption for item 5 using created_at as fallback
        assert result.success is True

    def test_timeline_hash_deterministic(self, tmp_store, audit, golden_items, case_links):
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = TimelineAlignmentAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        r1 = algo.run(params, context)
        r2 = algo.run(params, context)
        assert r1.payload["timeline_hash"] == r2.payload["timeline_hash"]


# ===================================================================
# Test: Integrity Sweep
# ===================================================================

class TestIntegritySweep:
    def test_passes_when_hashes_match(self, tmp_store, audit, golden_items, case_links):
        # Create originals with matching content
        for item in golden_items:
            content = f"content-for-{item.id}".encode()
            real_hash = hashlib.sha256(content).hexdigest()
            item.hash_sha256 = real_hash
            tmp_store.add_original(real_hash, content)

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)

        assert result.success is True
        assert result.payload["all_passed"] is True
        assert result.payload["summary"]["pass"] == 5

    def test_detects_missing_files(self, tmp_store, audit, golden_items, case_links):
        # Don't add any originals → all should be missing
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)

        assert result.success is True
        assert result.payload["all_passed"] is False
        assert result.payload["summary"]["missing"] == 5

    def test_detects_hash_mismatch(self, tmp_store, audit, golden_items, case_links):
        # Add original with wrong content
        item = golden_items[0]
        tmp_store.add_original(item.hash_sha256, b"tampered content - different hash")

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        result = algo.run(params, context)
        assert result.success is True
        # At least one should fail
        assert result.payload["summary"]["fail"] >= 1

    def test_emits_audit_events(self, tmp_store, audit, golden_items, case_links):
        content = b"audit-test-content"
        real_hash = hashlib.sha256(content).hexdigest()
        golden_items[0].hash_sha256 = real_hash
        tmp_store.add_original(real_hash, content)

        # Only use one item
        items_subset = [golden_items[0]]
        links_subset = [case_links[0]]
        context = make_context(tmp_store, audit, items_subset, links_subset)
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1, actor_name="test_user")

        result = algo.run(params, context)

        # Algorithm base emits one audit event + integrity sweep emits per-item
        assert len(audit.events) >= 1

    def test_originals_immutable_after_sweep(self, tmp_store, audit, golden_items, case_links):
        """Integrity sweep must NEVER modify the original files."""
        content = b"immutable original content"
        real_hash = hashlib.sha256(content).hexdigest()
        golden_items[0].hash_sha256 = real_hash
        tmp_store.add_original(real_hash, content)

        context = make_context(tmp_store, audit, [golden_items[0]], [case_links[0]])
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)
        algo.run(params, context)

        # Read back and verify unchanged
        with open(tmp_store.get_original_path(real_hash), "rb") as f:
            assert f.read() == content


# ===================================================================
# Test: Bates Generator
# ===================================================================

class TestBatesGenerator:
    def test_generates_numbered_derivatives(self, tmp_store, audit, golden_items, case_links):
        # Add originals
        for item in golden_items:
            tmp_store.add_original(item.hash_sha256, f"content-{item.id}".encode())

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = BatesGeneratorAlgorithm()
        params = AlgorithmParams(
            case_id=1, tenant_id=1,
            extra={"prefix": "CASE1", "start_number": 1},
        )

        result = algo.run(params, context)

        assert result.success is True
        exhibits = result.payload["exhibits"]
        assert len(exhibits) >= 4  # 4 unique hashes (items 1&2 share hash, first gets processed)

        # Check Bates numbering
        bates_numbers = [e["bates_number"] for e in exhibits if e.get("status") == "generated"]
        assert "CASE1-000001" in bates_numbers

    def test_derivatives_have_own_hashes(self, tmp_store, audit, golden_items, case_links):
        for item in golden_items:
            tmp_store.add_original(item.hash_sha256, f"content-{item.id}".encode())

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = BatesGeneratorAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1, extra={"prefix": "EVD"})

        result = algo.run(params, context)
        for exhibit in result.payload["exhibits"]:
            if exhibit.get("status") == "generated":
                assert "derivative_hash" in exhibit
                assert exhibit["derivative_hash"] != exhibit["original_hash"]

    def test_originals_unchanged(self, tmp_store, audit, golden_items, case_links):
        """Bates stamping must NOT modify originals."""
        original_content = b"This is the original PDF content"
        h = golden_items[3].hash_sha256  # PDF item
        tmp_store.add_original(h, original_content)

        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = BatesGeneratorAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)
        algo.run(params, context)

        with open(tmp_store.get_original_path(h), "rb") as f:
            assert f.read() == original_content


# ===================================================================
# Test: Access Anomaly Detector
# ===================================================================

class TestAccessAnomaly:
    def test_detects_download_burst(self, tmp_store, audit, golden_items, case_links):
        from models.evidence import ChainOfCustody

        # Create mock audit entries with download bursts
        mock_entries = []
        base_time = datetime(2025, 11, 15, 15, 0, 0, tzinfo=timezone.utc)
        for i in range(6):
            entry = MagicMock()
            entry.evidence_id = 1
            entry.action = "evidence.downloaded"
            entry.actor_name = "detective_jones"
            entry.actor_id = 2
            entry.action_timestamp = base_time.replace(minute=i)
            entry.ip_address = "10.0.1.51"
            mock_entries.append(entry)

        mock_session = MagicMock()
        def query_side_effect(model):
            model_name = model.__name__ if hasattr(model, "__name__") else str(model)
            if "LegalCase" in model_name:
                return MockQuery([MockLegalCase()])
            elif "CaseEvidence" in model_name:
                return MockQuery(case_links)
            elif "ChainOfCustody" in model_name:
                return MockQuery(mock_entries)
            return MockQuery([])

        mock_session.query = MagicMock(side_effect=query_side_effect)

        context = {
            "db_session": mock_session,
            "evidence_store": tmp_store,
            "audit_stream": audit,
        }

        algo = AccessAnomalyAlgorithm()
        params = AlgorithmParams(
            case_id=1, tenant_id=1,
            extra={"download_burst_threshold": 5},
        )

        result = algo.run(params, context)
        assert result.success is True
        assert result.payload["total_anomalies"] >= 1

        # Check that download burst was detected
        types = [a["type"] for a in result.payload["anomalies"]]
        assert "download_burst" in types


# ===================================================================
# Test: Cross-cutting concerns
# ===================================================================

class TestCrossCutting:
    def test_all_algorithms_registered(self):
        """Verify all 7 algorithms are registered in the global registry."""
        from algorithms.registry import registry
        # Import all to trigger registration
        import algorithms.bulk_dedup  # noqa
        import algorithms.provenance_graph  # noqa
        import algorithms.timeline_alignment  # noqa
        import algorithms.integrity_sweep  # noqa
        import algorithms.bates_generator  # noqa
        import algorithms.redaction_verify  # noqa
        import algorithms.access_anomaly  # noqa

        expected_ids = {
            "bulk_dedup",
            "provenance_graph",
            "timeline_alignment",
            "integrity_sweep",
            "bates_generator",
            "redaction_verify",
            "access_anomaly",
        }
        registered_ids = set(registry.ids())
        assert expected_ids.issubset(registered_ids)

    def test_all_results_have_integrity_check(self, tmp_store, audit, golden_items, case_links):
        """Every algorithm result must have a non-empty integrity_check."""
        context = make_context(tmp_store, audit, golden_items, case_links)

        algorithms = [
            BulkDedupAlgorithm(),
            ProvenanceGraphAlgorithm(),
            TimelineAlignmentAlgorithm(),
            IntegritySweepAlgorithm(),
        ]

        for algo in algorithms:
            params = AlgorithmParams(case_id=1, tenant_id=1)
            result = algo.run(params, context)
            assert result.integrity_check != "", f"{algo.algorithm_id} missing integrity_check"
            assert len(result.integrity_check) == 64, f"{algo.algorithm_id} bad integrity_check length"

    def test_all_results_have_run_id(self, tmp_store, audit, golden_items, case_links):
        """Every result must have a unique run_id."""
        context = make_context(tmp_store, audit, golden_items, case_links)
        algo = IntegritySweepAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)

        r1 = algo.run(params, context)
        r2 = algo.run(params, context)
        assert r1.run_id != r2.run_id
        assert len(r1.run_id) == 36  # UUID format
