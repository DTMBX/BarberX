"""
Tests for Phase 7 — Controlled External Trust & Scale
========================================================
Covers:
  - ShareLink model (token hashing, expiry, revocation, access limits)
  - ShareLinkService (create, resolve, revoke, list)
  - Share routes (create, revoke, list, portal, verify)
  - Transparency report (public-safe, counts only, no PII)
  - Multi-tenant isolation guard
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

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
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app, _db):
    yield _db.session


@pytest.fixture()
def test_user(app, _db):
    """Create a test user for authenticated operations."""
    from auth.models import User, UserRole, TierLevel
    import uuid

    user = User(
        email=f"test-{uuid.uuid4().hex[:8]}@evident.test",
        username=f"test_{uuid.uuid4().hex[:8]}",
        full_name="Test User",
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
    import uuid

    user = User(
        email=f"admin-{uuid.uuid4().hex[:8]}@evident.test",
        username=f"admin_{uuid.uuid4().hex[:8]}",
        full_name="Admin User",
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
def test_case(app, _db, test_user):
    """Create a test case with evidence."""
    from models.legal_case import LegalCase
    from models.evidence import EvidenceItem, CaseEvidence
    import uuid

    case = LegalCase(
        case_number=f"CASE-{uuid.uuid4().hex[:8]}",
        case_name="Phase 7 Test Case",
        case_type="civil",
        status="open",
        created_by_id=test_user.id,
    )
    _db.session.add(case)
    _db.session.flush()

    items = []
    for i in range(3):
        item = EvidenceItem(
            original_filename=f"test_doc_{i}.pdf",
            evidence_type="document",
            file_size_bytes=1024 * (i + 1),
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


def _login(client, user):
    """Log in a user for authenticated test requests via form POST."""
    client.post("/auth/login", data={
        "email": user.email,
        "password": "TestPass123!",
    })


# ===================================================================
# ShareLink Model Tests
# ===================================================================


class TestShareLinkModel:
    """Tests for the ShareLink model."""

    def test_generate_token_length(self):
        from models.share_link import ShareLink
        token = ShareLink.generate_token()
        assert len(token) == 64  # 32 bytes = 64 hex chars

    def test_generate_token_uniqueness(self):
        from models.share_link import ShareLink
        tokens = {ShareLink.generate_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_hash_token_is_sha256(self):
        from models.share_link import ShareLink
        token = "abcdef1234567890" * 4
        expected = hashlib.sha256(token.encode("utf-8")).hexdigest()
        assert ShareLink.hash_token(token) == expected

    def test_is_active_when_valid(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("test_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney Test",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.session.add(link)
        db.session.flush()
        assert link.is_active is True

    def test_is_active_false_when_expired(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("expired_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney Expired",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.session.add(link)
        db.session.flush()
        assert link.is_active is False

    def test_is_active_false_when_revoked(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("revoked_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney Revoked",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            revoked_at=datetime.now(timezone.utc),
        )
        db.session.add(link)
        db.session.flush()
        assert link.is_active is False

    def test_is_active_false_when_access_limit_reached(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("limited_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney Limited",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            max_access_count=5,
            access_count=5,
        )
        db.session.add(link)
        db.session.flush()
        assert link.is_active is False

    def test_evidence_ids_property(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("ids_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney IDs",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        link.evidence_ids = [3, 1, 2, 1]  # duplicates + unsorted
        db.session.add(link)
        db.session.flush()
        assert link.evidence_ids == [1, 2, 3]  # sorted, deduplicated

    def test_evidence_ids_none_means_whole_case(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("whole_case_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney WholeCase",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.session.add(link)
        db.session.flush()
        assert link.evidence_ids is None

    def test_record_access_increments(self, app, db_session, test_user, test_case):
        from models.share_link import ShareLink
        from auth.models import db

        link = ShareLink(
            token_hash=ShareLink.hash_token("counter_token"),
            case_id=test_case.id,
            scope="read_only",
            recipient_name="Attorney Counter",
            recipient_role="attorney",
            created_by_id=test_user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.session.add(link)
        db.session.flush()
        assert link.access_count == 0
        link.record_access()
        assert link.access_count == 1
        assert link.last_accessed_at is not None


# ===================================================================
# ShareLinkService Tests
# ===================================================================


class TestShareLinkService:
    """Tests for the ShareLinkService."""

    def test_create_returns_link_and_token(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService

        link, raw_token = ShareLinkService.create(
            case_id=test_case.id,
            created_by_id=test_user.id,
            recipient_name="Attorney A",
            recipient_role="attorney",
        )
        assert link.id is not None
        assert len(raw_token) == 64
        assert link.scope == "read_only"
        assert link.is_active is True

    def test_create_invalid_scope_raises(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService, ShareLinkError

        with pytest.raises(ShareLinkError, match="Invalid scope"):
            ShareLinkService.create(
                case_id=test_case.id,
                created_by_id=test_user.id,
                recipient_name="Bad Scope",
                recipient_role="attorney",
                scope="admin_full_access",
            )

    def test_create_invalid_role_raises(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService, ShareLinkError

        with pytest.raises(ShareLinkError, match="Invalid recipient_role"):
            ShareLinkService.create(
                case_id=test_case.id,
                created_by_id=test_user.id,
                recipient_name="Bad Role",
                recipient_role="hacker",
            )

    def test_create_invalid_expiry_raises(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService, ShareLinkError

        with pytest.raises(ShareLinkError, match="expires_in_days"):
            ShareLinkService.create(
                case_id=test_case.id,
                created_by_id=test_user.id,
                recipient_name="Too Long",
                recipient_role="attorney",
                expires_in_days=365,
            )

    def test_resolve_valid_token(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService

        link, raw_token = ShareLinkService.create(
            case_id=test_case.id,
            created_by_id=test_user.id,
            recipient_name="Resolve Test",
            recipient_role="attorney",
        )
        resolved = ShareLinkService.resolve(raw_token)
        assert resolved.id == link.id

    def test_resolve_invalid_token_raises(self, app, db_session):
        from services.share_link_service import ShareLinkService, ShareLinkError

        with pytest.raises(ShareLinkError, match="Invalid or unknown"):
            ShareLinkService.resolve("0" * 64)

    def test_revoke_and_resolve_fails(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService, ShareLinkError

        link, raw_token = ShareLinkService.create(
            case_id=test_case.id,
            created_by_id=test_user.id,
            recipient_name="Revoke Test",
            recipient_role="attorney",
        )
        ShareLinkService.revoke(link.id, revoked_by_id=test_user.id)

        with pytest.raises(ShareLinkError, match="revoked"):
            ShareLinkService.resolve(raw_token)

    def test_double_revoke_raises(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService, ShareLinkError

        link, _ = ShareLinkService.create(
            case_id=test_case.id,
            created_by_id=test_user.id,
            recipient_name="Double Revoke",
            recipient_role="attorney",
        )
        ShareLinkService.revoke(link.id, revoked_by_id=test_user.id)

        with pytest.raises(ShareLinkError, match="already revoked"):
            ShareLinkService.revoke(link.id, revoked_by_id=test_user.id)

    def test_list_for_case(self, app, db_session, test_user, test_case):
        from services.share_link_service import ShareLinkService

        for i in range(3):
            ShareLinkService.create(
                case_id=test_case.id,
                created_by_id=test_user.id,
                recipient_name=f"List Test {i}",
                recipient_role="attorney",
            )
        links = ShareLinkService.list_for_case(test_case.id)
        assert len(links) >= 3


# ===================================================================
# Share Routes Tests
# ===================================================================


class TestShareRoutes:
    """Tests for share-link HTTP routes."""

    def test_create_link_requires_auth(self, client):
        resp = client.post("/share/links", json={
            "case_id": 1,
            "recipient_name": "Test",
            "recipient_role": "attorney",
        })
        # Should redirect to login or return 302/401
        assert resp.status_code in (302, 401)

    def test_create_link_missing_fields(self, app, client, test_user):
        _login(client, test_user)
        resp = client.post("/share/links", json={"case_id": 1})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "Missing required fields" in data["error"]

    def test_create_link_success(self, app, client, test_user, test_case):
        _login(client, test_user)
        resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Route Test Attorney",
            "recipient_role": "attorney",
            "expires_in_days": 14,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert len(data["token"]) == 64
        assert "portal_url" in data

    def test_portal_without_token_returns_401(self, client):
        resp = client.get("/share/portal")
        assert resp.status_code == 401

    def test_portal_with_invalid_token_returns_403(self, client):
        resp = client.get("/share/portal?token=" + "a" * 64)
        assert resp.status_code == 403

    def test_portal_with_valid_token_returns_case_data(self, app, client, test_user, test_case):
        _login(client, test_user)
        create_resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Portal Test",
            "recipient_role": "attorney",
        })
        token = create_resp.get_json()["token"]

        # Portal access — no login needed
        with client.session_transaction() as sess:
            sess.clear()

        resp = client.get(f"/share/portal?token={token}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "case" in data
        assert data["case"]["case_number"] == test_case.case_number
        assert "evidence" in data
        assert len(data["evidence"]) == 3
        assert "notice" in data

    def test_portal_evidence_contains_hashes_but_no_content(self, app, client, test_user, test_case):
        _login(client, test_user)
        create_resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Hash Check",
            "recipient_role": "attorney",
        })
        token = create_resp.get_json()["token"]

        with client.session_transaction() as sess:
            sess.clear()

        resp = client.get(f"/share/portal?token={token}")
        data = resp.get_json()
        for ev in data["evidence"]:
            assert "hash_sha256" in ev
            assert "text_content" not in ev
            assert "transcript" not in ev

    def test_portal_increments_access_count(self, app, client, test_user, test_case):
        _login(client, test_user)
        create_resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Counter Check",
            "recipient_role": "attorney",
        })
        token = create_resp.get_json()["token"]

        with client.session_transaction() as sess:
            sess.clear()

        client.get(f"/share/portal?token={token}")
        client.get(f"/share/portal?token={token}")

        _login(client, test_user)
        list_resp = client.get(f"/share/links/case/{test_case.id}")
        links = list_resp.get_json()
        counter_link = [l for l in links if l["recipient_name"] == "Counter Check"]
        assert counter_link[0]["access_count"] == 2

    def test_verify_valid_token(self, app, client, test_user, test_case):
        _login(client, test_user)
        create_resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Verify Test",
            "recipient_role": "attorney",
        })
        token = create_resp.get_json()["token"]

        with client.session_transaction() as sess:
            sess.clear()

        resp = client.get(f"/share/portal/verify?token={token}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["valid"] is True

    def test_verify_invalid_token(self, client):
        resp = client.get("/share/portal/verify?token=" + "b" * 64)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["valid"] is False

    def test_revoke_link(self, app, client, test_user, test_case):
        _login(client, test_user)
        create_resp = client.post("/share/links", json={
            "case_id": test_case.id,
            "recipient_name": "Revoke Route",
            "recipient_role": "attorney",
        })
        link_id = create_resp.get_json()["id"]

        resp = client.post(f"/share/links/{link_id}/revoke")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "revoked"


# ===================================================================
# Transparency Report Tests
# ===================================================================


class TestTransparencyReport:
    """Tests for the public transparency endpoint."""

    def test_report_returns_200_no_auth(self, client):
        resp = client.get("/transparency/report")
        assert resp.status_code == 200

    def test_report_contains_counts_only(self, client):
        data = client.get("/transparency/report").get_json()
        assert "aggregate_counts" in data
        counts = data["aggregate_counts"]
        assert "cases" in counts
        assert "evidence_items" in counts
        assert "audit_entries" in counts
        # All values should be integers, not lists/dicts
        for v in counts.values():
            assert isinstance(v, int)

    def test_report_contains_no_pii(self, client):
        data = client.get("/transparency/report").get_json()
        text = json.dumps(data)
        # Ensure no emails, usernames, or case numbers leak
        assert "@" not in text or "evident" not in text.lower()
        assert "password" not in text.lower()
        assert "secret" not in text.lower()

    def test_report_has_notice(self, client):
        data = client.get("/transparency/report").get_json()
        assert "notice" in data
        assert "aggregate counts only" in data["notice"].lower()

    def test_report_has_version(self, client):
        data = client.get("/transparency/report").get_json()
        assert "version" in data

    def test_verify_instructions_returns_200(self, client):
        resp = client.get("/transparency/verify")
        assert resp.status_code == 200

    def test_verify_instructions_has_steps(self, client):
        data = client.get("/transparency/verify").get_json()
        assert "instructions" in data
        assert len(data["instructions"]) >= 3
        # Each step should have step number and description
        for step in data["instructions"]:
            assert "step" in step
            assert "description" in step

    def test_verify_instructions_has_tools(self, client):
        data = client.get("/transparency/verify").get_json()
        assert "tools" in data
        assert "linux" in data["tools"]
        assert "windows" in data["tools"]

    def test_verify_instructions_has_disclaimer(self, client):
        data = client.get("/transparency/verify").get_json()
        assert "notice" in data
        assert "not constitute legal advice" in data["notice"].lower()


# ===================================================================
# Multi-Tenant Isolation Tests
# ===================================================================


class TestTenantIsolation:
    """Tests for the multi-tenant isolation guard."""

    def test_admin_bypasses_tenant_filter(self, app, admin_user):
        from auth.tenant_isolation import _get_user_org_id
        from flask_login import login_user

        with app.test_request_context():
            login_user(admin_user)
            assert _get_user_org_id() is None  # None = no filter

    def test_tenant_filter_returns_query_for_admin(self, app, db_session, admin_user):
        from auth.tenant_isolation import tenant_filter_cases
        from models.legal_case import LegalCase
        from flask_login import login_user

        with app.test_request_context():
            login_user(admin_user)
            q = LegalCase.query
            filtered = tenant_filter_cases(q)
            # Admin gets unfiltered query
            assert str(filtered) == str(q)

    def test_tenant_case_access_decorator_allows_own_case(self, app, db_session, test_user, test_case):
        """User can access a case with no org restriction."""
        from auth.tenant_isolation import tenant_case_access
        from flask_login import login_user
        from flask import g

        @tenant_case_access
        def dummy_view(case_id):
            return "ok"

        with app.test_request_context():
            login_user(test_user)
            result = dummy_view(case_id=test_case.id)
            assert result == "ok"
            assert g.case.id == test_case.id

    def test_tenant_case_access_404_for_missing_case(self, app, db_session, test_user):
        from auth.tenant_isolation import tenant_case_access
        from flask_login import login_user

        @tenant_case_access
        def dummy_view(case_id):
            return "ok"

        with app.test_request_context():
            login_user(test_user)
            with pytest.raises(Exception) as exc_info:
                dummy_view(case_id=999999)
            assert "404" in str(exc_info.value) or exc_info.value.code == 404


# ===================================================================
# Governance Document Tests (presence + content validation)
# ===================================================================


class TestGovernanceDocs:
    """Verify governance documents exist and contain required sections."""

    def test_change_control_policy_exists(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs", "CHANGE_CONTROL_POLICY.md",
        )
        assert os.path.exists(path)

    def test_change_control_has_phase_locking(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs", "CHANGE_CONTROL_POLICY.md",
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase-Locking" in content
        assert "LOCKED" in content

    def test_change_control_has_branch_policy(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs", "CHANGE_CONTROL_POLICY.md",
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Branch Policy" in content
        assert "main" in content

    def test_change_control_has_forensic_review(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs", "CHANGE_CONTROL_POLICY.md",
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Forensic Code Review" in content
        assert "Immutability" in content
        assert "SHA-256" in content
