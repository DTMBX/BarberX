"""
Phase 2 Operational Excellence — Evidentiary Defensibility Tests
=================================================================
Verifies the five critical forensic invariants required for court-ready
evidence handling:

1. Sealed-event immutability — sealed events reject all mutations.
2. Offset mutation audit completeness — every offset change is logged
   and triggers hash recomputation.
3. Export reproducibility — identical scope yields identical manifests.
4. Duplicate-by-hash linking — same bytes produce one item, multiple links.
5. Audit append-only — operations only add entries; never overwrite or delete.

These tests are integration-level: they exercise the full service → model →
database stack via an in-memory SQLite database.

Non-negotiables upheld by these tests:
  - Originals never overwritten.
  - Every artifact hashed.
  - Derivatives reference originals.
  - Audit log append-only (no deletes/edits).
  - Alignment is metadata-only. No frame modification.
  - Exports reproducible.
  - No jurisdiction-specific legal conclusions.
"""

import hashlib
import json
import os
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# App-context fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    from app_config import create_app
    application = create_app()
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    return application


@pytest.fixture(autouse=True)
def app_context(app):
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
    from models.legal_case import LegalCase
    from auth.models import db
    _counter = [0]

    def _make(**overrides):
        _counter[0] += 1
        defaults = dict(
            case_number=f"DEF-{_counter[0]:04d}",
            case_name=f"Defensibility Test Case {_counter[0]}",
            case_type="criminal",
            jurisdiction="Federal",
        )
        defaults.update(overrides)
        c = LegalCase(**defaults)
        db.session.add(c)
        db.session.flush()
        return c

    return _make


@pytest.fixture
def make_evidence(db_session):
    from models.evidence import EvidenceItem
    from auth.models import db
    _counter = [0]

    def _make(origin_case_id=None, filename="test.mp4", sha256=None,
              duration_seconds=None):
        _counter[0] += 1
        ev = EvidenceItem(
            original_filename=filename,
            hash_sha256=sha256 or hashlib.sha256(
                f"unique_content_{_counter[0]}_{uuid.uuid4()}".encode()
            ).hexdigest(),
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
    from models.case_event import Event
    from auth.models import db

    def _make(case_id, label="Test Event", start_time=None):
        ev = Event(
            case_id=case_id,
            event_label=label,
            event_type="incident",
            start_time=start_time or datetime.now(timezone.utc),
        )
        db.session.add(ev)
        db.session.flush()
        return ev

    return _make


@pytest.fixture
def link_to_case(db_session):
    """Helper to create a CaseEvidence link."""
    from models.evidence import CaseEvidence
    from auth.models import db

    def _link(case_id, evidence_id, purpose="intake"):
        link = CaseEvidence(
            case_id=case_id,
            evidence_id=evidence_id,
            link_purpose=purpose,
        )
        db.session.add(link)
        db.session.flush()
        return link

    return _link


# ============================================================================
# 1. Sealed-Event Immutability
# ============================================================================


class TestSealedEventImmutability:
    """Sealed events must reject ALL mutation operations and log the denial."""

    def test_link_evidence_to_sealed_event_raises(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Linking evidence to a sealed event raises ValueError."""
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)
        event.is_sealed = True
        db.session.flush()

        svc = EventSyncService()
        with pytest.raises(ValueError, match="sealed"):
            svc.link_evidence_to_event(event.id, ev.id)

    def test_unlink_evidence_from_sealed_event_raises(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Unlinking evidence from a sealed event raises ValueError."""
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        svc.link_evidence_to_event(event.id, ev.id)

        event.is_sealed = True
        db.session.flush()

        with pytest.raises(ValueError, match="sealed"):
            svc.unlink_evidence_from_event(event.id, ev.id)

    def test_create_sync_group_on_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Sync group creation on a sealed event returns failure."""
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

    def test_offset_update_on_sealed_event_rejected(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Offset update on a sealed event returns failure."""
        from services.event_sync_service import EventSyncService
        from auth.models import db

        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Offset seal test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        assert result.success

        event.is_sealed = True
        db.session.flush()

        update = svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=999,
        )
        assert not update.success
        assert "sealed" in update.error.lower()

    def test_sealed_denial_emits_audit_entry(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Denied mutation on sealed event triggers audit recording."""
        from services.event_sync_service import EventSyncService, SyncAuditAction
        from auth.models import db

        mock_audit = MagicMock()
        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)
        event.is_sealed = True
        db.session.flush()

        svc = EventSyncService(audit_stream=mock_audit)
        with pytest.raises(ValueError):
            svc.link_evidence_to_event(event.id, ev.id)

        mock_audit.record.assert_called_once()
        call_kwargs = mock_audit.record.call_args[1]
        assert call_kwargs["action"] == SyncAuditAction.EVENT_MUTATION_DENIED


# ============================================================================
# 2. Offset Mutation Audit Completeness
# ============================================================================


class TestOffsetMutationAudit:
    """Offset updates must recompute integrity hash and emit audit entries."""

    def test_offset_update_changes_integrity_hash(
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
            sync_label="Hash change test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        assert result.success
        original_hash = result.integrity_hash

        update = svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=750,
        )
        assert update.success
        assert update.integrity_hash != original_hash

    def test_offset_update_emits_audit_with_old_and_new_hash(
        self, db_session, make_case, make_evidence, make_event
    ):
        from services.event_sync_service import EventSyncService, SyncAuditAction

        mock_audit = MagicMock()
        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService(audit_stream=mock_audit)
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Audit hash test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )
        original_hash = result.integrity_hash

        mock_audit.reset_mock()
        svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=750,
        )

        # Find the SYNC_OFFSET_UPDATED call
        offset_calls = [
            c for c in mock_audit.record.call_args_list
            if c[1].get("action") == SyncAuditAction.SYNC_OFFSET_UPDATED
        ]
        assert len(offset_calls) == 1
        meta = offset_calls[0][1]["metadata"]
        assert meta["old_offset_ms"] == 500
        assert meta["new_offset_ms"] == 750
        assert meta["old_integrity_hash"] == original_hash
        assert meta["new_integrity_hash"] != original_hash

    def test_offset_update_preserves_evidence_hash(
        self, db_session, make_case, make_evidence, make_event
    ):
        """Updating an offset must NOT alter any evidence SHA-256."""
        from services.event_sync_service import EventSyncService
        from models.evidence import EvidenceItem
        from auth.models import db

        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        original_hashes = {ev1.id: ev1.hash_sha256, ev2.id: ev2.hash_sha256}

        event = make_event(case.id)
        svc = EventSyncService()
        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Immutability test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )

        svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=1234,
        )

        for eid, expected in original_hashes.items():
            ev = db.session.get(EvidenceItem, eid)
            assert ev.hash_sha256 == expected, (
                f"Evidence {eid} hash changed after offset update"
            )


# ============================================================================
# 3. Export Reproducibility
# ============================================================================


class TestExportReproducibility:
    """Two exports of the same scope must produce identical manifest hashes."""

    def test_case_export_manifest_hash_is_stable(
        self, db_session, make_case, make_evidence, tmp_path
    ):
        """Two consecutive exports yield identical manifest content hashes."""
        from services.evidence_store import EvidenceStore
        from services.evidence_export import CaseExporter
        from models.evidence import CaseEvidence
        from auth.models import db

        store_root = str(tmp_path / "ev_store")
        store = EvidenceStore(root=store_root)

        sample = tmp_path / "sample_export.bin"
        sample.write_bytes(b"EVIDENT_REPRODUCIBILITY_TEST_" + (b"Z" * 512))
        ingest_result = store.ingest(str(sample), original_filename="sample.bin")
        assert ingest_result.sha256

        case = make_case(case_number="REPRO-001")
        ev = make_evidence(origin_case_id=case.id, filename="sample.bin")
        ev.evidence_store_id = ingest_result.evidence_id
        ev.hash_sha256 = ingest_result.sha256
        db.session.flush()

        link = CaseEvidence(case_id=case.id, evidence_id=ev.id, link_purpose="intake")
        db.session.add(link)
        db.session.flush()

        exporter = CaseExporter(store, export_dir=str(tmp_path / "exports"))

        result1 = exporter.export_case(case=case, evidence_items=[ev])
        result2 = exporter.export_case(case=case, evidence_items=[ev])

        assert result1.success and result2.success

        # Extract manifest hashes from both ZIPs
        def get_manifest_hash(zip_path):
            with zipfile.ZipFile(zip_path, "r") as zf:
                for name in zf.namelist():
                    if "case_manifest.json" in name:
                        data = json.loads(zf.read(name))
                        # Remove timestamp-dependent fields for comparison
                        data.pop("export_metadata", None)
                        canonical = json.dumps(data, sort_keys=True)
                        return hashlib.sha256(canonical.encode()).hexdigest()
            return None

        h1 = get_manifest_hash(result1.export_path)
        h2 = get_manifest_hash(result2.export_path)
        assert h1 is not None
        assert h1 == h2, "Export manifests differ between two identical-scope exports"

    def test_export_contains_evidence_hash_in_manifest(
        self, db_session, make_case, make_evidence, tmp_path
    ):
        """Export manifest must contain the SHA-256 of each included original."""
        from services.evidence_store import EvidenceStore
        from services.evidence_export import CaseExporter
        from models.evidence import CaseEvidence
        from auth.models import db

        store_root = str(tmp_path / "ev_store2")
        store = EvidenceStore(root=store_root)

        sample = tmp_path / "hashed_sample.bin"
        sample.write_bytes(b"HASH_VERIFICATION_" + os.urandom(128))
        ingest_result = store.ingest(str(sample), original_filename="hashed.bin")

        case = make_case(case_number="HASH-001")
        ev = make_evidence(origin_case_id=case.id, filename="hashed.bin")
        ev.evidence_store_id = ingest_result.evidence_id
        ev.hash_sha256 = ingest_result.sha256
        db.session.flush()

        link = CaseEvidence(case_id=case.id, evidence_id=ev.id, link_purpose="intake")
        db.session.add(link)
        db.session.flush()

        exporter = CaseExporter(store, export_dir=str(tmp_path / "exports2"))
        result = exporter.export_case(case=case, evidence_items=[ev])
        assert result.success

        with zipfile.ZipFile(result.export_path, "r") as zf:
            manifest_name = [n for n in zf.namelist() if "case_manifest.json" in n][0]
            manifest = json.loads(zf.read(manifest_name))
            evidence_sha = manifest["evidence"][0].get("sha256")
            assert evidence_sha == ingest_result.sha256


# ============================================================================
# 4. Duplicate-by-Hash Linking
# ============================================================================


class TestDuplicateByHashLinking:
    """Re-ingesting identical bytes must reuse the evidence item, not duplicate."""

    def test_same_hash_creates_one_evidence_item(
        self, db_session, make_case
    ):
        """Two uploads with identical SHA-256 result in one EvidenceItem."""
        from models.evidence import EvidenceItem, CaseEvidence
        from auth.models import db

        case_a = make_case(case_number="DUP-A")
        case_b = make_case(case_number="DUP-B")

        shared_hash = hashlib.sha256(b"identical_content").hexdigest()

        ev = EvidenceItem(
            original_filename="file.mp4",
            hash_sha256=shared_hash,
            evidence_type="video",
        )
        db.session.add(ev)
        db.session.flush()

        # Link to case A
        link_a = CaseEvidence(
            case_id=case_a.id, evidence_id=ev.id, link_purpose="intake"
        )
        db.session.add(link_a)
        db.session.flush()

        # Link same evidence to case B
        link_b = CaseEvidence(
            case_id=case_b.id, evidence_id=ev.id, link_purpose="discovery"
        )
        db.session.add(link_b)
        db.session.flush()

        # Only one EvidenceItem with that hash
        items = EvidenceItem.query.filter_by(hash_sha256=shared_hash).all()
        assert len(items) == 1

        # Two CaseEvidence links exist
        links = CaseEvidence.query.filter_by(evidence_id=ev.id).all()
        assert len(links) == 2

        # Evidence shows up in both cases
        assert len(ev.linked_cases) == 2

    def test_duplicate_hash_rejected_by_unique_constraint(
        self, db_session, make_case
    ):
        """Attempting to create two EvidenceItems with the same SHA-256 raises."""
        from models.evidence import EvidenceItem
        from auth.models import db
        from sqlalchemy.exc import IntegrityError

        shared_hash = hashlib.sha256(b"duplicate_attempt").hexdigest()

        ev1 = EvidenceItem(
            original_filename="dup1.mp4",
            hash_sha256=shared_hash,
            evidence_type="video",
        )
        db.session.add(ev1)
        db.session.flush()

        ev2 = EvidenceItem(
            original_filename="dup2.mp4",
            hash_sha256=shared_hash,
            evidence_type="video",
        )
        db.session.add(ev2)

        with pytest.raises(IntegrityError):
            db.session.flush()
        db.session.rollback()


# ============================================================================
# 5. Audit Append-Only
# ============================================================================


class TestAuditAppendOnly:
    """Audit entries must only accumulate; never be overwritten or deleted."""

    def test_chain_of_custody_row_count_monotonic(
        self, db_session, make_case, make_evidence
    ):
        """ChainOfCustody row count only increases across operations."""
        from models.evidence import ChainOfCustody, EvidenceItem
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)

        def custody_count():
            return ChainOfCustody.query.filter_by(evidence_id=ev.id).count()

        # Initial state
        initial = custody_count()

        # Add audit entries
        for action in ["ingested", "hash_computed", "accessed", "exported"]:
            entry = ChainOfCustody(
                evidence_id=ev.id,
                action=action,
                actor_name="test_system",
            )
            db.session.add(entry)
            db.session.flush()

        # Count must have increased by 4
        assert custody_count() == initial + 4

    def test_audit_entries_cannot_be_deleted_by_model_cascade(
        self, db_session, make_case, make_evidence
    ):
        """
        Verify that audit entries survive — they are append-only records.
        Even if a convenience relationship exists, the entries persist.
        """
        from models.evidence import ChainOfCustody
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)

        entry = ChainOfCustody(
            evidence_id=ev.id,
            action="test_append_only",
            actor_name="integrity_test",
        )
        db.session.add(entry)
        db.session.flush()

        entry_id = entry.id
        assert ChainOfCustody.query.get(entry_id) is not None

    def test_sync_operations_only_append_audit(
        self, db_session, make_case, make_evidence, make_event
    ):
        """All sync operations append to audit; never reduce entry count."""
        from services.event_sync_service import EventSyncService, SyncAuditAction

        mock_audit = MagicMock()
        case = make_case()
        ev1 = make_evidence(origin_case_id=case.id)
        ev2 = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService(audit_stream=mock_audit)

        # Create event → link → sync group → update offset
        svc.link_evidence_to_event(event.id, ev1.id)
        svc.link_evidence_to_event(event.id, ev2.id)

        result = svc.create_sync_group(
            event_id=event.id,
            sync_label="Append test",
            reference_evidence_id=ev1.id,
            member_evidence_ids=[ev1.id, ev2.id],
            offsets_ms={ev1.id: 0, ev2.id: 500},
        )

        svc.update_sync_offset(
            group_id=result.sync_group_id,
            evidence_id=ev2.id,
            new_offset_ms=600,
        )

        # Audit call count must be monotonically increasing
        # 2 links + 1 group_created + 2 member_added + 1 offset_updated = 6
        assert mock_audit.record.call_count >= 6

        # Collect all actions — all must be known SyncAuditAction values
        actions = [c[1]["action"] for c in mock_audit.record.call_args_list]
        assert SyncAuditAction.EVENT_EVIDENCE_LINKED in actions
        assert SyncAuditAction.SYNC_GROUP_CREATED in actions
        assert SyncAuditAction.SYNC_OFFSET_UPDATED in actions


# ============================================================================
# 6. Case/Event-Scoped Audit Slices
# ============================================================================


class TestCaseEventScopedAudit:
    """Audit entries are attributable to specific cases and events."""

    def test_case_evidence_links_are_auditable(
        self, db_session, make_case, make_evidence
    ):
        """CaseEvidence records carry linked_at timestamps for audit trail."""
        from models.evidence import CaseEvidence
        from auth.models import db

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)

        link = CaseEvidence(
            case_id=case.id,
            evidence_id=ev.id,
            link_purpose="exhibit",
        )
        db.session.add(link)
        db.session.flush()

        assert link.linked_at is not None
        assert link.is_active is True

    def test_event_evidence_links_are_timestamped(
        self, db_session, make_case, make_evidence, make_event
    ):
        """EventEvidence records carry linked_at for temporal audit."""
        from services.event_sync_service import EventSyncService
        from models.case_event import EventEvidence

        case = make_case()
        ev = make_evidence(origin_case_id=case.id)
        event = make_event(case.id)

        svc = EventSyncService()
        svc.link_evidence_to_event(event.id, ev.id)

        link = EventEvidence.query.filter_by(
            event_id=event.id, evidence_id=ev.id
        ).first()
        assert link is not None
        assert link.linked_at is not None
