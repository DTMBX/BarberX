"""
Tests for Phase 8 — API Hardening & Webhook Notifications
============================================================
Covers:
  - Bearer-token authentication middleware
  - Versioned REST API /api/v1/ (cases, evidence, audit, tokens, webhooks)
  - Webhook subscription model (HMAC signing, event matching, auto-disable)
  - Webhook delivery service (dispatch, create, delete, list)
  - Rate-limit headers and usage tracking
"""

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    """Create a test Flask app with in-memory DB."""
    os.environ["FLASK_ENV"] = "testing"
    from app_config import create_app

    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["RATELIMIT_ENABLED"] = False
    yield application


@pytest.fixture(scope="module")
def _db(app):
    """Module-scoped: push app context, create tables, tear down at end."""
    from auth.models import db

    # Ensure all models are imported so create_all() sees them
    import models.webhook  # noqa: F401

    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def test_user(app, _db):
    """Create a test user."""
    from auth.models import User, UserRole, TierLevel

    user = User(
        email=f"api-test-{uuid.uuid4().hex[:8]}@evident.test",
        username=f"apitest_{uuid.uuid4().hex[:8]}",
        full_name="API Test User",
        role=UserRole.USER,
        tier=TierLevel.PRO,
        is_verified=True,
        is_active=True,
    )
    user.set_password("TestPass123!")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture()
def admin_user(app, _db):
    """Create an admin user."""
    from auth.models import User, UserRole, TierLevel

    user = User(
        email=f"api-admin-{uuid.uuid4().hex[:8]}@evident.test",
        username=f"apiadmin_{uuid.uuid4().hex[:8]}",
        full_name="API Admin",
        role=UserRole.ADMIN,
        tier=TierLevel.ADMIN,
        is_verified=True,
        is_active=True,
    )
    user.set_password("AdminPass123!")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture()
def api_token(app, _db, test_user):
    """Create a valid API token for the test user."""
    from auth.models import ApiToken

    raw = ApiToken.generate_token()
    token_obj = ApiToken(
        token=raw,
        name="test-token",
        user_id=test_user.id,
    )
    _db.session.add(token_obj)
    _db.session.commit()
    return raw, token_obj


@pytest.fixture()
def admin_token(app, _db, admin_user):
    """Create a valid API token for the admin user."""
    from auth.models import ApiToken

    raw = ApiToken.generate_token()
    token_obj = ApiToken(
        token=raw,
        name="admin-token",
        user_id=admin_user.id,
    )
    _db.session.add(token_obj)
    _db.session.commit()
    return raw, token_obj


@pytest.fixture()
def test_case(app, _db, test_user):
    """Create a test case with evidence."""
    from models.evidence import CaseEvidence, EvidenceItem
    from models.legal_case import LegalCase

    case = LegalCase(
        case_number=f"CASE-{uuid.uuid4().hex[:8]}",
        case_name="API Test Case",
        case_type="civil",
        status="open",
        created_by_id=test_user.id,
    )
    _db.session.add(case)
    _db.session.flush()

    items = []
    for i in range(3):
        item = EvidenceItem(
            original_filename=f"api_doc_{i}.pdf",
            evidence_type="document",
            file_size_bytes=2048 * (i + 1),
            hash_sha256=f"{uuid.uuid4().hex}{uuid.uuid4().hex}",
            processing_status="complete",
        )
        _db.session.add(item)
        _db.session.flush()
        items.append(item)

        link = CaseEvidence(
            case_id=case.id,
            evidence_id=item.id,
            linked_by_id=test_user.id,
            link_purpose="intake",
        )
        _db.session.add(link)

    _db.session.commit()
    case._test_items = items
    return case


def _auth_headers(raw_token):
    """Return Authorization header dict for Bearer token."""
    return {"Authorization": f"Bearer {raw_token}"}


# ===================================================================
# 1. Bearer Token Authentication Middleware
# ===================================================================


class TestApiTokenAuth:
    """Tests for the API token authentication layer."""

    def test_missing_auth_header_returns_401(self, client):
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 401
        assert "Missing" in resp.get_json()["error"]

    def test_invalid_token_returns_401(self, client):
        resp = client.get("/api/v1/cases", headers=_auth_headers("invalid-token"))
        assert resp.status_code == 401
        assert "Invalid" in resp.get_json()["error"]

    def test_expired_token_returns_401(self, app, _db, test_user, client):
        from auth.models import ApiToken

        raw = ApiToken.generate_token()
        token_obj = ApiToken(
            token=raw,
            name="expired-token",
            user_id=test_user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        _db.session.add(token_obj)
        _db.session.commit()

        resp = client.get("/api/v1/cases", headers=_auth_headers(raw))
        assert resp.status_code == 401

    def test_inactive_token_returns_401(self, app, _db, test_user, client):
        from auth.models import ApiToken

        raw = ApiToken.generate_token()
        token_obj = ApiToken(
            token=raw,
            name="inactive-token",
            user_id=test_user.id,
            is_active=False,
        )
        _db.session.add(token_obj)
        _db.session.commit()

        resp = client.get("/api/v1/cases", headers=_auth_headers(raw))
        assert resp.status_code == 401

    def test_valid_token_succeeds(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/cases", headers=_auth_headers(raw))
        assert resp.status_code == 200

    def test_token_last_used_at_updated(self, app, _db, client, api_token):
        raw, token_obj = api_token
        before = token_obj.last_used_at
        client.get("/api/v1/cases", headers=_auth_headers(raw))
        _db.session.refresh(token_obj)
        assert token_obj.last_used_at is not None
        if before is not None:
            assert token_obj.last_used_at >= before


# ===================================================================
# 2. Cases API
# ===================================================================


class TestCasesApi:
    """Tests for /api/v1/cases endpoints."""

    def test_list_cases_200(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get("/api/v1/cases", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert "cases" in data
        assert "meta" in data
        assert data["meta"]["total"] >= 1

    def test_list_cases_pagination(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get("/api/v1/cases?page=1&per_page=1", headers=_auth_headers(raw))
        data = resp.get_json()
        assert data["meta"]["per_page"] == 1
        assert len(data["cases"]) <= 1

    def test_list_cases_filter_by_status(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get("/api/v1/cases?status=open", headers=_auth_headers(raw))
        data = resp.get_json()
        for c in data["cases"]:
            assert c["status"] == "open"

    def test_get_case_200(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get(f"/api/v1/cases/{test_case.id}", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["case_number"] == test_case.case_number
        assert "evidence" in data
        assert len(data["evidence"]) == 3

    def test_get_case_404(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/cases/999999", headers=_auth_headers(raw))
        assert resp.status_code == 404

    def test_case_has_no_pii_fields(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get(f"/api/v1/cases/{test_case.id}", headers=_auth_headers(raw))
        data = resp.get_json()
        # Evidence should not contain content bytes or transcripts
        for ev in data["evidence"]:
            assert "transcript" not in ev
            assert "text_content" not in ev
            assert "notes" not in ev


# ===================================================================
# 3. Evidence API
# ===================================================================


class TestEvidenceApi:
    """Tests for /api/v1/evidence endpoints."""

    def test_list_evidence_200(self, client, api_token, test_case):
        raw, _ = api_token
        resp = client.get("/api/v1/evidence", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert "evidence" in data

    def test_get_evidence_200(self, client, api_token, test_case):
        raw, _ = api_token
        item_id = test_case._test_items[0].id
        resp = client.get(f"/api/v1/evidence/{item_id}", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["hash_sha256"] is not None

    def test_get_evidence_404(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/evidence/999999", headers=_auth_headers(raw))
        assert resp.status_code == 404

    def test_verify_evidence_hash_found(self, client, api_token, test_case):
        raw, _ = api_token
        item = test_case._test_items[0]
        resp = client.get(
            f"/api/v1/evidence/verify/{item.hash_sha256}",
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["verified"] is True
        assert data["evidence_id"] == item.id

    def test_verify_evidence_hash_not_found(self, client, api_token):
        raw, _ = api_token
        fake_hash = "a" * 64
        resp = client.get(
            f"/api/v1/evidence/verify/{fake_hash}",
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 404
        assert resp.get_json()["verified"] is False


# ===================================================================
# 4. Audit API
# ===================================================================


class TestAuditApi:
    """Tests for /api/v1/audit endpoints."""

    def test_list_audit_200(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/audit", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert "audit_trail" in data
        assert "meta" in data

    def test_audit_invalid_since_returns_400(self, client, api_token):
        raw, _ = api_token
        resp = client.get(
            "/api/v1/audit?since=not-a-date", headers=_auth_headers(raw)
        )
        assert resp.status_code == 400

    def test_evidence_audit_trail(self, app, _db, client, api_token, test_case):
        raw, _ = api_token
        # Create an audit entry for the evidence item
        from models.evidence import ChainOfCustody

        entry = ChainOfCustody(
            evidence_id=test_case._test_items[0].id,
            action="evidence.accessed",
            actor_name="test_api",
            action_timestamp=datetime.now(timezone.utc),
        )
        _db.session.add(entry)
        _db.session.commit()

        item_id = test_case._test_items[0].id
        resp = client.get(
            f"/api/v1/evidence/{item_id}/audit", headers=_auth_headers(raw)
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["audit_trail"]) >= 1


# ===================================================================
# 5. Token Management API
# ===================================================================


class TestTokenApi:
    """Tests for /api/v1/tokens endpoints."""

    def test_list_tokens(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/tokens", headers=_auth_headers(raw))
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["tokens"]) >= 1

    def test_create_token_success(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/tokens",
            json={"name": "new-test-token", "expires_in_days": 30},
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data  # Raw token returned once
        assert data["name"] == "new-test-token"

    def test_create_token_missing_name(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/tokens", json={}, headers=_auth_headers(raw)
        )
        assert resp.status_code == 400

    def test_create_token_invalid_expiry(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/tokens",
            json={"name": "bad-expiry", "expires_in_days": -5},
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 400

    def test_revoke_token(self, app, _db, client, api_token, test_user):
        from auth.models import ApiToken

        # Create a separate token to revoke
        raw_extra = ApiToken.generate_token()
        extra = ApiToken(
            token=raw_extra, name="to-revoke", user_id=test_user.id
        )
        _db.session.add(extra)
        _db.session.commit()

        raw, _ = api_token
        resp = client.delete(
            f"/api/v1/tokens/{extra.id}", headers=_auth_headers(raw)
        )
        assert resp.status_code == 200
        _db.session.refresh(extra)
        assert extra.is_active is False

    def test_revoke_nonexistent_token(self, client, api_token):
        raw, _ = api_token
        resp = client.delete(
            "/api/v1/tokens/999999", headers=_auth_headers(raw)
        )
        assert resp.status_code == 404


# ===================================================================
# 6. Webhook Model
# ===================================================================


class TestWebhookModel:
    """Tests for WebhookSubscription model."""

    def test_generate_secret_length(self):
        from models.webhook import WebhookSubscription

        secret = WebhookSubscription.generate_secret()
        assert len(secret) == 64  # 32 bytes = 64 hex chars

    def test_sign_and_verify_payload(self):
        from models.webhook import WebhookSubscription

        secret = WebhookSubscription.generate_secret()
        payload = b'{"event": "test"}'
        sig = WebhookSubscription.sign_payload(secret, payload)
        assert WebhookSubscription.verify_signature(secret, payload, sig)

    def test_verify_rejects_wrong_signature(self):
        from models.webhook import WebhookSubscription

        secret = WebhookSubscription.generate_secret()
        payload = b'{"event": "test"}'
        assert not WebhookSubscription.verify_signature(secret, payload, "wrong")

    def test_matches_event_wildcard(self, app, _db, test_user):
        from models.webhook import WebhookSubscription

        sub = WebhookSubscription(
            user_id=test_user.id,
            name="test",
            url="https://example.com/hook",
            secret="s",
            event_types="*",
            is_active=True,
        )
        assert sub.matches_event("evidence.ingested")
        assert sub.matches_event("case.created")

    def test_matches_event_specific(self, app, _db, test_user):
        from models.webhook import WebhookSubscription

        sub = WebhookSubscription(
            user_id=test_user.id,
            name="test",
            url="https://example.com/hook",
            secret="s",
            event_types="evidence.ingested,case.created",
            is_active=True,
        )
        assert sub.matches_event("evidence.ingested")
        assert not sub.matches_event("share_link.revoked")

    def test_matches_event_inactive(self, app, _db, test_user):
        from models.webhook import WebhookSubscription

        sub = WebhookSubscription(
            user_id=test_user.id,
            name="test",
            url="https://example.com/hook",
            secret="s",
            event_types="*",
            is_active=False,
        )
        assert not sub.matches_event("evidence.ingested")

    def test_record_failure_auto_disables(self, app, _db, test_user):
        from models.webhook import WebhookSubscription

        sub = WebhookSubscription(
            user_id=test_user.id,
            name="fragile",
            url="https://example.com/hook",
            secret="s",
            event_types="*",
        )
        _db.session.add(sub)
        _db.session.flush()

        for i in range(WebhookSubscription.MAX_CONSECUTIVE_FAILURES):
            sub.record_failure(f"HTTP 500 attempt {i}")

        assert sub.is_active is False
        assert sub.consecutive_failures == WebhookSubscription.MAX_CONSECUTIVE_FAILURES

    def test_record_success_resets_failures(self, app, _db, test_user):
        from models.webhook import WebhookSubscription

        sub = WebhookSubscription(
            user_id=test_user.id,
            name="recovery",
            url="https://example.com/hook",
            secret="s",
            event_types="*",
            consecutive_failures=0,
        )
        _db.session.add(sub)
        _db.session.flush()
        sub.record_failure("HTTP 503")
        sub.record_failure("HTTP 503")
        sub.record_success()
        assert sub.consecutive_failures == 0


# ===================================================================
# 7. Webhook Service
# ===================================================================


class TestWebhookService:
    """Tests for the webhook delivery service."""

    def test_create_subscription(self, app, _db, test_user):
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="svc-test",
            url="https://example.com/hook",
            event_types="evidence.ingested,case.created",
        )
        assert sub.id is not None
        assert sub.secret  # Generated, non-empty
        assert sub.is_active

    def test_create_subscription_invalid_event_type(self, app, _db, test_user):
        from services.webhook_service import WebhookService

        with pytest.raises(ValueError, match="Invalid event types"):
            WebhookService.create_subscription(
                user_id=test_user.id,
                name="bad-events",
                url="https://example.com/hook",
                event_types="totally.fake.event",
            )

    def test_list_subscriptions(self, app, _db, test_user):
        from services.webhook_service import WebhookService

        WebhookService.create_subscription(
            user_id=test_user.id,
            name="list-test",
            url="https://example.com/list",
        )
        subs = WebhookService.list_subscriptions(test_user.id)
        assert len(subs) >= 1

    def test_delete_subscription(self, app, _db, test_user):
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="to-delete",
            url="https://example.com/del",
        )
        assert WebhookService.delete_subscription(sub.id, test_user.id)

        from models.webhook import WebhookSubscription

        refreshed = _db.session.get(WebhookSubscription, sub.id)
        assert refreshed.is_active is False

    def test_delete_subscription_wrong_user(self, app, _db, test_user, admin_user):
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="no-del",
            url="https://example.com/nodel",
        )
        # Admin user trying to delete — still needs to own it
        assert not WebhookService.delete_subscription(sub.id, admin_user.id)

    def test_dispatch_calls_matching_subs(self, app, _db, test_user):
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="dispatch-test",
            url="https://example.com/dispatch",
            event_types="evidence.ingested",
        )

        with patch("services.webhook_service._deliver") as mock_deliver:
            count = WebhookService.dispatch(
                "evidence.ingested", {"evidence_id": 42}
            )
            assert count >= 1
            assert mock_deliver.called


# ===================================================================
# 8. Webhook Routes (via API)
# ===================================================================


class TestWebhookRoutes:
    """Tests for /api/v1/webhooks endpoints."""

    def test_list_webhooks_200(self, client, api_token):
        raw, _ = api_token
        resp = client.get("/api/v1/webhooks", headers=_auth_headers(raw))
        assert resp.status_code == 200
        assert "webhooks" in resp.get_json()

    def test_create_webhook_success(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/webhooks",
            json={
                "name": "Test Hook",
                "url": "https://example.com/webhook",
                "event_types": "evidence.ingested",
            },
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "secret" in data  # Returned once on creation

    def test_create_webhook_non_https_rejected(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/webhooks",
            json={
                "name": "Insecure",
                "url": "http://example.com/webhook",
            },
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 400
        assert "HTTPS" in resp.get_json()["error"]

    def test_create_webhook_missing_fields(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/webhooks",
            json={"name": "No URL"},
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 400

    def test_create_webhook_invalid_events(self, client, api_token):
        raw, _ = api_token
        resp = client.post(
            "/api/v1/webhooks",
            json={
                "name": "Bad Events",
                "url": "https://example.com/bad",
                "event_types": "made.up.event",
            },
            headers=_auth_headers(raw),
        )
        assert resp.status_code == 422

    def test_delete_webhook(self, app, _db, client, api_token, test_user):
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="to-delete-route",
            url="https://example.com/delr",
        )
        raw, _ = api_token
        resp = client.delete(
            f"/api/v1/webhooks/{sub.id}", headers=_auth_headers(raw)
        )
        assert resp.status_code == 200

    def test_delete_webhook_not_found(self, client, api_token):
        raw, _ = api_token
        resp = client.delete(
            "/api/v1/webhooks/999999", headers=_auth_headers(raw)
        )
        assert resp.status_code == 404


# ===================================================================
# 9. API Health (no auth)
# ===================================================================


class TestApiHealth:
    """Tests for /api/v1/health endpoint."""

    def test_health_no_auth_required(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["api_version"] == "v1"

    def test_health_has_version(self, client):
        resp = client.get("/api/v1/health")
        data = resp.get_json()
        assert "version" in data


# ===================================================================
# 10. Delivery Log (append-only)
# ===================================================================


class TestWebhookDeliveryLog:
    """Tests for WebhookDeliveryLog model."""

    def test_delivery_log_created_on_dispatch(self, app, _db, test_user):
        from models.webhook import WebhookDeliveryLog, WebhookSubscription
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=test_user.id,
            name="log-test",
            url="https://httpbin.org/status/500",  # will fail
            event_types="evidence.ingested",
        )

        # Mock the HTTP call to avoid real network
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"

        with patch("requests.post", return_value=mock_resp):
            WebhookService.dispatch("evidence.ingested", {"test": True})

        logs = (
            WebhookDeliveryLog.query
            .filter_by(subscription_id=sub.id)
            .all()
        )
        assert len(logs) >= 1
        assert logs[0].event_type == "evidence.ingested"
        assert logs[0].payload_hash  # non-empty SHA-256
