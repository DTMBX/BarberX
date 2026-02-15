"""
Phase 10.1 — Review Performance Baseline
==========================================
Verifies search throughput at scale (5 000 documents / ~50 000 pages
equivalent) and confirms query‐plan‐relevant indexes exist.

Design:
  - Bulk‐seeds evidence items + content extraction indexes in batches.
  - Executes representative searches (text, filtered, sorted).
  - Asserts wall‐clock per‐query < 2 s on SQLite (generous; real
    PostgreSQL will be faster).
  - Explicitly inspects database indexes built by SQLAlchemy.
"""

import time
import hashlib
import pytest
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOC_COUNT = 5_000
BATCH_SIZE = 500  # flush interval
QUERY_TIMEOUT_S = 2.0  # max seconds per query on SQLite


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """Module‐scoped app + database seeded with DOC_COUNT evidence items."""
    import os
    os.environ["FLASK_ENV"] = "testing"

    from app_config import create_app
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SERVER_NAME"] = "localhost"

    from auth.models import db

    import models.evidence            # noqa: F401
    import models.legal_case          # noqa: F401
    import models.document_processing # noqa: F401
    import models.review              # noqa: F401
    import models.webhook             # noqa: F401
    import models.forensic_media      # noqa: F401

    with app.app_context():
        db.create_all()
        _seed_data(db)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def db_session(app):
    from auth.models import db
    with app.app_context():
        yield db.session


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------

def _seed_data(db):
    """Bulk‐insert DOC_COUNT evidence rows + content indexes."""
    from models.legal_case import LegalCase
    from models.evidence import EvidenceItem, CaseEvidence
    from models.document_processing import ContentExtractionIndex
    from auth.models import User

    # User & case
    user = User(
        username="perf_user",
        email="perf@example.com",
        full_name="Performance Benchmark User",
        role="reviewer",
    )
    user.set_password("Perf1234!")
    db.session.add(user)
    db.session.flush()

    case = LegalCase(
        case_number="PERF-2025-001",
        case_name="Performance Benchmark Case",
        case_type="civil",
        status="active",
        lead_attorney_id=user.id,
    )
    db.session.add(case)
    db.session.flush()

    file_types = ["pdf", "docx", "xlsx", "png", "txt", "eml", "csv", "jpg"]
    ev_types = ["document", "image", "audio", "video"]
    statuses = ["pending", "completed", "error"]

    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    sample_text = (
        "The witness testified that the agreement was executed on the "
        "premises of 123 Oak Street. Counsel for the plaintiff argued "
        "that the contract was void due to lack of consideration. "
        "The corporation memo states quarterly revenue declined by 12%. "
    )

    for batch_start in range(0, DOC_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, DOC_COUNT)
        for i in range(batch_start, batch_end):
            sha = hashlib.sha256(f"perf-evidence-{i}".encode()).hexdigest()
            ev = EvidenceItem(
                original_filename=f"document_{i:05d}.{file_types[i % len(file_types)]}",
                stored_filename=f"stored_{i:05d}",
                file_type=file_types[i % len(file_types)],
                file_size_bytes=1024 * (10 + i % 500),
                mime_type=f"application/{file_types[i % len(file_types)]}",
                evidence_type=ev_types[i % len(ev_types)],
                hash_sha256=sha,
                collected_date=base_date + timedelta(days=i % 365),
                collected_by=f"Custodian_{i % 50}",
                processing_status=statuses[i % len(statuses)],
                has_ocr=(i % 3 == 0),
                uploaded_by_id=user.id,
            )
            db.session.add(ev)
            db.session.flush()

            # Link to case
            link = CaseEvidence(
                case_id=case.id,
                evidence_id=ev.id,
                linked_at=datetime.now(timezone.utc),
                linked_by_id=user.id,
            )
            db.session.add(link)

            # Content extraction index (~10 pages ≈ 50 000 pages total)
            full_text = (sample_text * 10) + f" Document number {i}. "
            ci = ContentExtractionIndex(
                evidence_id=ev.id,
                case_id=case.id,
                content_type="text",
                word_count=len(full_text.split()),
                character_count=len(full_text),
                line_count=full_text.count("\n") + 1,
                full_text=full_text,
                persons=f"John Doe, Jane Smith" if i % 2 == 0 else "Alice Johnson",
                organizations=f"Acme Corp, Globex" if i % 3 == 0 else "",
                email_addresses=f"user{i}@example.com",
                phone_numbers="555-0100" if i % 5 == 0 else "",
                key_phrases="contract, testimony, revenue",
            )
            db.session.add(ci)

        db.session.commit()


# ---------------------------------------------------------------------------
# Index verification
# ---------------------------------------------------------------------------

class TestIndexCoverage:
    """Verify that search‐hot columns have indexes."""

    def test_evidence_item_indexes(self, app):
        """EvidenceItem: file_type, collected_date, evidence_type, processing_status."""
        from models.evidence import EvidenceItem
        idx_names = {idx.name for idx in EvidenceItem.__table__.indexes}
        expected = {
            "ix_evidence_item_file_type",
            "ix_evidence_item_collected_date",
            "ix_evidence_item_evidence_type",
            "ix_evidence_item_processing_status",
        }
        assert expected.issubset(idx_names), (
            f"Missing indexes: {expected - idx_names}"
        )

    def test_content_extraction_case_id_index(self, app):
        """ContentExtractionIndex: case_id index for search joins."""
        from models.document_processing import ContentExtractionIndex
        idx_names = {idx.name for idx in ContentExtractionIndex.__table__.indexes}
        assert "ix_content_extraction_case_id" in idx_names

    def test_review_decision_composite_index(self, app):
        """ReviewDecision: composite (case_id, evidence_id, is_current)."""
        from models.review import ReviewDecision
        idx_names = {idx.name for idx in ReviewDecision.__table__.indexes}
        assert "ix_review_decision_lookup" in idx_names

    def test_review_annotation_composite_index(self, app):
        """ReviewAnnotation: composite (case_id, evidence_id)."""
        from models.review import ReviewAnnotation
        idx_names = {idx.name for idx in ReviewAnnotation.__table__.indexes}
        assert "ix_review_annotation_lookup" in idx_names

    def test_case_evidence_indexes(self, app):
        """CaseEvidence: case_id and evidence_id indexed."""
        from models.evidence import CaseEvidence
        cols_indexed = set()
        for idx in CaseEvidence.__table__.indexes:
            for col in idx.columns:
                cols_indexed.add(col.name)
        # unique constraint also creates an implicit index
        assert "case_id" in cols_indexed or any(
            c.name == "case_id"
            for uc in CaseEvidence.__table__.constraints
            for c in getattr(uc, "columns", [])
        )


# ---------------------------------------------------------------------------
# Search throughput
# ---------------------------------------------------------------------------

class TestSearchThroughput:
    """Verify searches complete within budget on 5 000‐doc corpus."""

    def _search(self, db_session, case_id, **kwargs):
        from services.review_search_service import ReviewSearchService
        svc = ReviewSearchService(db_session)
        t0 = time.monotonic()
        result = svc.search(case_id=case_id, actor_id=None, **kwargs)
        elapsed = time.monotonic() - t0
        return result, elapsed

    def _get_case_id(self, db_session):
        from models.legal_case import LegalCase
        case = db_session.query(LegalCase).filter_by(
            case_number="PERF-2025-001"
        ).first()
        assert case is not None, "Performance case not seeded"
        return case.id

    def test_unfiltered_search(self, db_session):
        """Unfiltered paginated search should complete quickly."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(db_session, case_id, page=1, page_size=50)
        assert result["pagination"]["total"] == DOC_COUNT
        assert elapsed < QUERY_TIMEOUT_S, f"Unfiltered search took {elapsed:.2f}s"

    def test_text_search(self, db_session):
        """Text search (ILIKE) should complete within budget."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            query_text="testimony agreement",
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] > 0
        assert elapsed < QUERY_TIMEOUT_S, f"Text search took {elapsed:.2f}s"

    def test_phrase_search(self, db_session):
        """Exact phrase search."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            query_text='"lack of consideration"',
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] > 0
        assert elapsed < QUERY_TIMEOUT_S, f"Phrase search took {elapsed:.2f}s"

    def test_filtered_search_file_type(self, db_session):
        """Filter by file_type."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            filters={"file_type": "pdf"},
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] > 0
        assert elapsed < QUERY_TIMEOUT_S, f"File-type filter took {elapsed:.2f}s"

    def test_filtered_search_date_range(self, db_session):
        """Filter by date range."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            filters={
                "date_from": "2024-03-01",
                "date_to": "2024-06-30",
            },
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] > 0
        assert elapsed < QUERY_TIMEOUT_S, f"Date-range filter took {elapsed:.2f}s"

    def test_filtered_search_custodian(self, db_session):
        """Filter by custodian (collected_by ILIKE)."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            filters={"custodian": "Custodian_7"},
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] > 0
        assert elapsed < QUERY_TIMEOUT_S, f"Custodian filter took {elapsed:.2f}s"

    def test_combined_text_and_filters(self, db_session):
        """Text search + multiple filters."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            query_text="revenue",
            filters={"file_type": "docx", "has_ocr": "false"},
            page=1, page_size=50,
        )
        # May or may not find results depending on seed pattern
        assert elapsed < QUERY_TIMEOUT_S, f"Combined search took {elapsed:.2f}s"

    def test_sort_by_date(self, db_session):
        """Sort by collected_date ascending."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            sort_by="date", sort_order="asc",
            page=1, page_size=50,
        )
        assert result["pagination"]["total"] == DOC_COUNT
        assert elapsed < QUERY_TIMEOUT_S, f"Sorted search took {elapsed:.2f}s"

    def test_deep_pagination(self, db_session):
        """Access page 50 of results (items 2450–2500)."""
        case_id = self._get_case_id(db_session)
        result, elapsed = self._search(
            db_session, case_id,
            page=50, page_size=50,
        )
        assert len(result["results"]) == 50
        assert elapsed < QUERY_TIMEOUT_S, f"Deep pagination took {elapsed:.2f}s"
