"""
Unit Tests — Manifest Helpers
================================
Tests for hash linking, provenance edges, and verification utilities.
"""

import os
import tempfile

import pytest

from algorithms.manifest import (
    ProvenanceEdge,
    build_derivative_record,
    compute_manifest_hash,
    link_provenance,
    verify_hash,
)


class TestVerifyHash:
    def test_matching_hash(self, tmp_path):
        content = b"Hello, forensic evidence world!"
        file_path = tmp_path / "test.bin"
        file_path.write_bytes(content)

        import hashlib
        expected = hashlib.sha256(content).hexdigest()
        result = verify_hash(str(file_path), expected)

        assert result["match"] is True
        assert result["computed"] == expected

    def test_mismatching_hash(self, tmp_path):
        file_path = tmp_path / "test.bin"
        file_path.write_bytes(b"original content")

        result = verify_hash(str(file_path), "0000000000000000000000000000000000000000000000000000000000000000")
        assert result["match"] is False

    def test_missing_file(self):
        result = verify_hash("/nonexistent/path/file.bin", "abc123")
        assert result["match"] is False
        assert result["error"] is not None

    def test_returns_computed_hash(self, tmp_path):
        content = b"test data"
        file_path = tmp_path / "data.bin"
        file_path.write_bytes(content)

        import hashlib
        expected = hashlib.sha256(content).hexdigest()
        result = verify_hash(str(file_path), expected)
        assert result["computed"] == expected


class TestBuildDerivativeRecord:
    def test_creates_record_with_hash(self):
        original_hash = "a" * 64
        data = b"derivative content bytes"
        record = build_derivative_record(
            original_hash=original_hash,
            derivative_bytes=data,
            derivative_type="bates_stamped",
            algorithm_id="bates_gen",
            algorithm_version="1.0.0",
            run_id="run-123",
        )

        assert record["original_hash"] == original_hash
        assert record["derivative_type"] == "bates_stamped"
        assert record["algorithm_id"] == "bates_gen"
        assert record["size_bytes"] == len(data)
        assert len(record["derivative_hash"]) == 64
        assert record["derivative_hash"] != original_hash

    def test_deterministic_hash(self):
        data = b"same bytes"
        r1 = build_derivative_record("a" * 64, data, "test", "algo", "1.0", "run1")
        r2 = build_derivative_record("a" * 64, data, "test", "algo", "1.0", "run2")
        assert r1["derivative_hash"] == r2["derivative_hash"]


class TestComputeManifestHash:
    def test_deterministic(self):
        entries = [{"hash": "abc", "file": "test.pdf"}, {"hash": "def", "file": "test2.pdf"}]
        h1 = compute_manifest_hash(entries)
        h2 = compute_manifest_hash(entries)
        assert h1 == h2
        assert len(h1) == 64

    def test_different_entries_different_hash(self):
        h1 = compute_manifest_hash([{"a": 1}])
        h2 = compute_manifest_hash([{"a": 2}])
        assert h1 != h2


class TestLinkProvenance:
    def test_creates_edge(self):
        edge = link_provenance(
            source_hash="src" + "0" * 61,
            target_hash="tgt" + "0" * 61,
            transformation="thumbnail",
            algorithm_id="thumb_gen",
            algorithm_version="1.0.0",
            run_id="run-abc",
        )
        assert isinstance(edge, ProvenanceEdge)
        assert edge.source_hash.startswith("src")
        assert edge.target_hash.startswith("tgt")
        assert edge.transformation == "thumbnail"
        assert edge.created_at != ""

    def test_edge_to_dict(self):
        edge = link_provenance("a" * 64, "b" * 64, "stamp", "algo", "1.0", "run")
        d = edge.to_dict()
        assert "source_hash" in d
        assert "target_hash" in d
        assert "transformation" in d
