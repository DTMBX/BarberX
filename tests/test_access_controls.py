"""
Tests for Purpose-Required Access Controls and Security Hardening
==================================================================
EPX-402 — Verifies:
  - Purpose is required for evidence downloads.
  - Invalid/missing purpose returns proper error codes.
  - Valid access is audit-recorded.
  - Rate limits are configured on auth endpoints.
  - Secure headers are present.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    """Create a test Flask app."""
    import os
    os.environ["FLASK_ENV"] = "testing"
    from app_config import create_app
    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["RATELIMIT_ENABLED"] = False  # disable for unit tests
    yield application


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def db_session(app):
    from auth.models import db
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()


@pytest.fixture
def auth_user(app, db_session):
    """Create and return a test user, logging them in."""
    from auth.models import User, UserRole, TierLevel
    with app.app_context():
        user = User.query.filter_by(email="testaccess@evident.test").first()
        if not user:
            user = User(
                email="testaccess@evident.test",
                username="testaccess",
                full_name="Test Access User",
                role=UserRole.USER,
                tier=TierLevel.PRO,
                is_verified=True,
                is_active=True,
            )
            user.set_password("TestPass123!")
            db_session.session.add(user)
            db_session.session.commit()
        return user


# ===========================================================================
# 1. Purpose-Required Decorator Unit Tests
# ===========================================================================


class TestPurposeExtraction:
    """Test purpose extraction from various request sources."""

    def test_purpose_from_query_string(self, app):
        from auth.access_control import _extract_purpose
        with app.test_request_context("/?purpose=case_review"):
            assert _extract_purpose() == "case_review"

    def test_purpose_from_json_body(self, app):
        from auth.access_control import _extract_purpose
        with app.test_request_context(
            "/",
            method="POST",
            json={"purpose": "court_filing"},
            content_type="application/json",
        ):
            assert _extract_purpose() == "court_filing"

    def test_purpose_from_header(self, app):
        from auth.access_control import _extract_purpose
        with app.test_request_context(
            "/", headers={"X-Access-Purpose": "internal_audit"}
        ):
            assert _extract_purpose() == "internal_audit"

    def test_purpose_missing_returns_none(self, app):
        from auth.access_control import _extract_purpose
        with app.test_request_context("/"):
            assert _extract_purpose() is None

    def test_purpose_normalized_to_lowercase(self, app):
        from auth.access_control import _extract_purpose
        with app.test_request_context("/?purpose=CASE_REVIEW"):
            assert _extract_purpose() == "case_review"


class TestPurposeValidation:
    """Test that valid purposes are accepted, invalid are rejected."""

    def test_all_valid_purposes_are_accepted(self):
        from auth.access_control import VALID_ACCESS_PURPOSES
        # Minimum expected purposes
        expected = {
            "case_review", "exhibit_preparation", "court_filing",
            "internal_audit", "compliance_review", "investigation",
        }
        assert expected.issubset(VALID_ACCESS_PURPOSES)

    def test_invalid_purpose_not_in_set(self):
        from auth.access_control import VALID_ACCESS_PURPOSES
        assert "curiosity" not in VALID_ACCESS_PURPOSES
        assert "" not in VALID_ACCESS_PURPOSES
        assert "hacking" not in VALID_ACCESS_PURPOSES


# ===========================================================================
# 2. Download Endpoint Denial / Acceptance Tests
# ===========================================================================


class TestDownloadAccessDenial:
    """Test that the download endpoint denies access without proper purpose."""

    def test_download_without_login_redirects(self, client, app):
        with app.app_context():
            rv = client.get("/upload/api/export/abc12345/download")
            # Should redirect to login (302) or return 401
            assert rv.status_code in (302, 401, 308)

    def test_download_without_purpose_returns_400(self, client, app, auth_user):
        with app.app_context():
            # Login first
            client.post("/auth/login", data={
                "email": "testaccess@evident.test",
                "password": "TestPass123!",
            })
            rv = client.get("/upload/api/export/abc12345/download")
            assert rv.status_code == 400
            data = rv.get_json()
            assert "purpose" in data.get("error", "").lower()

    def test_download_with_invalid_purpose_returns_422(self, client, app, auth_user):
        with app.app_context():
            client.post("/auth/login", data={
                "email": "testaccess@evident.test",
                "password": "TestPass123!",
            })
            rv = client.get(
                "/upload/api/export/abc12345/download?purpose=just_curious"
            )
            assert rv.status_code == 422
            data = rv.get_json()
            assert "invalid" in data.get("error", "").lower()

    def test_download_with_valid_purpose_proceeds(self, client, app, auth_user):
        """With valid purpose, should get 404 (no exports dir) — not 400/422."""
        with app.app_context():
            client.post("/auth/login", data={
                "email": "testaccess@evident.test",
                "password": "TestPass123!",
            })
            rv = client.get(
                "/upload/api/export/abc12345/download?purpose=case_review"
            )
            # 404 because there's no exports directory in test — but NOT 400/422
            assert rv.status_code == 404


# ===========================================================================
# 3. Audit Recording Tests
# ===========================================================================


class TestAuditOnAccess:
    """Test that successful downloads are audit-recorded."""

    def test_record_access_writes_to_audit_stream(self, app, db_session):
        """Verify record_access calls audit_stream.record with correct args."""
        from auth.access_control import record_access
        from services.audit_stream import AuditAction

        mock_audit = MagicMock()

        with app.test_request_context("/?purpose=case_review"):
            # Simulate what purpose_required sets
            from flask import request as req
            req.access_purpose = "case_review"
            req.access_action = AuditAction.DOWNLOADED

            record_access(
                audit_stream=mock_audit,
                evidence_id="test-uuid-1234",
                db_evidence_id=42,
            )

        mock_audit.record.assert_called_once()
        call_kwargs = mock_audit.record.call_args[1]
        assert call_kwargs["evidence_id"] == "test-uuid-1234"
        assert call_kwargs["action"] == AuditAction.DOWNLOADED
        assert call_kwargs["db_evidence_id"] == 42
        assert call_kwargs["details"]["purpose"] == "case_review"

    def test_downloaded_action_constant_exists(self):
        """AuditAction.DOWNLOADED must exist for download tracking."""
        from services.audit_stream import AuditAction
        assert hasattr(AuditAction, "DOWNLOADED")
        assert AuditAction.DOWNLOADED == "evidence.downloaded"


# ===========================================================================
# 4. Security Middleware Tests
# ===========================================================================


class TestSecureHeaders:
    """Test that Talisman applies secure headers."""

    def test_x_frame_options_deny(self, client, app):
        with app.app_context():
            rv = client.get("/")
            # Talisman should set X-Frame-Options
            xfo = rv.headers.get("X-Frame-Options", "")
            assert xfo.upper() in ("DENY", "SAMEORIGIN"), \
                f"X-Frame-Options not set or unexpected: {xfo}"

    def test_content_security_policy_present(self, client, app):
        with app.app_context():
            rv = client.get("/")
            csp = rv.headers.get("Content-Security-Policy", "")
            assert "default-src" in csp, "CSP header missing or empty"

    def test_x_content_type_options(self, client, app):
        with app.app_context():
            rv = client.get("/")
            xcto = rv.headers.get("X-Content-Type-Options", "")
            assert xcto == "nosniff"


class TestRateLimiterConfigured:
    """Test that rate limiter is initialized."""

    def test_limiter_instance_exists(self, app):
        from auth.security import get_limiter
        with app.app_context():
            limiter = get_limiter()
            # Limiter should be configured (may be disabled for tests)
            assert limiter is not None


class TestSessionHardening:
    """Test session cookie configuration."""

    def test_session_cookie_httponly(self, app):
        assert app.config.get("SESSION_COOKIE_HTTPONLY") is True

    def test_session_cookie_samesite(self, app):
        assert app.config.get("SESSION_COOKIE_SAMESITE") == "Lax"


# ===========================================================================
# 5. Decorator Consolidation Tests
# ===========================================================================


class TestDecoratorAvailability:
    """Verify auth decorators are importable from canonical locations."""

    def test_access_control_importable(self):
        from auth.access_control import (
            purpose_required,
            record_access,
            VALID_ACCESS_PURPOSES,
        )
        assert callable(purpose_required)
        assert callable(record_access)
        assert isinstance(VALID_ACCESS_PURPOSES, frozenset)

    def test_security_importable(self):
        from auth.security import init_security, get_limiter
        assert callable(init_security)
        assert callable(get_limiter)
