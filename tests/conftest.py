"""
Shared Test Fixtures
=====================
Provides Flask application, test client, database session, and
authenticated API fixtures for all test suites.

Also embeds the Court-Exhibit Test Report plugin, which generates
a hash-verified JSON report when --court-report is passed.
"""

import hashlib
import json
import os
import platform
import secrets
import sys
import tempfile
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest


# ===================================================================
# Court-Exhibit Test Report Plugin (inline for pytest auto-discovery)
# ===================================================================

def _canonical_json_report(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


class _CourtTestReportPlugin:
    """Collects test results and generates a court-exhibit report."""

    def __init__(self, output_dir="test-results"):
        self.output_dir = output_dir
        self.results = []
        self.start_time = None
        self.end_time = None
        self.collection_errors = []

    def pytest_sessionstart(self, session):
        self.start_time = datetime.now(timezone.utc)

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.results.append({
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration_seconds": round(report.duration, 4),
                "longrepr": str(report.longrepr)[:500] if report.failed else None,
            })
        elif report.when == "setup" and report.failed:
            self.results.append({
                "nodeid": report.nodeid,
                "outcome": "error",
                "duration_seconds": round(report.duration, 4),
                "longrepr": str(report.longrepr)[:500],
            })

    def pytest_sessionfinish(self, session, exitstatus):
        self.end_time = datetime.now(timezone.utc)
        self._write_report(exitstatus)

    def _get_algorithm_inventory(self):
        try:
            from algorithms.registry import registry
            try:
                from algorithms.bulk_dedup import BulkDedup
                from algorithms.provenance_graph import ProvenanceGraph
                from algorithms.timeline_alignment import TimelineAlignment
                from algorithms.integrity_sweep import IntegritySweep
                from algorithms.bates_generator import BatesGenerator
                from algorithms.redaction_verify import RedactionVerify
                from algorithms.access_anomaly import AccessAnomaly
            except ImportError:
                pass
            return registry.list_algorithms()
        except Exception:
            return []

    def _get_package_versions(self):
        versions = {}
        for pkg in ["flask", "sqlalchemy", "pytest", "werkzeug", "cryptography"]:
            try:
                import importlib.metadata
                versions[pkg] = importlib.metadata.version(pkg)
            except Exception:
                versions[pkg] = "unknown"
        return versions

    def _write_report(self, exitstatus):
        os.makedirs(self.output_dir, exist_ok=True)
        passed = sum(1 for r in self.results if r["outcome"] == "passed")
        failed = sum(1 for r in self.results if r["outcome"] == "failed")
        errors = sum(1 for r in self.results if r["outcome"] == "error")
        skipped = sum(1 for r in self.results if r["outcome"] == "skipped")

        payload = {
            "report_type": "court_exhibit_test_report",
            "report_version": "1.0.0",
            "generated_at": self.start_time.isoformat() if self.start_time else None,
            "completed_at": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round(
                (self.end_time - self.start_time).total_seconds(), 2
            ) if self.start_time and self.end_time else None,
            "environment": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "packages": self._get_package_versions(),
            },
            "algorithm_inventory": self._get_algorithm_inventory(),
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "exit_status": exitstatus,
                "all_passed": failed == 0 and errors == 0,
            },
            "tests": self.results,
            "collection_errors": self.collection_errors,
        }

        payload_json = _canonical_json_report(payload)
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        report = {
            "payload": payload,
            "payload_hash_sha256": payload_hash,
            "verification_note": (
                "To verify: extract 'payload', serialize with sorted keys and no whitespace, "
                "compute SHA-256. Must match payload_hash_sha256."
            ),
        }

        report_path = os.path.join(self.output_dir, "COURT_TEST_REPORT.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True, default=str)

        summary_path = os.path.join(self.output_dir, "test-summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"Evident Test Report — {self.end_time.isoformat() if self.end_time else 'unknown'}\n")
            f.write(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed} | Errors: {errors}\n")
            f.write(f"Report Hash: {payload_hash}\n")
            if failed or errors:
                f.write("\nFailures:\n")
                for r in self.results:
                    if r["outcome"] in ("failed", "error"):
                        f.write(f"  FAIL: {r['nodeid']}\n")


def pytest_addoption(parser):
    parser.addoption(
        "--court-report", action="store_true", default=False,
        help="Generate a court-exhibit test report (test-results/COURT_TEST_REPORT.json)",
    )


def pytest_configure(config):
    if config.getoption("--court-report", default=False) or os.environ.get("COURT_REPORT"):
        config.pluginmanager.register(
            _CourtTestReportPlugin(output_dir="test-results"),
            "court_test_report",
        )


# ---------------------------------------------------------------------------
# Flask app + database
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Create a Flask application configured for testing."""
    os.environ["FLASK_ENV"] = "testing"
    from app_config import create_app
    application = create_app()
    application.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost",
    })
    yield application


@pytest.fixture(scope="session")
def _db(app):
    """Create all tables once per session."""
    from auth.models import db
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def db_session(app, _db):
    """
    Provide a clean database for a test that needs Flask.

    Uses nested transactions so each test is isolated:
    changes are rolled back after the test completes.
    Request this fixture explicitly in tests that need DB access.
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()

        # Bind the session to the connection
        options = {"bind": connection, "binds": {}}
        session = _db.create_scoped_session(options=options)
        old_session = _db.session
        _db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()
        _db.session = old_session


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Push and pop an application context."""
    with app.app_context():
        yield


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_user(app, db_session):
    """Create and return a standard test user."""
    from auth.models import User, UserRole, TierLevel
    with app.app_context():
        user = User(
            email="test@evident.tech",
            username="testuser",
            full_name="Test User",
            organization="Evident QA",
            role=UserRole.USER,
            tier=TierLevel.PRO,
            is_active=True,
            is_verified=True,
        )
        user.password_hash = "pbkdf2:sha256:unused_test_hash"
        db_session.add(user)
        db_session.flush()
        return user


@pytest.fixture
def admin_user(app, db_session):
    """Create and return an admin user."""
    from auth.models import User, UserRole, TierLevel
    with app.app_context():
        user = User(
            email="admin@evident.tech",
            username="adminuser",
            full_name="Admin User",
            organization="Evident QA",
            role=UserRole.ADMIN,
            tier=TierLevel.ADMIN,
            is_active=True,
            is_verified=True,
        )
        user.password_hash = "pbkdf2:sha256:unused_test_hash"
        db_session.add(user)
        db_session.flush()
        return user


@pytest.fixture
def api_token(app, db_session, test_user):
    """Create a valid Bearer token for API access."""
    from auth.models import ApiToken
    with app.app_context():
        token_value = f"evt_test_{secrets.token_hex(16)}"
        token = ApiToken(
            user_id=test_user.id,
            token=token_value,
            name="test-ci-token",
        )
        db_session.add(token)
        db_session.flush()
        return token_value


@pytest.fixture
def auth_headers(api_token):
    """Return headers dict with Bearer token for authenticated API calls."""
    return {"Authorization": f"Bearer {api_token}"}


# ---------------------------------------------------------------------------
# Evidence fixtures (deterministic, hash-stable)
# ---------------------------------------------------------------------------

class MockEvidenceItem:
    """Minimal mock of models.evidence.EvidenceItem for algorithm tests."""
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


class MockCaseEvidence:
    """Minimal mock of models.evidence.CaseEvidence."""
    def __init__(self, case_id, evidence_id):
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.unlinked_at = None


class MockLegalCase:
    """Minimal mock of LegalCase."""
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


@pytest.fixture
def tmp_store(tmp_path):
    """Provide a temporary evidence store."""
    return MockEvidenceStore(str(tmp_path))


@pytest.fixture
def audit():
    """Provide a mock audit stream that captures events."""
    return MockAuditStream()


@pytest.fixture
def golden_items():
    """Deterministic evidence items matching tests/fixtures/golden_case.json."""
    return [
        MockEvidenceItem(
            id=1, filename="bodycam_001.mp4",
            hash_sha256="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            file_type="mp4", device_label="BWC-7139078", device_type="body_worn_camera",
            collected_date=datetime(2025, 11, 15, 14, 30, tzinfo=timezone.utc),
            duration_seconds=300,
        ),
        MockEvidenceItem(
            id=2, filename="bodycam_001.mp4",
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
            collected_date=None,
        ),
    ]


@pytest.fixture
def case_links():
    """Case-evidence links for the golden case."""
    return [
        MockCaseEvidence(1, 1),
        MockCaseEvidence(1, 2),
        MockCaseEvidence(1, 3),
        MockCaseEvidence(1, 4),
        MockCaseEvidence(1, 5),
    ]


def make_context(tmp_store, audit, items, case_links):
    """Build a mock context dict with patched DB queries."""
    mock_session = MagicMock()
    mock_session.query.return_value = MockQuery(items)
    return {
        "db_session": mock_session,
        "evidence_store": tmp_store,
        "audit_stream": audit,
        "items": items,
        "case_links": case_links,
    }
