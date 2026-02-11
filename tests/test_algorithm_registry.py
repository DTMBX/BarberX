"""
Unit Tests — Algorithm Registry
=================================
Tests for algorithm registration, discovery, and versioning.
"""

import pytest
from algorithms.base import AlgorithmBase, AlgorithmParams
from algorithms.registry import AlgorithmRegistry


class AlgoV1(AlgorithmBase):
    @property
    def algorithm_id(self):
        return "test_reg"

    @property
    def algorithm_version(self):
        return "1.0.0"

    def _execute(self, params, context):
        return {"version": "1.0.0"}


class AlgoV2(AlgorithmBase):
    @property
    def algorithm_id(self):
        return "test_reg"

    @property
    def algorithm_version(self):
        return "2.0.0"

    def _execute(self, params, context):
        return {"version": "2.0.0"}


class OtherAlgo(AlgorithmBase):
    @property
    def algorithm_id(self):
        return "other_algo"

    @property
    def algorithm_version(self):
        return "1.0.0"

    def _execute(self, params, context):
        return {"id": "other"}


class TestAlgorithmRegistry:
    def setup_method(self):
        self.registry = AlgorithmRegistry()

    def test_register_and_get(self):
        self.registry.register(AlgoV1)
        algo = self.registry.get("test_reg")
        assert algo is not None
        assert algo.algorithm_id == "test_reg"
        assert algo.algorithm_version == "1.0.0"

    def test_get_specific_version(self):
        self.registry.register(AlgoV1)
        self.registry.register(AlgoV2)
        algo = self.registry.get("test_reg", "1.0.0")
        assert algo.algorithm_version == "1.0.0"

    def test_get_latest_version(self):
        self.registry.register(AlgoV1)
        self.registry.register(AlgoV2)
        algo = self.registry.get("test_reg")
        assert algo.algorithm_version == "2.0.0"

    def test_get_nonexistent(self):
        assert self.registry.get("nonexistent") is None

    def test_list_algorithms(self):
        self.registry.register(AlgoV1)
        self.registry.register(OtherAlgo)
        listing = self.registry.list_algorithms()
        assert len(listing) == 2
        ids = [a["algorithm_id"] for a in listing]
        assert "test_reg" in ids
        assert "other_algo" in ids

    def test_ids(self):
        self.registry.register(AlgoV1)
        self.registry.register(OtherAlgo)
        assert self.registry.ids() == ["other_algo", "test_reg"]

    def test_register_decorator_returns_class(self):
        reg = AlgorithmRegistry()
        result = reg.register(AlgoV1)
        assert result is AlgoV1
