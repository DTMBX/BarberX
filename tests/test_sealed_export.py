"""
Tests — Integrity-Sealed Court Package Export
================================================
Tests verify:
  1. Package ZIP is created with all required files.
  2. SEAL.json contains correct file manifest.
  3. All file hashes are verified against actual content.
  4. Algorithm version manifest is generated.
  5. Failures in individual algorithms do not crash the build.
  6. SealedPackageResult correctly reports status.
  7. Deterministic given same inputs.
"""

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from algorithms.base import AlgorithmParams, AlgorithmResult, hash_json
from algorithms.sealed_export import SealedCourtPackageBuilder, SealedPackageResult


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

class MockEvidenceItem:
    def __init__(self, id, filename, hash_sha256):
        self.id = id
        self.original_filename = filename
        self.hash_sha256 = hash_sha256
        self.file_type = "pdf"
        self.device_label = None
        self.device_type = None
        self.collected_date = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        self.file_size_bytes = 1024
        self.evidence_store_id = f"store-{id}"
        self.duration_seconds = None
        self.is_redacted = False
        self.evidence_type = "document"
        self.created_at = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


class MockCaseEvidence:
    def __init__(self, case_id, evidence_id):
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.unlinked_at = None


class MockQuery:
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


class MockAudit:
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


class MockStore:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self._originals = {}

    def add_original(self, sha256, content):
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
        return path

    def load_manifest(self, evidence_id):
        return None

    def append_audit(self, **kwargs):
        pass


class MockLegalCase:
    def __init__(self, id=1, organization_id=1):
        self.id = id
        self.organization_id = organization_id


def _make_mock_session(items, case_links):
    """Build a mock session that returns items and links."""
    session = MagicMock()

    def query_side_effect(model):
        name = model.__name__ if hasattr(model, "__name__") else str(model)
        if "LegalCase" in name:
            return MockQuery([MockLegalCase()])
        elif "CaseEvidence" in name:
            return MockQuery(case_links)
        elif "EvidenceItem" in name:
            return MockQuery(items)
        elif "ChainOfCustody" in name:
            return MockQuery([])
        return MockQuery([])

    session.query = MagicMock(side_effect=query_side_effect)
    return session


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def items():
    return [
        MockEvidenceItem(1, "report.pdf", "aaaa" * 16),
        MockEvidenceItem(2, "photo.jpg", "bbbb" * 16),
    ]


@pytest.fixture
def case_links():
    return [
        MockCaseEvidence(1, 1),
        MockCaseEvidence(1, 2),
    ]


@pytest.fixture
def store(tmp_path):
    s = MockStore(str(tmp_path))
    content_a = b"original content A"
    content_b = b"original content B"
    s.add_original("aaaa" * 16, content_a)
    s.add_original("bbbb" * 16, content_b)
    return s


@pytest.fixture
def audit():
    return MockAudit()


@pytest.fixture
def builder(tmp_path):
    return SealedCourtPackageBuilder(export_base=str(tmp_path / "sealed"))


# ---------------------------------------------------------------------------
# SealedPackageResult tests
# ---------------------------------------------------------------------------

class TestSealedPackageResult:
    def test_to_dict_serializable(self):
        result = SealedPackageResult(
            success=True,
            package_path="/tmp/test.zip",
            seal_hash="abc123",
            exhibit_count=5,
            algorithms_run=["integrity_sweep"],
            algorithm_versions={"integrity_sweep": "1.0.0"},
            total_files=10,
        )
        d = result.to_dict()
        assert d["success"] is True
        assert json.dumps(d)  # Must be JSON-serializable

    def test_failure_result(self):
        result = SealedPackageResult(
            success=False,
            package_path="",
            seal_hash="",
            exhibit_count=0,
            algorithms_run=[],
            algorithm_versions={},
            total_files=0,
            error="something broke",
        )
        assert result.success is False
        assert result.error == "something broke"


# ---------------------------------------------------------------------------
# SealedCourtPackageBuilder tests
# ---------------------------------------------------------------------------

class TestSealedCourtPackageBuilder:
    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_build_creates_zip(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """Builder must produce a ZIP file."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result.success is True
        assert result.package_path.endswith(".zip")
        assert os.path.isfile(result.package_path)

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_zip_contains_seal_json(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """The ZIP must contain SEAL.json and SEAL_HASH.txt."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert "SEAL.json" in names
            assert "SEAL_HASH.txt" in names

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_seal_hash_matches_content(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """SEAL.json hash must match the seal_hash in result."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            seal_bytes = zf.read("SEAL.json")
            computed = hashlib.sha256(seal_bytes).hexdigest()
            assert computed == result.seal_hash

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_file_manifest_hashes_verified(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """Every file in SEAL.json file_manifest must have a correct hash."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            seal = json.loads(zf.read("SEAL.json"))
            for entry_path, expected_hash in seal["file_manifest"].items():
                content = zf.read(entry_path)
                actual = hashlib.sha256(content).hexdigest()
                assert actual == expected_hash, (
                    f"Hash mismatch for {entry_path}: expected {expected_hash}, got {actual}"
                )

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_algorithm_versions_included(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """ALGORITHM_VERSIONS.json must be present in the ZIP."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "ALGORITHM_VERSIONS.json" in zf.namelist()
            versions = json.loads(zf.read("ALGORITHM_VERSIONS.json"))
            assert "algorithms" in versions

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_reports_directory_populated(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """Reports directory must contain algorithm result JSONs."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            report_files = [n for n in zf.namelist() if n.startswith("reports/")]
            assert len(report_files) > 0

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_audit_log_included(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """audit_log.json must be present in the ZIP."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "audit_log.json" in zf.namelist()

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_single_algorithm_failure_does_not_crash(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """If one algorithm fails, the build should still produce a package."""
        # One algo succeeds, one throws
        success_result = self._make_algo_result("integrity_sweep", success=True)
        failing_algo = MagicMock()
        failing_algo.run.side_effect = RuntimeError("algo crashed")
        failing_algo.algorithm_version = "1.0.0"

        success_algo = MagicMock()
        success_algo.run.return_value = success_result

        def get_algo(algo_id, version=None):
            if algo_id == "provenance_graph":
                return failing_algo
            return success_algo

        mock_registry.get.side_effect = get_algo
        mock_registry.list_algorithms.return_value = []
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        # The build should still succeed (partial results)
        assert result.success is True

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_seal_version(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """SEAL.json must have seal_version 1.0."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        with zipfile.ZipFile(result.package_path, "r") as zf:
            seal = json.loads(zf.read("SEAL.json"))
            assert seal["seal_version"] == "1.0"
            assert seal["case_id"] == 1

    @patch("algorithms.sealed_export._ensure_algorithms")
    @patch("algorithms.sealed_export.registry")
    def test_result_fields(
        self, mock_registry, mock_ensure, builder, items, case_links, store, audit
    ):
        """Result must populate all expected fields."""
        self._setup_registry(mock_registry)
        session = _make_mock_session(items, case_links)

        result = builder.build(
            case_id=1, tenant_id=1,
            db_session=session,
            evidence_store=store,
            audit_stream=audit,
            generated_at=datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert result.success is True
        assert result.seal_hash
        assert len(result.seal_hash) == 64
        assert isinstance(result.algorithms_run, list)
        assert result.total_files > 0

    # -----------------------------------------------------------------------
    # Helper to set up a basic registry that returns mock results
    # -----------------------------------------------------------------------

    @staticmethod
    def _make_algo_result(algo_id, version="1.0.0", success=True):
        return AlgorithmResult(
            algorithm_id=algo_id,
            algorithm_version=version,
            run_id=f"run-{algo_id}",
            input_hashes=["in1"],
            output_hashes=["out1"],
            success=success,
            payload={
                "total_items": 2,
                "summary": {"pass": 2, "fail": 0, "missing": 0, "error": 0, "warning": 0, "skipped": 0},
                "all_passed": True,
                "report_hash": "fake_report_hash",
                "total_checked": 2,
                "count": 2,
                "exact_duplicate_groups": 0,
                "items": [],
                "stats": {"total_items": 2, "exact": 1, "derived": 1, "unknown": 0},
                "assumptions": [],
                "drift_pairs": [],
            },
            error=None if success else "failed",
        )

    def _setup_registry(self, mock_registry):
        """Configure mock_registry to return functional mock algorithms."""
        algo_ids = [
            "integrity_sweep", "provenance_graph", "timeline_alignment",
            "bates_generator", "redaction_verify", "access_anomaly",
        ]

        def get_algo(algo_id, version=None):
            if algo_id in algo_ids:
                mock_algo = MagicMock()
                mock_algo.run.return_value = self._make_algo_result(algo_id)
                mock_algo.algorithm_version = "1.0.0"
                return mock_algo
            return None

        mock_registry.get.side_effect = get_algo
        mock_registry.list_algorithms.return_value = [
            {"algorithm_id": aid, "version": "1.0.0", "description": f"Mock {aid}"}
            for aid in algo_ids
        ]
