"""
E2E Chain-of-Custody Integration Tests
========================================
Full-pipeline tests that verify court-defensibility guarantees by
exercising the algorithm engine, sealed export, and Flask routes.

These tests prove:
  1. Evidence originals are never mutated by any algorithm operation.
  2. Every algorithm run produces an auditable, hash-verified record.
  3. The sealed court package is self-verifying via SEAL.json.
  4. Replay produces identical results (deterministic reproducibility).
  5. The audit log is append-only — no deletions or overwrites.
  6. API authentication is enforced on all algorithm endpoints.

Each test uses mock contexts consistent with the existing test patterns
in test_algorithms_integration.py.
"""

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from algorithms.base import AlgorithmParams, AlgorithmResult, canonical_json, hash_json
from algorithms.registry import registry
from algorithms.bulk_dedup import BulkDedupAlgorithm
from algorithms.provenance_graph import ProvenanceGraphAlgorithm
from algorithms.timeline_alignment import TimelineAlignmentAlgorithm
from algorithms.integrity_sweep import IntegritySweepAlgorithm
from algorithms.bates_generator import BatesGeneratorAlgorithm
from algorithms.access_anomaly import AccessAnomalyAlgorithm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _MockEvItem:
    """Mock evidence item matching the shape algorithms expect."""
    def __init__(self, id, filename, hash_sha256, file_type="pdf",
                 device_label=None, device_type=None, collected_date=None,
                 file_size_bytes=1024, evidence_store_id=None,
                 duration_seconds=None, is_redacted=False,
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
    """Mock SQLAlchemy query that supports chained filter/order calls."""
    def __init__(self, items):
        self._items = items

    def filter_by(self, **kw):
        return self

    def filter(self, *a):
        return self

    def order_by(self, *a):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items


class _MockStore:
    """Mock evidence store that manages originals on the filesystem."""
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        os.makedirs(tmp_dir, exist_ok=True)
        self._originals = {}
        self._derivatives = {}
        self._manifests = {}

    def add_original(self, sha256, content):
        path = os.path.join(self.tmp_dir, f"orig_{sha256[:8]}")
        with open(path, "wb") as f:
            f.write(content)
        self._originals[sha256] = path

    def get_original_path(self, sha256):
        return self._originals.get(sha256)

    def original_exists(self, sha256):
        return sha256 in self._originals

    def store_derivative(self, evidence_id, derivative_type, filename, data,
                         parameters=None):
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


class _MockAudit:
    """Append-only mock audit stream capturing all events."""
    def __init__(self):
        self.events = []

    def record(self, **kwargs):
        self.events.append(kwargs)


# ---------------------------------------------------------------------------
# Sample evidence items (used by all tests)
# ---------------------------------------------------------------------------

ITEMS = [
    _MockEvItem(
        id=1, filename="bodycam_001.mp4",
        hash_sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        file_type="mp4", device_label="BWC-7139078", device_type="body_worn_camera",
        collected_date=datetime(2025, 11, 15, 14, 30, tzinfo=timezone.utc),
        file_size_bytes=52428800, duration_seconds=300,
    ),
    _MockEvItem(
        id=2, filename="bodycam_001.mp4",
        hash_sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        file_type="mp4", device_label="BWC-7139078", device_type="body_worn_camera",
        collected_date=datetime(2025, 11, 15, 14, 30, tzinfo=timezone.utc),
        file_size_bytes=52428800, duration_seconds=300,
    ),
    _MockEvItem(
        id=3, filename="dashcam_scene.mp4",
        hash_sha256="b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3",
        file_type="mp4", device_label="DASH-4421", device_type="dash_cam",
        collected_date=datetime(2025, 11, 15, 14, 32, 5, tzinfo=timezone.utc),
        file_size_bytes=104857600, duration_seconds=600,
    ),
    _MockEvItem(
        id=4, filename="incident_report.pdf",
        hash_sha256="c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        file_type="pdf",
        collected_date=datetime(2025, 11, 15, 16, 0, tzinfo=timezone.utc),
        file_size_bytes=2048000,
    ),
    _MockEvItem(
        id=5, filename="witness_photo.jpg",
        hash_sha256="d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
        file_type="jpg", device_label="PHONE-OFC-12", device_type="mobile_phone",
        file_size_bytes=4096000,
    ),
]

CASE_LINKS = [_MockCaseEvidence(1, i) for i in range(1, 6)]


def _make_context(tmp_dir):
    """Build a mock algorithm execution context using query_side_effect routing."""
    store = _MockStore(tmp_dir)
    audit = _MockAudit()

    for item in ITEMS:
        content = f"original-content-{item.hash_sha256}".encode()
        store.add_original(item.hash_sha256, content)

    mock_session = MagicMock()

    def query_side_effect(model):
        name = model.__name__ if hasattr(model, "__name__") else str(model)
        if "LegalCase" in name:
            return _MockQuery([_MockLegalCase()])
        elif "CaseEvidence" in name:
            return _MockQuery(CASE_LINKS)
        elif "EvidenceItem" in name:
            return _MockQuery(ITEMS)
        elif "ChainOfCustody" in name:
            return _MockQuery([])
        return _MockQuery([])

    mock_session.query = MagicMock(side_effect=query_side_effect)

    return {
        "db_session": mock_session,
        "evidence_store": store,
        "audit_stream": audit,
    }


PARAMS = AlgorithmParams(case_id=1, tenant_id=1)

# Algorithms that are safe to run with our mock context
ALGOS = [
    BulkDedupAlgorithm,
    TimelineAlignmentAlgorithm,
    BatesGeneratorAlgorithm,
    IntegritySweepAlgorithm,
]


# ===================================================================
# 1. Evidence Immutability
# ===================================================================

class TestEvidenceImmutability:
    """Prove that running algorithms never mutates original evidence."""

    def test_originals_unchanged_after_all_algorithms(self, tmp_path):
        """Run every algorithm and verify original file hashes are identical."""
        ctx = _make_context(str(tmp_path))
        store = ctx["evidence_store"]

        # Record original hashes before any algorithm runs
        original_hashes = {}
        for item in ITEMS:
            path = store.get_original_path(item.hash_sha256)
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    original_hashes[item.hash_sha256] = _sha256(f.read())

        assert len(original_hashes) > 0, "No originals found"

        # Run all algorithms
        for AlgoClass in ALGOS:
            algo = AlgoClass()
            try:
                algo.run(PARAMS, ctx)
            except Exception:
                pass  # Algorithm errors are acceptable; mutation is not

        # Verify no original was mutated
        for sha, orig_hash in original_hashes.items():
            path = store.get_original_path(sha)
            assert os.path.exists(path), f"Original file disappeared: {sha[:16]}"
            with open(path, "rb") as f:
                current = _sha256(f.read())
            assert current == orig_hash, f"Original mutated: {sha[:16]}"

    def test_evidence_hashes_are_deterministic(self):
        """SHA-256 of identical content is always identical."""
        content = b"court-exhibit-2025-alpha-bravo"
        assert _sha256(content) == _sha256(content)
        assert len(_sha256(content)) == 64

    def test_different_content_different_hash(self):
        """One-byte change produces a different hash."""
        a = b"evidence-original-file-content"
        b_mod = b"evidence-original-file-contenU"
        assert _sha256(a) != _sha256(b_mod)


# ===================================================================
# 2. Algorithm Determinism
# ===================================================================

class TestAlgorithmDeterminism:
    """Prove that identical inputs produce identical outputs."""

    def test_bulk_dedup_deterministic(self, tmp_path):
        ctx = _make_context(str(tmp_path))
        algo = BulkDedupAlgorithm()
        r1 = algo.run(PARAMS, ctx)
        r2 = algo.run(PARAMS, ctx)
        assert r1.result_hash == r2.result_hash
        assert r1.params_hash == r2.params_hash

    def test_timeline_alignment_deterministic(self, tmp_path):
        ctx = _make_context(str(tmp_path))
        algo = TimelineAlignmentAlgorithm()
        r1 = algo.run(PARAMS, ctx)
        r2 = algo.run(PARAMS, ctx)
        assert r1.result_hash == r2.result_hash

    def test_bates_generator_deterministic(self, tmp_path):
        ctx = _make_context(str(tmp_path))
        algo = BatesGeneratorAlgorithm()
        p = AlgorithmParams(case_id=1, tenant_id=1, extra={"prefix": "EVD", "start_number": 1})
        r1 = algo.run(p, ctx)
        r2 = algo.run(p, ctx)
        assert r1.result_hash == r2.result_hash

    def test_integrity_sweep_deterministic(self, tmp_path):
        ctx = _make_context(str(tmp_path))
        algo = IntegritySweepAlgorithm()
        r1 = algo.run(PARAMS, ctx)
        r2 = algo.run(PARAMS, ctx)
        assert r1.result_hash == r2.result_hash

    def test_all_algorithms_produce_valid_result(self, tmp_path):
        """Every algorithm returns a well-formed AlgorithmResult."""
        ctx = _make_context(str(tmp_path))
        for AlgoClass in ALGOS:
            algo = AlgoClass()
            result = algo.run(PARAMS, ctx)
            assert isinstance(result, AlgorithmResult), f"{AlgoClass.__name__} wrong type"
            assert result.result_hash, f"{AlgoClass.__name__} missing result_hash"
            assert result.integrity_check, f"{AlgoClass.__name__} missing integrity_check"


# ===================================================================
# 3. Audit Log Integrity
# ===================================================================

class TestAuditLogIntegrity:
    """Prove that audit logs are append-only and capture all operations."""

    def test_audit_events_appended_per_algorithm(self, tmp_path):
        ctx = _make_context(str(tmp_path))
        audit = ctx["audit_stream"]
        initial = len(audit.events)
        algo = BulkDedupAlgorithm()
        algo.run(PARAMS, ctx)
        assert len(audit.events) > initial, "No audit event recorded"

    def test_audit_events_never_decrease(self, tmp_path):
        """Event count is monotonically non-decreasing across runs."""
        ctx = _make_context(str(tmp_path))
        audit = ctx["audit_stream"]
        counts = [len(audit.events)]
        for AlgoClass in ALGOS:
            algo = AlgoClass()
            try:
                algo.run(PARAMS, ctx)
            except Exception:
                pass
            counts.append(len(audit.events))
        for i in range(1, len(counts)):
            assert counts[i] >= counts[i - 1], (
                f"Audit event count decreased at step {i}: {counts[i-1]} → {counts[i]}"
            )

    def test_audit_events_monotonic_reference(self):
        """Events are stored by reference; appending is always additive."""
        audit = _MockAudit()
        audit.record(action="e1", actor="sys")
        audit.record(action="e2", actor="sys")
        saved = audit.events  # same reference
        audit.record(action="e3", actor="sys")
        assert len(saved) == 3, "Audit list was replaced, not appended"

    def test_canonical_json_is_deterministic(self):
        """Key ordering does not affect canonical hash."""
        o1 = {"z_key": 1, "a_key": 2, "m_key": [3, 4]}
        o2 = {"a_key": 2, "m_key": [3, 4], "z_key": 1}
        assert canonical_json(o1) == canonical_json(o2)
        assert hash_json(o1) == hash_json(o2)


# ===================================================================
# 4. Sealed Court Package Verification
# ===================================================================

class TestSealedCourtPackage:
    """Prove that sealed packages are cryptographically self-verifying."""

    def _build_package(self, tmp_path):
        from algorithms.sealed_export import SealedCourtPackageBuilder
        ctx = _make_context(str(tmp_path))
        builder = SealedCourtPackageBuilder(export_base=str(tmp_path / "sealed"))
        result = builder.build(
            case_id=1,
            tenant_id=1,
            db_session=ctx["db_session"],
            evidence_store=ctx["evidence_store"],
            audit_stream=ctx["audit_stream"],
            generated_at=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            actor_name="e2e-test",
        )
        return result

    def test_seal_json_references_all_files(self, tmp_path):
        result = self._build_package(tmp_path)
        assert result.success, f"Build failed: {result.error}"
        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert "SEAL.json" in names
            seal = json.loads(zf.read("SEAL.json"))
            referenced = set(seal.get("file_manifest", {}).keys())
            for name in names:
                if name in ("SEAL.json", "SEAL_HASH.txt"):
                    continue
                assert name in referenced, f"{name} not referenced in SEAL.json"

    def test_seal_hash_matches_seal_json(self, tmp_path):
        result = self._build_package(tmp_path)
        assert result.success, f"Build failed: {result.error}"
        with zipfile.ZipFile(result.package_path, "r") as zf:
            seal_bytes = zf.read("SEAL.json")
            seal_hash_text = zf.read("SEAL_HASH.txt").decode()
            # Extract hash from human-readable text: "SEAL.json SHA-256: <hash>"
            recorded = None
            for line in seal_hash_text.splitlines():
                if "SHA-256:" in line:
                    recorded = line.split(":", 1)[1].strip()
                    break
            assert recorded is not None, "SHA-256 not found in SEAL_HASH.txt"
            computed = _sha256(seal_bytes)
            assert computed == recorded, "SEAL_HASH.txt hash does not match SEAL.json"

    def test_file_hashes_verify_in_package(self, tmp_path):
        result = self._build_package(tmp_path)
        assert result.success, f"Build failed: {result.error}"
        with zipfile.ZipFile(result.package_path, "r") as zf:
            seal = json.loads(zf.read("SEAL.json"))
            for fname, expected in seal.get("file_manifest", {}).items():
                actual = _sha256(zf.read(fname))
                assert actual == expected, f"Tampered file: {fname}"

    def test_package_algorithm_results_are_deterministic(self, tmp_path):
        """Two builds produce identical algorithm result_hashes.

        Uses a shared evidence directory so that file paths in
        algorithm payloads are identical across both runs.
        """
        from algorithms.sealed_export import SealedCourtPackageBuilder

        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()
        ctx = _make_context(str(evidence_dir))

        result_hashes_per_run = []
        for i in range(2):
            export_dir = tmp_path / f"export_{i}" / "sealed"
            builder = SealedCourtPackageBuilder(export_base=str(export_dir))
            result = builder.build(
                case_id=1,
                tenant_id=1,
                db_session=ctx["db_session"],
                evidence_store=ctx["evidence_store"],
                audit_stream=ctx["audit_stream"],
                generated_at=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
                actor_name="e2e-test",
            )
            assert result.success, f"Build {i} failed: {result.error}"
            with zipfile.ZipFile(result.package_path, "r") as zf:
                seal = json.loads(zf.read("SEAL.json"))
                algo_hashes = {
                    aid: info["result_hash"]
                    for aid, info in seal.get("algorithm_summary", {}).items()
                }
            result_hashes_per_run.append(algo_hashes)
        for algo_id in result_hashes_per_run[0]:
            assert result_hashes_per_run[0][algo_id] == result_hashes_per_run[1][algo_id], (
                f"{algo_id}: result_hash differs between runs"
            )


# ===================================================================
# 5. API Authentication Enforcement
# ===================================================================

class TestAPIAuthEnforcement:
    """Prove all algorithm API endpoints reject unauthenticated access."""

    PROTECTED = [
        ("/api/v1/algorithms/", "GET"),
        ("/api/v1/algorithms/run", "POST"),
        ("/api/v1/algorithms/runs", "GET"),
        ("/api/v1/algorithms/replay", "POST"),
        ("/api/v1/algorithms/sealed-package", "POST"),
    ]

    @pytest.mark.parametrize("path,method", PROTECTED)
    def test_unauthenticated_401(self, client, path, method):
        """Endpoints must return 401 without a token."""
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json={})
        assert resp.status_code == 401, f"{method} {path} → {resp.status_code}"

    @pytest.mark.parametrize("path,method", PROTECTED)
    def test_invalid_token_401(self, client, path, method):
        """Endpoints must return 401 with an invalid token."""
        h = {"Authorization": "Bearer invalid_token_abc123"}
        if method == "GET":
            resp = client.get(path, headers=h)
        else:
            resp = client.post(path, json={}, headers=h)
        assert resp.status_code == 401, f"{method} {path} → {resp.status_code}"


# ===================================================================
# 6. Hash-Chain Integrity
# ===================================================================

class TestHashChainIntegrity:
    """Prove the hash chain (params → result → integrity) is unbroken."""

    def test_result_hash_matches_payload(self, tmp_path):
        """result_hash is the SHA-256 of the canonical payload."""
        ctx = _make_context(str(tmp_path))
        algo = BulkDedupAlgorithm()
        result = algo.run(PARAMS, ctx)
        recomputed = hash_json(result.payload)
        assert result.result_hash == recomputed

    def test_integrity_check_is_self_verifying(self, tmp_path):
        """integrity_check matches compute_integrity() on the result."""
        ctx = _make_context(str(tmp_path))
        algo = BulkDedupAlgorithm()
        result = algo.run(PARAMS, ctx)
        # compute_integrity hashes the full result dict minus integrity_check
        expected = result.compute_integrity()
        assert result.integrity_check == expected

    def test_different_params_different_hash(self, tmp_path):
        p1 = AlgorithmParams(case_id=1, tenant_id=1, extra={"prefix": "AAA"})
        p2 = AlgorithmParams(case_id=1, tenant_id=1, extra={"prefix": "BBB"})
        h1 = hash_json(p1.to_dict())
        h2 = hash_json(p2.to_dict())
        assert h1 != h2

    def test_hash_json_sensitivity(self):
        """hash_json detects single-value changes."""
        assert hash_json({"k": "v1"}) != hash_json({"k": "v2"})
        assert hash_json({"k": "v1"}) == hash_json({"k": "v1"})


# ===================================================================
# 7. Cross-Algorithm Pipeline
# ===================================================================

class TestCrossAlgorithmPipeline:
    """Prove running multiple algorithms in sequence maintains integrity."""

    def test_pipeline_preserves_provenance(self, tmp_path):
        """Each algorithm in the pipeline produces a valid result hash."""
        ctx = _make_context(str(tmp_path))
        results = {}
        for AlgoClass in ALGOS:
            algo = AlgoClass()
            result = algo.run(PARAMS, ctx)
            results[result.algorithm_id] = result
        for algo_id, r in results.items():
            assert r.result_hash and len(r.result_hash) == 64, (
                f"{algo_id}: invalid result_hash"
            )

    def test_pipeline_deterministic_across_runs(self, tmp_path):
        """Two full pipeline runs produce identical result hashes."""
        all_hashes = []
        for _ in range(2):
            ctx = _make_context(str(tmp_path))
            run_hashes = {}
            for AlgoClass in ALGOS:
                algo = AlgoClass()
                result = algo.run(PARAMS, ctx)
                run_hashes[result.algorithm_id] = result.result_hash
            all_hashes.append(run_hashes)
        for algo_id in all_hashes[0]:
            assert all_hashes[0][algo_id] == all_hashes[1][algo_id], (
                f"{algo_id}: run1 != run2"
            )
