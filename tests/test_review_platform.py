"""
Phase 10 — Review Platform Tests
=================================
Tests for search correctness, review coding, tags, annotations,
batch actions, audit trail, and permissions.
"""

import json
import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create test app with in-memory database."""
    import os
    os.environ["FLASK_ENV"] = "testing"

    from app_config import create_app
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SERVER_NAME"] = "localhost"

    from auth.models import db

    # Ensure all models are imported so create_all() sees their tables
    import models.evidence            # noqa: F401
    import models.legal_case          # noqa: F401
    import models.document_processing # noqa: F401
    import models.review              # noqa: F401
    import models.webhook             # noqa: F401
    import models.forensic_media      # noqa: F401

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def db_session(app):
    from auth.models import db
    with app.app_context():
        yield db.session


@pytest.fixture
def admin_user(app, db_session):
    """Create an admin user."""
    from auth.models import User, UserRole, TierLevel

    user = User(
        email="reviewer@evident.test",
        username="reviewer",
        full_name="Test Reviewer",
        role=UserRole.ADMIN,
        tier=TierLevel.ADMIN,
        is_verified=True,
        is_active=True,
    )
    user.set_password("TestPass123!")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_case(app, db_session, admin_user):
    """Create a test case."""
    from models.legal_case import LegalCase

    case = LegalCase(
        case_number="TEST-2026-001",
        case_name="Review Test Case",
        case_type="civil",
        status="open",
        created_by_id=admin_user.id,
    )
    db_session.add(case)
    db_session.commit()
    return case


@pytest.fixture
def evidence_items(app, db_session, test_case, admin_user):
    """Create test evidence items with index entries."""
    from models.evidence import EvidenceItem, CaseEvidence
    from models.document_processing import ContentExtractionIndex

    items = []
    for i in range(5):
        ev = EvidenceItem(
            original_filename=f"document_{i + 1}.pdf",
            file_type="pdf",
            mime_type="application/pdf",
            file_size_bytes=1024 * (i + 1),
            evidence_type="document",
            hash_sha256=f"{'a' * 60}{i:04d}",
            processing_status="completed",
            has_ocr=(i < 3),
            collected_by="Officer Smith" if i < 3 else "Detective Jones",
            collected_date=datetime(2026, 1, 10 + i, tzinfo=timezone.utc),
            uploaded_by_id=admin_user.id,
        )
        db_session.add(ev)
        db_session.flush()

        # Link to case
        link = CaseEvidence(
            case_id=test_case.id,
            evidence_id=ev.id,
            linked_by_id=admin_user.id,
        )
        db_session.add(link)

        # Content index
        texts = [
            "The contract was signed on January 15th by both parties.",
            "Email correspondence regarding the settlement agreement.",
            "Confidential attorney-client privileged communication.",
            "Invoice for legal services rendered in Q4 2025.",
            "Witness statement from the deposition of John Doe.",
        ]
        idx = ContentExtractionIndex(
            evidence_id=ev.id,
            case_id=test_case.id,
            content_type="text",
            full_text=texts[i],
            word_count=len(texts[i].split()),
            persons="John Doe" if i == 4 else None,
            organizations="Acme Corp" if i == 3 else None,
            email_addresses="contact@acme.com" if i == 1 else None,
            is_indexed=True,
        )
        db_session.add(idx)
        items.append(ev)

    db_session.commit()
    return items


@pytest.fixture
def logged_in_client(app, admin_user):
    """Flask test client with logged-in session."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
    return client


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

class TestReviewModels:
    """Tests for review model integrity."""

    def test_review_decision_creation(self, app, db_session, admin_user, test_case, evidence_items):
        from models.review import ReviewDecision, ReviewCode

        decision = ReviewDecision(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            review_code=ReviewCode.RESPONSIVE,
            reviewer_id=admin_user.id,
            reviewer_note="Clearly relevant to the case.",
            is_current=True,
        )
        db_session.add(decision)
        db_session.commit()

        assert decision.id is not None
        assert decision.review_code == "responsive"
        assert decision.is_current is True
        d = decision.to_dict()
        assert d["review_code"] == "responsive"
        assert d["reviewer_note"] == "Clearly relevant to the case."

    def test_review_decision_supersede(self, app, db_session, admin_user, test_case, evidence_items):
        from models.review import ReviewDecision, ReviewCode

        old = ReviewDecision(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            review_code=ReviewCode.RESPONSIVE,
            reviewer_id=admin_user.id,
            is_current=True,
        )
        db_session.add(old)
        db_session.flush()

        new = ReviewDecision(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            review_code=ReviewCode.PRIVILEGED,
            reviewer_id=admin_user.id,
            is_current=True,
        )
        db_session.add(new)
        db_session.flush()

        old.is_current = False
        old.superseded_by_id = new.id
        db_session.commit()

        assert old.is_current is False
        assert new.is_current is True
        assert old.superseded_by_id == new.id

    def test_annotation_creation(self, app, db_session, admin_user, test_case, evidence_items):
        from models.review import ReviewAnnotation

        note = ReviewAnnotation(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            content="Notable inconsistency in dates mentioned.",
            annotation_type="note",
            page_number=3,
            author_id=admin_user.id,
        )
        db_session.add(note)
        db_session.commit()

        assert note.id is not None
        assert note.is_deleted is False
        d = note.to_dict()
        assert d["content"] == "Notable inconsistency in dates mentioned."
        assert d["page_number"] == 3

    def test_annotation_soft_delete(self, app, db_session, admin_user, test_case, evidence_items):
        from models.review import ReviewAnnotation

        note = ReviewAnnotation(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            content="To be deleted.",
            author_id=admin_user.id,
        )
        db_session.add(note)
        db_session.commit()

        note.is_deleted = True
        note.deleted_at = datetime.now(timezone.utc)
        db_session.commit()

        assert note.is_deleted is True
        assert note.deleted_at is not None

    def test_review_audit_event(self, app, db_session, admin_user, test_case, evidence_items):
        from models.review import ReviewAuditEvent

        event = ReviewAuditEvent(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            action="review.coded",
            actor_id=admin_user.id,
            details_json=json.dumps({"review_code": "responsive"}),
            ip_address="127.0.0.1",
        )
        db_session.add(event)
        db_session.commit()

        assert event.id is not None
        assert event.details == {"review_code": "responsive"}
        d = event.to_dict()
        assert d["action"] == "review.coded"

    def test_saved_search(self, app, db_session, admin_user, test_case):
        from models.review import SavedSearch

        ss = SavedSearch(
            case_id=test_case.id,
            user_id=admin_user.id,
            name="Privileged docs",
            query_text="attorney-client",
            filters_json=json.dumps({"file_type": "pdf", "has_ocr": True}),
        )
        db_session.add(ss)
        db_session.commit()

        assert ss.filters == {"file_type": "pdf", "has_ocr": True}
        d = ss.to_dict()
        assert d["name"] == "Privileged docs"

    def test_review_code_constants(self):
        from models.review import ReviewCode

        assert len(ReviewCode.ALL) == 5
        assert "responsive" in ReviewCode.ALL
        assert "non_responsive" in ReviewCode.ALL
        assert "privileged" in ReviewCode.ALL
        assert "hot" in ReviewCode.ALL
        assert "irrelevant" in ReviewCode.ALL


# ---------------------------------------------------------------------------
# Search Service Tests
# ---------------------------------------------------------------------------

class TestReviewSearchService:
    """Tests for search correctness."""

    def test_basic_search(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            query_text="contract",
            actor_id=admin_user.id,
        )

        assert result["pagination"]["total_results"] >= 1
        filenames = [r["original_filename"] for r in result["results"]]
        assert "document_1.pdf" in filenames

    def test_phrase_search(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            query_text='"settlement agreement"',
            actor_id=admin_user.id,
        )

        assert result["pagination"]["total_results"] >= 1
        filenames = [r["original_filename"] for r in result["results"]]
        assert "document_2.pdf" in filenames

    def test_or_search(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            query_text="contract OR invoice",
            actor_id=admin_user.id,
        )

        assert result["pagination"]["total_results"] >= 2

    def test_filter_by_file_type(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            filters={"file_type": "pdf"},
            actor_id=admin_user.id,
        )

        assert result["pagination"]["total_results"] == 5

    def test_filter_has_ocr(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            filters={"has_ocr": True},
            actor_id=admin_user.id,
        )

        # Items 0, 1, 2 have has_ocr=True
        assert result["pagination"]["total_results"] == 3

    def test_filter_custodian(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            filters={"custodian": "Jones"},
            actor_id=admin_user.id,
        )

        # Items 3, 4 have collected_by="Detective Jones"
        assert result["pagination"]["total_results"] == 2

    def test_filter_date_range(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            filters={"date_from": "2026-01-12", "date_to": "2026-01-14"},
            actor_id=admin_user.id,
        )

        # Items 2 (Jan 12), 3 (Jan 13), 4 (Jan 14) = 3
        assert result["pagination"]["total_results"] == 3

    def test_pagination(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            page=1,
            page_size=2,
            actor_id=admin_user.id,
        )

        assert len(result["results"]) == 2
        assert result["pagination"]["total_results"] == 5
        assert result["pagination"]["total_pages"] == 3
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_prev"] is False

    def test_deterministic_sort(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        r1 = svc.search(case_id=test_case.id, sort_by="filename", sort_order="asc", actor_id=admin_user.id)
        r2 = svc.search(case_id=test_case.id, sort_by="filename", sort_order="asc", actor_id=admin_user.id)

        ids1 = [r["evidence_id"] for r in r1["results"]]
        ids2 = [r["evidence_id"] for r in r2["results"]]
        assert ids1 == ids2

    def test_search_audit_logged(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService
        from models.review import ReviewAuditEvent

        svc = ReviewSearchService(db_session)
        svc.search(case_id=test_case.id, query_text="contract", actor_id=admin_user.id)

        events = ReviewAuditEvent.query.filter_by(
            case_id=test_case.id, action="review.search"
        ).all()
        assert len(events) >= 1
        assert "contract" in events[-1].details.get("query", "")

    def test_empty_query_returns_all(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(case_id=test_case.id, actor_id=admin_user.id)

        assert result["pagination"]["total_results"] == 5

    def test_filter_uncoded(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService
        from models.review import ReviewDecision

        # Code one item
        d = ReviewDecision(
            case_id=test_case.id,
            evidence_id=evidence_items[0].id,
            review_code="responsive",
            reviewer_id=admin_user.id,
            is_current=True,
        )
        db_session.add(d)
        db_session.commit()

        svc = ReviewSearchService(db_session)
        result = svc.search(
            case_id=test_case.id,
            filters={"uncoded": True},
            actor_id=admin_user.id,
        )

        assert result["pagination"]["total_results"] == 4

    def test_snippet_generation(self, app, db_session, admin_user, test_case, evidence_items):
        from services.review_search_service import ReviewSearchService

        svc = ReviewSearchService(db_session)
        result = svc.search(case_id=test_case.id, query_text="contract", actor_id=admin_user.id)

        matching = [r for r in result["results"] if r["original_filename"] == "document_1.pdf"]
        assert len(matching) == 1
        assert "contract" in matching[0]["snippet"].lower()


# ---------------------------------------------------------------------------
# API Route Tests
# ---------------------------------------------------------------------------

class TestReviewAPIRoutes:
    """Tests for review API endpoints."""

    def test_search_requires_case_id(self, app, logged_in_client):
        resp = logged_in_client.get("/api/v1/review/search")
        assert resp.status_code == 400
        assert b"case_id" in resp.data

    def test_search_returns_results(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.get(f"/api/v1/review/search?case_id={test_case.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert "pagination" in data

    def test_search_with_query(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.get(f"/api/v1/review/search?case_id={test_case.id}&q=contract")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pagination"]["total_results"] >= 1

    def test_apply_review_code(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.post(
            "/api/v1/review/code",
            json={
                "case_id": test_case.id,
                "evidence_id": evidence_items[0].id,
                "review_code": "responsive",
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["decision"]["review_code"] == "responsive"

    def test_invalid_review_code_rejected(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.post(
            "/api/v1/review/code",
            json={
                "case_id": test_case.id,
                "evidence_id": evidence_items[0].id,
                "review_code": "invalid_code",
            },
        )
        assert resp.status_code == 400
        assert b"Invalid review_code" in resp.data

    def test_batch_code(self, app, logged_in_client, test_case, evidence_items):
        ids = [evidence_items[0].id, evidence_items[1].id, evidence_items[2].id]
        resp = logged_in_client.post(
            "/api/v1/review/code/batch",
            json={
                "case_id": test_case.id,
                "evidence_ids": ids,
                "review_code": "non_responsive",
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["applied_count"] == 3
        assert data["batch_id"] is not None

    def test_decision_history(self, app, logged_in_client, test_case, evidence_items):
        # Apply two decisions to create history
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id, "evidence_id": evidence_items[0].id, "review_code": "responsive",
        })
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id, "evidence_id": evidence_items[0].id, "review_code": "privileged",
        })

        resp = logged_in_client.get(
            f"/api/v1/review/evidence/{evidence_items[0].id}/decisions?case_id={test_case.id}"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["decisions"]) == 2

    def test_create_and_list_tags(self, app, logged_in_client, test_case):
        # Create
        resp = logged_in_client.post("/api/v1/review/tags", json={
            "case_id": test_case.id, "name": "Key Document", "color": "#ef4444",
        })
        assert resp.status_code == 201
        tag_id = resp.get_json()["id"]

        # List
        resp = logged_in_client.get(f"/api/v1/review/tags?case_id={test_case.id}")
        assert resp.status_code == 200
        tags = resp.get_json()["tags"]
        assert len(tags) >= 1
        assert any(t["name"] == "Key Document" for t in tags)

    def test_apply_and_remove_tag(self, app, logged_in_client, test_case, evidence_items):
        # Create tag
        resp = logged_in_client.post("/api/v1/review/tags", json={
            "case_id": test_case.id, "name": "Important", "color": "#22c55e",
        })
        tag_id = resp.get_json()["id"]

        # Apply
        resp = logged_in_client.post("/api/v1/review/tag", json={
            "case_id": test_case.id, "evidence_ids": [evidence_items[0].id], "tag_id": tag_id,
        })
        assert resp.status_code == 200
        assert resp.get_json()["applied_count"] == 1

        # Remove
        resp = logged_in_client.delete("/api/v1/review/tag", json={
            "case_id": test_case.id, "evidence_ids": [evidence_items[0].id], "tag_id": tag_id,
        })
        assert resp.status_code == 200
        assert resp.get_json()["removed_count"] == 1

    def test_create_annotation(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.post("/api/v1/review/annotations", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "content": "Check date discrepancy on page 3.",
            "page_number": 3,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["annotation"]["content"] == "Check date discrepancy on page 3."

    def test_list_annotations(self, app, logged_in_client, test_case, evidence_items):
        # Create two annotations
        for content in ["Note A", "Note B"]:
            logged_in_client.post("/api/v1/review/annotations", json={
                "case_id": test_case.id,
                "evidence_id": evidence_items[0].id,
                "content": content,
            })

        resp = logged_in_client.get(
            f"/api/v1/review/annotations?case_id={test_case.id}&evidence_id={evidence_items[0].id}"
        )
        assert resp.status_code == 200
        assert len(resp.get_json()["annotations"]) == 2

    def test_update_annotation(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.post("/api/v1/review/annotations", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "content": "Original note.",
        })
        ann_id = resp.get_json()["annotation"]["id"]

        resp = logged_in_client.put(f"/api/v1/review/annotations/{ann_id}", json={
            "content": "Updated note.",
        })
        assert resp.status_code == 200
        assert resp.get_json()["annotation"]["content"] == "Updated note."

    def test_delete_annotation_soft(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.post("/api/v1/review/annotations", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "content": "To be deleted.",
        })
        ann_id = resp.get_json()["annotation"]["id"]

        resp = logged_in_client.delete(f"/api/v1/review/annotations/{ann_id}")
        assert resp.status_code == 200

        # Should not appear in list
        resp = logged_in_client.get(
            f"/api/v1/review/annotations?case_id={test_case.id}&evidence_id={evidence_items[0].id}"
        )
        assert len(resp.get_json()["annotations"]) == 0

    def test_evidence_detail(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.get(
            f"/api/v1/review/evidence/{evidence_items[0].id}?case_id={test_case.id}"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["evidence_id"] == evidence_items[0].id
        assert data["original_filename"] == "document_1.pdf"

    def test_evidence_text(self, app, logged_in_client, test_case, evidence_items):
        resp = logged_in_client.get(
            f"/api/v1/review/evidence/{evidence_items[0].id}/text?case_id={test_case.id}"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "contract" in data["text"].lower()

    def test_review_audit_trail(self, app, logged_in_client, test_case, evidence_items):
        # Perform a coded action
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "review_code": "hot",
        })

        resp = logged_in_client.get(f"/api/v1/review/audit?case_id={test_case.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["events"]) >= 1
        actions = [e["action"] for e in data["events"]]
        assert "review.coded" in actions

    def test_evidence_history(self, app, logged_in_client, test_case, evidence_items):
        # Code + annotate
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "review_code": "responsive",
        })
        logged_in_client.post("/api/v1/review/annotations", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "content": "Test note for history.",
        })

        resp = logged_in_client.get(
            f"/api/v1/review/evidence/{evidence_items[0].id}/history?case_id={test_case.id}"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["decisions"]) >= 1
        assert len(data["annotations"]) >= 1
        assert len(data["audit_events"]) >= 1

    def test_review_stats(self, app, logged_in_client, test_case, evidence_items):
        # Code some items
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[0].id,
            "review_code": "responsive",
        })
        logged_in_client.post("/api/v1/review/code", json={
            "case_id": test_case.id,
            "evidence_id": evidence_items[1].id,
            "review_code": "privileged",
        })

        resp = logged_in_client.get(f"/api/v1/review/stats?case_id={test_case.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_evidence"] == 5
        assert data["coded"] == 2
        assert data["uncoded"] == 3
        assert data["by_code"]["responsive"] == 1
        assert data["by_code"]["privileged"] == 1

    def test_unauthenticated_request_rejected(self, app):
        client = app.test_client()
        resp = client.get("/api/v1/review/search?case_id=1")
        assert resp.status_code in (401, 302)  # 401 for API, 302 for redirect to login


# ---------------------------------------------------------------------------
# UI Route Tests
# ---------------------------------------------------------------------------

class TestReviewUIRoutes:
    """Tests for review page routes."""

    def test_review_index_requires_login(self, app):
        client = app.test_client()
        resp = client.get("/review/")
        assert resp.status_code in (302, 401)

    def test_review_workspace_loads(self, app, logged_in_client, test_case):
        resp = logged_in_client.get(f"/review/case/{test_case.id}")
        assert resp.status_code == 200
        assert b"Review" in resp.data
        assert bytes(test_case.case_name, "utf-8") in resp.data

    def test_review_workspace_404_for_missing_case(self, app, logged_in_client):
        resp = logged_in_client.get("/review/case/99999")
        assert resp.status_code == 404
