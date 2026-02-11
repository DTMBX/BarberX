"""
Tests for Health Endpoints and Structured Logging
====================================================
Phase 6 — Verifies:
  - /health/live returns 200 with status "ok".
  - /health/ready returns 200 when DB is reachable, 503 otherwise.
  - /health/info returns version, environment, uptime.
  - None of the health endpoints require authentication.
  - Structured logging assigns request_id to every request.
  - X-Request-ID header is present on every response.
  - JSON log formatter produces valid JSON in production mode.
"""

import json
import logging
import os
import pytest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    """Create a test Flask app."""
    os.environ["FLASK_ENV"] = "testing"
    from app_config import create_app

    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["RATELIMIT_ENABLED"] = False

    with application.app_context():
        from auth.models import db
        db.create_all()
        yield application


@pytest.fixture()
def client(app):
    return app.test_client()


# ===================================================================
# Health endpoint tests
# ===================================================================


class TestHealthLive:
    """Tests for /health/live — liveness probe."""

    def test_returns_200(self, client):
        resp = client.get("/health/live")
        assert resp.status_code == 200

    def test_status_ok(self, client):
        data = client.get("/health/live").get_json()
        assert data["status"] == "ok"

    def test_has_timestamp(self, client):
        data = client.get("/health/live").get_json()
        assert "timestamp" in data
        # ISO-8601 should contain a 'T' separator
        assert "T" in data["timestamp"]

    def test_no_auth_required(self, client):
        """Liveness must work without any session or token."""
        resp = client.get("/health/live")
        assert resp.status_code == 200


class TestHealthReady:
    """Tests for /health/ready — readiness probe."""

    def test_returns_200_when_db_ok(self, client):
        resp = client.get("/health/ready")
        assert resp.status_code == 200

    def test_status_ok(self, client):
        data = client.get("/health/ready").get_json()
        assert data["status"] == "ok"
        assert data["checks"]["database"]["status"] == "ok"

    def test_returns_503_when_db_fails(self, app, client):
        """Simulate DB failure — readiness should report degraded."""
        from auth.models import db

        original_execute = db.session.execute

        def _fail(*a, **kw):
            raise RuntimeError("simulated DB failure")

        with patch.object(db.session, "execute", side_effect=_fail):
            resp = client.get("/health/ready")
            assert resp.status_code == 503
            data = resp.get_json()
            assert data["status"] == "degraded"
            assert data["checks"]["database"]["status"] == "fail"
            assert "error" in data["checks"]["database"]

    def test_no_auth_required(self, client):
        resp = client.get("/health/ready")
        assert resp.status_code == 200


class TestHealthInfo:
    """Tests for /health/info — build metadata."""

    def test_returns_200(self, client):
        resp = client.get("/health/info")
        assert resp.status_code == 200

    def test_has_version(self, client):
        data = client.get("/health/info").get_json()
        assert "version" in data
        # Version should look like a semver-ish string
        assert data["version"] != ""

    def test_has_environment(self, client):
        data = client.get("/health/info").get_json()
        assert "environment" in data

    def test_has_uptime(self, client):
        data = client.get("/health/info").get_json()
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_no_auth_required(self, client):
        resp = client.get("/health/info")
        assert resp.status_code == 200


# ===================================================================
# Structured logging tests
# ===================================================================


class TestStructuredLogging:
    """Tests for the structured logging infrastructure."""

    def test_request_id_assigned(self, app, client):
        """Every request should get a unique request_id in flask.g."""
        with app.test_request_context("/health/live"):
            app.preprocess_request()
            from flask import g
            assert hasattr(g, "request_id")
            assert len(g.request_id) == 32  # hex UUID without dashes

    def test_request_id_in_response_header(self, client):
        """X-Request-ID header should appear on every response."""
        resp = client.get("/health/live")
        assert "X-Request-ID" in resp.headers
        assert len(resp.headers["X-Request-ID"]) == 32

    def test_request_ids_are_unique(self, client):
        """Consecutive requests should get different IDs."""
        r1 = client.get("/health/live")
        r2 = client.get("/health/live")
        assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]

    def test_json_formatter_produces_valid_json(self):
        """The _JSONFormatter should emit parseable JSON."""
        from services.structured_logging import _JSONFormatter

        formatter = _JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"
        assert parsed["message"] == "hello world"
        assert "timestamp" in parsed

    def test_json_formatter_includes_exception(self):
        """Exception info should be included when present."""
        from services.structured_logging import _JSONFormatter
        import traceback
        import sys

        formatter = _JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="failure",
            args=(),
            exc_info=exc_info,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]


# ===================================================================
# Audit report script tests (import validation)
# ===================================================================


class TestAuditReportImport:
    """Verify audit_report.py is importable and has expected commands."""

    def test_importable(self):
        import importlib
        mod = importlib.import_module("scripts.audit_report")
        assert hasattr(mod, "main")
        assert hasattr(mod, "cmd_activity")
        assert hasattr(mod, "cmd_evidence")
        assert hasattr(mod, "cmd_actors")
        assert hasattr(mod, "cmd_exports")
