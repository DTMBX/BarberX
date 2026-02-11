"""
Unit Tests — Algorithm Base Classes
=====================================
Tests for base.py: canonical JSON, hashing, AlgorithmParams, AlgorithmResult, AlgorithmBase.
"""

import json
import pytest

from algorithms.base import (
    AlgorithmBase,
    AlgorithmParams,
    AlgorithmResult,
    canonical_json,
    hash_json,
)


class TestCanonicalJson:
    """canonical_json must be deterministic and sorted."""

    def test_sorted_keys(self):
        obj = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(obj)
        assert result == '{"a":2,"m":3,"z":1}'

    def test_no_whitespace(self):
        obj = {"key": "value", "num": 42}
        result = canonical_json(obj)
        assert " " not in result
        assert "\n" not in result

    def test_deterministic(self):
        obj = {"b": [3, 2, 1], "a": {"y": True, "x": False}}
        r1 = canonical_json(obj)
        r2 = canonical_json(obj)
        assert r1 == r2

    def test_nested_objects(self):
        obj = {"outer": {"inner": {"deep": 1}}}
        result = json.loads(canonical_json(obj))
        assert result["outer"]["inner"]["deep"] == 1


class TestHashJson:
    """hash_json must produce consistent SHA-256 hashes."""

    def test_deterministic_hash(self):
        obj = {"case_id": 1, "items": [1, 2, 3]}
        h1 = hash_json(obj)
        h2 = hash_json(obj)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_different_objects_different_hashes(self):
        h1 = hash_json({"a": 1})
        h2 = hash_json({"a": 2})
        assert h1 != h2

    def test_key_order_irrelevant(self):
        """Canonical JSON sorts keys, so order shouldn't matter."""
        h1 = hash_json({"z": 1, "a": 2})
        h2 = hash_json({"a": 2, "z": 1})
        assert h1 == h2


class TestAlgorithmParams:
    def test_serialization(self):
        params = AlgorithmParams(case_id=42, tenant_id=1, actor_name="test")
        d = params.to_dict()
        assert d["case_id"] == 42
        assert d["tenant_id"] == 1
        assert d["actor_name"] == "test"

    def test_canonical_deterministic(self):
        p1 = AlgorithmParams(case_id=1, tenant_id=1)
        p2 = AlgorithmParams(case_id=1, tenant_id=1)
        assert p1.canonical() == p2.canonical()

    def test_different_params_different_canonical(self):
        p1 = AlgorithmParams(case_id=1, tenant_id=1)
        p2 = AlgorithmParams(case_id=2, tenant_id=1)
        assert p1.canonical() != p2.canonical()


class TestAlgorithmResult:
    def test_finalize_sets_integrity(self):
        result = AlgorithmResult(
            algorithm_id="test",
            algorithm_version="1.0.0",
            run_id="abc-123",
            input_hashes=["hash1"],
            payload={"data": "value"},
        )
        result.finalize()
        assert result.integrity_check != ""
        assert len(result.integrity_check) == 64

    def test_integrity_consistent(self):
        r1 = AlgorithmResult(
            algorithm_id="test",
            algorithm_version="1.0.0",
            run_id="same-id",
            input_hashes=["h1"],
            payload={"x": 1},
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:01",
        )
        r1.finalize()

        r2 = AlgorithmResult(
            algorithm_id="test",
            algorithm_version="1.0.0",
            run_id="same-id",
            input_hashes=["h1"],
            payload={"x": 1},
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:01",
        )
        r2.finalize()

        assert r1.integrity_check == r2.integrity_check

    def test_to_dict_includes_all_fields(self):
        result = AlgorithmResult(
            algorithm_id="test",
            algorithm_version="1.0.0",
            run_id="abc",
            input_hashes=[],
        )
        d = result.to_dict()
        assert "algorithm_id" in d
        assert "integrity_check" in d
        assert "payload" in d


class ConcreteAlgorithm(AlgorithmBase):
    """Minimal concrete algorithm for testing."""

    @property
    def algorithm_id(self):
        return "test_algo"

    @property
    def algorithm_version(self):
        return "0.1.0"

    def _execute(self, params, context):
        return {"computed": params.case_id * 2, "output_hashes": ["outhash1"]}


class FailingAlgorithm(AlgorithmBase):
    """Algorithm that always fails."""

    @property
    def algorithm_id(self):
        return "fail_algo"

    @property
    def algorithm_version(self):
        return "0.1.0"

    def _execute(self, params, context):
        raise ValueError("Intentional test failure")


class TestAlgorithmBase:
    def test_run_produces_result(self):
        algo = ConcreteAlgorithm()
        params = AlgorithmParams(case_id=5, tenant_id=1)
        result = algo.run(params, {})

        assert result.success is True
        assert result.algorithm_id == "test_algo"
        assert result.algorithm_version == "0.1.0"
        assert result.payload["computed"] == 10
        assert result.output_hashes == ["outhash1"]
        assert result.integrity_check != ""
        assert result.run_id != ""
        assert result.started_at != ""
        assert result.completed_at != ""

    def test_run_captures_failure(self):
        algo = FailingAlgorithm()
        params = AlgorithmParams(case_id=1, tenant_id=1)
        result = algo.run(params, {})

        assert result.success is False
        assert "Intentional test failure" in result.error
        assert result.integrity_check != ""

    def test_run_deterministic_params_hash(self):
        algo = ConcreteAlgorithm()
        p1 = AlgorithmParams(case_id=5, tenant_id=1)
        p2 = AlgorithmParams(case_id=5, tenant_id=1)
        r1 = algo.run(p1, {})
        r2 = algo.run(p2, {})
        assert r1.params_hash == r2.params_hash

    def test_run_different_params_different_hash(self):
        algo = ConcreteAlgorithm()
        r1 = algo.run(AlgorithmParams(case_id=1, tenant_id=1), {})
        r2 = algo.run(AlgorithmParams(case_id=2, tenant_id=1), {})
        assert r1.params_hash != r2.params_hash
