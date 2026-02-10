"""
Case Management & BWC Sync — Integrity Tests
==============================================
Validates:

1. CaseEvidence many-to-many: link, unlink, soft-delete, relink.
2. Case model jurisdiction metadata fields.
3. EventSyncService sealed-event enforcement.
4. EventSyncService update_sync_offset with hash recomputation.
5. EventSyncService detect_temporal_overlaps.
6. EventSyncService audit stream wiring.
7. CaseExporter end-to-end case-level export.
"""

import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone

import pytest

# ---------------------------------------------------------------------------
# App-context fixture (required for SQLAlchemy models)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    """Create a Flask application with an in-memory SQLite database."""
    from app_config import create_app
    application = create_app()
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    return application


@pytest.fixture(autouse=True)
def app_context(app):
    """Push app context and create tables for each test."""
    from auth.models import db
    with app.app_context():
        db.create_all()
        yield
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def db_session():
    from auth.models import db
    return db.session


# ---------------------------------------------------------------------------
# Model factories
# ---------------------------------------------------------------------------

@pytest.fixture
def make_case(db_session):
    """Factory to create a LegalCase record."""
    from models.legal_case import LegalCase
    from auth.models import db

    def _make(
        case_number="CASE-001",
        case_name="Test Case",
        case_type="general",
        jurisdiction="Federal",
        jurisdiction_state="NJ",
        jurisdiction_agency_type="municipal_pd",
    ):
        c = LegalCase(
            case_number=case_number,
            case_name=case_name,
            case_type=case_type,
            jurisdiction=jurisdiction,
            jurisdiction_state=jurisdiction_state,
            jurisdiction_agency_type=jurisdiction_agency_type,
        )
        db.session.add(c)
        db.session.flush()
        return c

    return _make


@pytest.fixture
def make_evidence(db_session):
    """Factory to create an EvidenceItem record."""
    from models.evidence import EvidenceItem
    from auth.models import db
    import uuid

    _counter = [0]

    def _make(
        origin_case_id=None,
        filename="test_video.mp4",
        sha256=None,
        duration_seconds=None,
    ):
        _counter[0] += 1
        ev = EvidenceItem(
            original_filename=filename,
            hash_sha256=sha256 or f"sha256_test_{_counter[0]:04d}_{'a' * 56}",
            evidence_store_id=str(uuid.uuid4()),
            origin_case_id=origin_case_id,
            duration_seconds=duration_seconds,
            evidence_type="video",
        )
        db.session.add(ev)
        db.session.flush()
        return ev

    return _make


@pytest.fixture
def make_event(db_session):
    """Factory to create an Event (CaseEvent) record."""
    from models.case_event import Event
    from auth.models import db

    def _make(case_id, label="Test Event", start_time=None):
        ev = Event(
            case_id=case_id,
            event_label=label,  # Uses __init__ alias → event_name
            event_type="incident",
            start_time=start_time or datetime.now(timezone.utc),  # → event_start
        )
        db.session.add(ev)
        db.session.flush()
        return ev

    return _make


# ============================================================================
# 1. CaseEvidence Many-to-Many
# ============================================================================


class TestCaseEvidenceLinking:
    """Verify CaseEvidence association model behavior."""

    def test_link_evidence_to_case(self, db_session, make_case, make_evidence):
        from models.evidence import CaseEvidence
        from auth.models import db

        case = make_case()
        ev = make_evidence()
        link = CaseEvidence(
            case_id=case.id,
            evidence_id=ev.id,
            link_purpose="intake",
        )
        db.session.add(link)
        db.session.flush()

        assert link.id is not None
        assert link.is_active is True
        assert case.evidence_count == 1

    def test_soft_unlink_preserves_record(self, db_session, make_case, make_evidence):
        from models.evidence import CaseEvidence
        from auth.models import db

        case = make_case()
        ev = make_evidence()
        link = CaseEvidence(
            case_id=case.id,
            evidence_id=ev.id,
            link_purpose="intake",
        )
        db.session.add(link)
        db.session.flush()

        # Soft-unlink
        link.unlinked_at = datetime.now(timezone.utc)
        db.session.flush()

        assert link.is_active is False
        assert case.evidence_count == 0  # Active count is 0

        # Record still exists in DB
        assert CaseEvidence.query.get(link.id) is not None

    def test_evidence_linked_to_multiple_cases(
        self, db_session, make_case, make_evidence
    ):
        from models.evidence import CaseEvidence
        from auth.models import db

        case_a = make_case(case_number="A-001", case_name="Case A")
        case_b = make_case(case_number="B-001", case_name="Case B")
        ev = make_evidence()

        for case in [case_a, case_b]:
            link = CaseEvidence(
                case_id=case.id,
                evidence_id=ev.id,
                link_purpose="discovery",
            )
            db.session.add(link)
        db.session.flush()

        assert case_a.evidence_count == 1
        assert case_b.evidence_count == 1
        assert len(ev.linked_cases) == 2

    def test_duplicate_link_rejected(self, db_session, make_case, make_evidence):
        """UniqueConstraint on (case_id, evidence_id) prevents duplicates."""
        from models.evidence import CaseEvidence
        from auth.models import db
        from sqlalchemy.exc import IntegrityError

        case = make_case()
        ev = make_evidence()

        link1 = CaseEvidence(case_id=case.id, evidence_id=ev.id, link_purpose="intake")
        db.session.add(link1)
        db.session.flush()

        link2 = CaseEvidence(case_id=case.id, evidence_id=ev.id, link_purpose="exhibit")
        db.session.add(link2)

        with pytest.raises(IntegrityError):
            db.session.flush()
        db.session.rollback()


# ============================================================================
# 2. Jurisdiction Metadata
# ============================================================================


class TestJurisdictionMetadata:
    """Verify jurisdiction fields persist correctly."""

    def test_jurisdiction_fields_stored(self, db_session, make_case):
        case = make_case(
            jurisdiction="State",
            jurisdiction_state="NJ",
            jurisdiction_agency_type="county_sheriff",
        )

        from models.legal_case import LegalCase
        loaded = LegalCase.query.get(case.id)
        assert loaded.jurisdiction_state == "NJ"
        assert loaded.jurisdiction_agency_type == "county_sheriff"

    def test_incident_metadata(self, db_session):
        from models.legal_case import LegalCase
        from auth.models import db

        case = LegalCase(
            case_number="INC-001",
            case_name="Incident Test",
            case_type="general",
            incident_number="RPT-2025-0001",
            incident_date=datetime(2025, 1, 15),
        )
        db.session.add(case)
        db.session.flush()

        loaded = LegalCase.query.get(case.id)
        assert loaded.incident_number == "RPT-2025-0001"
        assert loaded.incident_date.day == 15


# ============================================================================
# 3. Sealed-Event Enforcement
# ============================================================================


class TestSealedEventEnforcement:
    """Verify that sealed events reject mutation operations."""

    def test_link_to_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        from models.evidence import CaseEvidence
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        # Seal the event
        event.is_sealed = True
        db.session.flush()

        svc = EventSyncService()
        with pytest.raises(ValueError, match="sealed"):
            svc.link_evidence_to_event(event.id, ev.id)

    def test_unlink_from_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        svc.link_evidence_to_event(event.id, ev.id)

        # Now seal
        event.is_sealed = True
        db.session.flush()

        with pytest.raises(ValueError, match="sealed"):
            svc.unlink_evidence_from_event(event.id, ev.id)

    def test_sync_group_on_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        event.is_sealed = True
        db.session.flush()

        svc = EventSyncService()
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Sealed test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        assert not result.success
        assert "sealed" in result.error.lower()


# ============================================================================
# 4. Update Sync Offset with Hash Recomputation
# ============================================================================


class TestSyncOffsetUpdate:
    """Verify offset updates recompute integrity hash."""

    def test_offset_update_changes_hash(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService

        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Two-camera test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        assert result.success
        original_hash = result.integrity_hash

        # Update offset
        update = svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=750,
        )
        assert update.success
        assert update.integrity_hash != original_hash

    def test_offset_update_on_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Seal test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )

        event.is_sealed = True
        db.session.flush()

        update = svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=999,
        )
        assert not update.success
        assert "sealed" in update.error.lower()


# ============================================================================
# 5. Temporal Overlap Detection
# ============================================================================


class TestTemporalOverlapDetection:
    """Verify overlap detection between camera streams."""

    def test_overlapping_streams_detected(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService

        case = make_case()
        ev1 = make_evidence(
            origin_case_id=case.id,
            filename="cam1.mp4",
            duration_seconds=120,
        )
        ev2 = make_evidence(
            origin_case_id=case.id,
            filename="cam2.mp4",
            duration_seconds=90,
        )
        event = make_event(case.id)

        svc = EventSyncService()
        svc.link_evidence_to_event(event.id, ev1.id, temporal_offset_ms=0)
        svc.link_evidence_to_event(event.id, ev2.id, temporal_offset_ms=60_000)

        # ev1: 0ms—120000ms, ev2: 60000ms—150000ms → overlap 60000ms—120000ms
        overlaps = svc.detect_temporal_overlaps(event.id)
        assert len(overlaps) == 1
        assert overlaps[0]["overlap_ms"] == 60_000
        assert overlaps[0]["window_start_ms"] == 60_000
        assert overlaps[0]["window_end_ms"] == 120_000

    def test_non_overlapping_streams(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService

        case = make_case()
        ev1 = make_evidence(
            origin_case_id=case.id,
            filename="cam1.mp4",
            duration_seconds=60,
        )
        ev2 = make_evidence(
            origin_case_id=case.id,
            filename="cam2.mp4",
            duration_seconds=60,
        )
        event = make_event(case.id)

        svc = EventSyncService()
        svc.link_evidence_to_event(event.id, ev1.id, temporal_offset_ms=0)
        svc.link_evidence_to_event(event.id, ev2.id, temporal_offset_ms=70_000)

        # ev1: 0—60000, ev2: 70000—130000 → no overlap
        overlaps = svc.detect_temporal_overlaps(event.id)
        assert len(overlaps) == 0


# ============================================================================
# 6. Audit Stream Wiring
# ============================================================================


class TestAuditStreamWiring:
    """Verify that sync operations emit audit events when stream provided."""

    def test_create_event_emits_audit(
        self, db_session, make_case
    ):
        from services.event_sync_service import EventSyncService, SyncAuditAction
        from unittest.mock import MagicMock

        mock_audit = MagicMock()
        case = make_case()
        svc = EventSyncService(audit_stream=mock_audit)

        svc.create_event(
            case_id=case.id,
            event_label="Audit test event",
            start_time=datetime.now(timezone.utc),
        )

        mock_audit.record.assert_called_once()
        call_kwargs = mock_audit.record.call_args
        assert call_kwargs[1]["action"] == SyncAuditAction.EVENT_CREATED

    def test_link_evidence_emits_audit(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService, SyncAuditAction
        from unittest.mock import MagicMock

        mock_audit = MagicMock()
        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService(audit_stream=mock_audit)
        svc.link_evidence_to_event(event.id, ev.id)

        mock_audit.record.assert_called_once()
        call_kwargs = mock_audit.record.call_args
        assert call_kwargs[1]["action"] == SyncAuditAction.EVENT_EVIDENCE_LINKED

    def test_create_sync_group_emits_audit(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService, SyncAuditAction
        from unittest.mock import MagicMock

        mock_audit = MagicMock()
        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService(audit_stream=mock_audit)
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Audit group",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        assert result.success

        # Should have: 1 group_created + 2 member_added = 3 calls
        assert mock_audit.record.call_count == 3
        actions = [c[1]["action"] for c in mock_audit.record.call_args_list]
        assert SyncAuditAction.SYNC_GROUP_CREATED in actions
        assert actions.count(SyncAuditAction.SYNC_MEMBER_ADDED) == 2


# ============================================================================
# 7. Case-Level Export
# ============================================================================


class TestCaseExport:
    """Verify the CaseExporter produces correct ZIP structure."""

    def test_case_export_zip_structure(
        self, db_session, make_case, make_evidence, tmp_path
    ):
        from services.evidence_store import EvidenceStore
        from services.evidence_export import CaseExporter
        from models.evidence import CaseEvidence
        from auth.models import db

        # Set up evidence store with a real ingested file
        store_root = str(tmp_path / "ev_store")
        store = EvidenceStore(root=store_root)

        # Create and ingest a sample file
        sample = tmp_path / "sample.txt"
        sample.write_bytes(b"EVIDENT_CASE_EXPORT_TEST_" + (b"X" * 512))

        result = store.ingest(str(sample), original_filename="sample.txt")
        assert result.sha256

        # Create case and evidence record
        case = make_case(case_number="EXPORT-001")
        ev = make_evidence(origin_case_id=case.id, filename="sample.txt")
        ev.evidence_store_id = result.evidence_id
        ev.hash_sha256 = result.sha256

        link = CaseEvidence(case_id=case.id, evidence_id=ev.id, link_purpose="intake")
        db.session.add(link)
        db.session.flush()

        # Export
        export_dir = str(tmp_path / "exports")
        exporter = CaseExporter(store, export_dir=export_dir)
        export_result = exporter.export_case(
            case=case,
            evidence_items=[ev],
            exported_by="test@evident.info",
        )

        assert export_result.success
        assert export_result.evidence_count == 1
        assert export_result.package_sha256

        # Verify ZIP contents
        with zipfile.ZipFile(export_result.export_path, "r") as zf:
            names = zf.namelist()
            # Must contain case_manifest.json and case_integrity_report.md
            assert any("case_manifest.json" in n for n in names)
            assert any("case_integrity_report.md" in n for n in names)
            # Must contain evidence subdirectory
            assert any("evidence/" in n for n in names)
            # Must contain per-evidence manifest
            assert any("manifest.json" in n and "evidence/" in n for n in names)

        # Verify case manifest contents
        with zipfile.ZipFile(export_result.export_path, "r") as zf:
            manifest_name = [n for n in zf.namelist() if "case_manifest.json" in n][0]
            manifest = json.loads(zf.read(manifest_name))
            assert manifest["case_number"] == "EXPORT-001"
            assert manifest["evidence_count"] == 1
            assert manifest["evidence"][0]["status"] == "exported"
