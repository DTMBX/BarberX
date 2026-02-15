"""
Tests — Deterministic Replay Harness
=======================================
Tests verify:
  1. Matching runs are correctly identified.
  2. Mismatched hashes produce proper verdicts.
  3. Missing algorithms produce error verdicts.
  4. Report hashing is deterministic.
  5. Empty cases produce valid empty reports.
  6. Audit events are emitted correctly.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from algorithms.base import AlgorithmParams, AlgorithmResult, hash_json
from algorithms.replay import ReplayEngine, ReplayReport, ReplayVerdict


# ---------------------------------------------------------------------------
# Mock objects
# ---------------------------------------------------------------------------

@dataclass
class MockAlgorithmRun:
    """Minimal mock of models.algorithm_models.AlgorithmRun."""
    run_id: str = "run-abc-001"
    algorithm_id: str = "integrity_sweep"
    algorithm_version: str = "1.0.0"
    case_id: int = 1
    tenant_id: int = 1
    actor_id: Optional[int] = None
    success: bool = True
    result_hash: str = "aaa111"
    params_hash: str = "ppp111"
    integrity_check: str = "iii111"
    payload_json: str = "{}"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


class MockQueryResult:
    """Simulates SQLAlchemy query chain."""
    def __init__(self, items):
        self._items = items
        self._chain = self

    def filter_by(self, **kw):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return self._items


class MockAudit:
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


def _make_result(algo_id="integrity_sweep", version="1.0.0",
                 result_hash="aaa111", params_hash="ppp111",
                 integrity_check="iii111", success=True, error=None):
    """Create a deterministic AlgorithmResult for testing."""
    return AlgorithmResult(
        algorithm_id=algo_id,
        algorithm_version=version,
        run_id="replay-xyz",
        input_hashes=["in1"],
        output_hashes=["out1"],
        result_hash=result_hash,
        params_hash=params_hash,
        integrity_check=integrity_check,
        success=success,
        error=error,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    return ReplayEngine()


@pytest.fixture
def audit():
    return MockAudit()


@pytest.fixture
def mock_store():
    return MagicMock()


# ---------------------------------------------------------------------------
# ReplayVerdict tests
# ---------------------------------------------------------------------------

class TestReplayVerdict:
    def test_to_dict_round_trip(self):
        v = ReplayVerdict(
            original_run_id="run-1",
            algorithm_id="integrity_sweep",
            algorithm_version="1.0.0",
            original_result_hash="aaa",
            replay_result_hash="aaa",
            match=True,
            original_params_hash="ppp",
            replay_params_hash="ppp",
            params_match=True,
            original_integrity_check="iii",
            replay_integrity_check="iii",
            integrity_match=True,
            replay_success=True,
        )
        d = v.to_dict()
        assert d["match"] is True
        assert d["original_run_id"] == "run-1"

    def test_mismatch_verdict(self):
        v = ReplayVerdict(
            original_run_id="run-2",
            algorithm_id="bulk_dedup",
            algorithm_version="1.0.0",
            original_result_hash="aaa",
            replay_result_hash="bbb",
            match=False,
            original_params_hash="ppp",
            replay_params_hash="ppp",
            params_match=True,
            original_integrity_check="iii",
            replay_integrity_check="jjj",
            integrity_match=False,
            replay_success=True,
            delta_details={"result_hash_original": "aaa", "result_hash_replay": "bbb"},
        )
        assert v.match is False
        assert v.integrity_match is False
        assert v.delta_details["result_hash_original"] == "aaa"


# ---------------------------------------------------------------------------
# ReplayReport tests
# ---------------------------------------------------------------------------

class TestReplayReport:
    def test_finalize_computes_hash(self):
        report = ReplayReport(
            case_id=1, tenant_id=1,
            replayed_at="2025-06-01T12:00:00Z",
            total_runs=0, matched=0, mismatched=0, skipped=0, errors=0,
            all_reproducible=True, verdicts=[],
        )
        report.finalize()
        assert report.report_hash
        assert len(report.report_hash) == 64

    def test_finalize_is_deterministic(self):
        """Two identical reports must produce the same hash."""
        kwargs = dict(
            case_id=1, tenant_id=1,
            replayed_at="2025-06-01T12:00:00Z",
            total_runs=1, matched=1, mismatched=0, skipped=0, errors=0,
            all_reproducible=True, verdicts=[],
        )
        r1 = ReplayReport(**kwargs)
        r2 = ReplayReport(**kwargs)
        r1.finalize()
        r2.finalize()
        assert r1.report_hash == r2.report_hash

    def test_different_data_different_hash(self):
        r1 = ReplayReport(
            case_id=1, tenant_id=1, replayed_at="2025-06-01T12:00:00Z",
            total_runs=1, matched=1, mismatched=0, skipped=0, errors=0,
            all_reproducible=True, verdicts=[],
        )
        r2 = ReplayReport(
            case_id=1, tenant_id=1, replayed_at="2025-06-01T12:00:00Z",
            total_runs=1, matched=0, mismatched=1, skipped=0, errors=0,
            all_reproducible=False, verdicts=[],
        )
        r1.finalize()
        r2.finalize()
        assert r1.report_hash != r2.report_hash

    def test_to_dict_structure(self):
        report = ReplayReport(
            case_id=42, tenant_id=1,
            replayed_at="2025-06-01T12:00:00Z",
            total_runs=2, matched=1, mismatched=1, skipped=0, errors=0,
            all_reproducible=False, verdicts=[],
        )
        report.finalize()
        d = report.to_dict()
        assert d["case_id"] == 42
        assert d["all_reproducible"] is False
        assert "report_hash" in d


# ---------------------------------------------------------------------------
# ReplayEngine tests
# ---------------------------------------------------------------------------

class TestReplayEngine:
    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    def test_empty_case_returns_valid_report(
        self, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """A case with no algorithm runs should return reproducible=True."""
        mock_model.query = MockQueryResult([])
        report = engine.replay_case(
            case_id=99, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.total_runs == 0
        assert report.all_reproducible is True
        assert report.report_hash

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_matching_run_produces_match_verdict(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """A replay that produces the same hashes should match."""
        original = MockAlgorithmRun(
            result_hash="aaa111", params_hash="ppp111",
            integrity_check="iii111",
        )
        mock_model.query = MockQueryResult([original])

        # Mock the algorithm to return identical hashes
        mock_algo = MagicMock()
        mock_algo.run.return_value = _make_result(
            result_hash="aaa111", params_hash="ppp111", integrity_check="iii111",
        )
        mock_registry.get.return_value = mock_algo

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.total_runs == 1
        assert report.matched == 1
        assert report.mismatched == 0
        assert report.all_reproducible is True

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_mismatched_hash_produces_delta(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """A replay with different result hash should flag a mismatch."""
        original = MockAlgorithmRun(
            result_hash="aaa111", params_hash="ppp111",
            integrity_check="iii111",
        )
        mock_model.query = MockQueryResult([original])

        mock_algo = MagicMock()
        mock_algo.run.return_value = _make_result(
            result_hash="DIFFERENT", params_hash="ppp111", integrity_check="iii111",
        )
        mock_registry.get.return_value = mock_algo

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.mismatched == 1
        assert report.all_reproducible is False
        assert report.verdicts[0].match is False
        assert report.verdicts[0].delta_details["result_hash_original"] == "aaa111"

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_missing_algorithm_produces_error(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """If a recorded algorithm is no longer in the registry, error."""
        original = MockAlgorithmRun(algorithm_id="deleted_algo")
        mock_model.query = MockQueryResult([original])
        mock_registry.get.return_value = None

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.errors == 1
        assert report.all_reproducible is False
        assert "not found" in report.verdicts[0].replay_error

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_algorithm_execution_error(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """If replay execution throws, capture error in verdict."""
        original = MockAlgorithmRun()
        mock_model.query = MockQueryResult([original])

        mock_algo = MagicMock()
        mock_algo.run.side_effect = RuntimeError("boom")
        mock_registry.get.return_value = mock_algo

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.errors == 1
        assert report.verdicts[0].replay_error == "boom"

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_audit_event_emitted(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """Replay must emit an audit event on completion."""
        mock_model.query = MockQueryResult([])
        engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert len(audit.events) == 1
        assert audit.events[0]["action"] == "replay.completed"

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_multiple_runs_mixed_results(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """Multiple runs: one match, one mismatch, one error."""
        runs = [
            MockAlgorithmRun(run_id="match", algorithm_id="bulk_dedup",
                             result_hash="h1", params_hash="p1", integrity_check="i1"),
            MockAlgorithmRun(run_id="mismatch", algorithm_id="timeline_alignment",
                             result_hash="h2", params_hash="p2", integrity_check="i2"),
            MockAlgorithmRun(run_id="error", algorithm_id="gone_algo",
                             result_hash="h3", params_hash="p3", integrity_check="i3"),
        ]
        mock_model.query = MockQueryResult(runs)

        def get_algo(algo_id, version=None):
            if algo_id == "gone_algo":
                return None
            mock_a = MagicMock()
            if algo_id == "bulk_dedup":
                mock_a.run.return_value = _make_result(
                    result_hash="h1", params_hash="p1", integrity_check="i1",
                )
            else:
                mock_a.run.return_value = _make_result(
                    result_hash="CHANGED", params_hash="p2", integrity_check="i2",
                )
            return mock_a

        mock_registry.get.side_effect = get_algo

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )
        assert report.total_runs == 3
        assert report.matched == 1
        assert report.mismatched == 1
        assert report.errors == 1
        assert report.all_reproducible is False

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_params_reconstructed_from_payload(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """Params stored in payload_json._params are reconstructed."""
        stored_params = {
            "case_id": 1, "tenant_id": 1,
            "actor_id": None, "actor_name": "original",
            "extra": {"threshold": 0.8},
        }
        original = MockAlgorithmRun(
            payload_json=json.dumps({"_params": stored_params}),
            result_hash="h1", params_hash="p1", integrity_check="i1",
        )
        mock_model.query = MockQueryResult([original])

        captured_params = []

        def run_capture(params, context):
            captured_params.append(params)
            return _make_result(result_hash="h1", params_hash="p1", integrity_check="i1")

        mock_algo = MagicMock()
        mock_algo.run.side_effect = run_capture
        mock_registry.get.return_value = mock_algo

        engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
        )

        assert len(captured_params) == 1
        assert captured_params[0].extra == {"threshold": 0.8}

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    @patch("algorithms.replay.registry")
    def test_algorithm_filter(
        self, mock_registry, mock_model, mock_ensure, engine, audit, mock_store
    ):
        """When algorithm_filter is set, only matching runs replay."""
        runs = [
            MockAlgorithmRun(run_id="r1", algorithm_id="bulk_dedup",
                             result_hash="h1", params_hash="p1", integrity_check="i1"),
        ]
        mock_model.query = MockQueryResult(runs)

        mock_algo = MagicMock()
        mock_algo.run.return_value = _make_result(
            result_hash="h1", params_hash="p1", integrity_check="i1",
        )
        mock_registry.get.return_value = mock_algo

        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=audit,
            algorithm_filter=["bulk_dedup"],
        )
        assert report.total_runs == 1
        assert report.matched == 1

    @patch("algorithms.replay._ensure_algorithms")
    @patch("models.algorithm_models.AlgorithmRun")
    def test_audit_failure_does_not_crash(
        self, mock_model, mock_ensure, engine, mock_store
    ):
        """If audit emit fails, replay still completes."""
        mock_model.query = MockQueryResult([])
        bad_audit = MagicMock()
        bad_audit.record.side_effect = RuntimeError("audit db down")

        # Should not raise
        report = engine.replay_case(
            case_id=1, tenant_id=1,
            db_session=MagicMock(), evidence_store=mock_store,
            audit_stream=bad_audit,
        )
        assert report.all_reproducible is True


# ---------------------------------------------------------------------------
# Integrity check: report hash is a valid SHA-256
# ---------------------------------------------------------------------------

class TestReplayReportIntegrity:
    def test_report_hash_is_sha256(self):
        report = ReplayReport(
            case_id=1, tenant_id=1,
            replayed_at="2025-06-01T12:00:00Z",
            total_runs=0, matched=0, mismatched=0, skipped=0, errors=0,
            all_reproducible=True, verdicts=[],
        )
        report.finalize()
        # SHA-256 produces 64 hex chars
        assert len(report.report_hash) == 64
        int(report.report_hash, 16)  # Valid hex
