"""
Forensic Invariant Tests — Case + Event Models
===============================================
22 tests verifying that event management, evidence linking, and
multi-camera synchronization preserve all forensic invariants.

Invariants under test:
  1. Sync integrity hashes are deterministic and tamper-detectable.
  2. Events enforce temporal, naming, and case-scope constraints.
  3. Sync groups validate inputs and detect parameter changes.
  4. Timeline entries are derived views in chronological order.
  5. Evidence hashes are never altered by link/sync/timeline operations.
"""

import unittest
from datetime import datetime, timedelta, timezone

from app_config import create_app
from auth.models import db, User
from models.case_event import (
    CameraSyncGroup,
    CaseTimelineEntry,
    Event,
    EventEvidence,
    SyncMethod,
    TimelineEntryType,
)
from models.evidence import CaseEvidence, EvidenceItem
from models.legal_case import LegalCase
from services.event_sync_service import EventSyncService


# ====================================================================
# Base test class
# ====================================================================


class ForensicTestBase(unittest.TestCase):
    """Shared setUp / tearDown for forensic invariant tests."""

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Test user
        self.user = User(
            username='test_forensic_user',
            email='test@evident.test',
            full_name='Test User',
        )
        self.user.set_password('TestPassword123!')
        db.session.add(self.user)
        db.session.commit()

        # Test case
        self.case = LegalCase(
            case_number='TC-2025-001',
            case_name='Test Forensic Case',
            case_type='criminal',
            jurisdiction='Test District',
            created_by_id=self.user.id,
        )
        db.session.add(self.case)
        db.session.commit()

        # Test evidence items (linked to case)
        self.evidence_a = self._create_evidence('bodycam_a.mp4', 'a' * 64, self.case.id)
        self.evidence_b = self._create_evidence('bodycam_b.mp4', 'b' * 64, self.case.id)
        self.evidence_c = self._create_evidence('dashcam.mp4', 'c' * 64, self.case.id)

        self.sync_service = EventSyncService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _create_evidence(self, filename, sha256, case_id):
        item = EvidenceItem(
            original_filename=filename,
            evidence_type='video',
            hash_sha256=sha256,
            origin_case_id=case_id,
        )
        db.session.add(item)
        db.session.commit()

        link = CaseEvidence(
            case_id=case_id,
            evidence_id=item.id,
            linked_by_id=self.user.id,
            link_purpose='intake',
        )
        db.session.add(link)
        db.session.commit()
        return item

    def _create_event(self, event_name='Test Event'):
        return self.sync_service.create_event(
            case_id=self.case.id,
            event_name=event_name,
            event_start=datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
            event_end=datetime(2025, 1, 15, 15, 0, tzinfo=timezone.utc),
            created_by_user_id=self.user.id,
        )

    def _create_event_and_group(self):
        result = self._create_event()
        self.assertTrue(result.success)
        event = result.data

        # Link evidence to event
        self.sync_service.link_evidence_to_event(
            event_id=event.id,
            evidence_id=self.evidence_a.id,
            sync_offset_ms=0,
            camera_label='BWC-A',
            linked_by_user_id=self.user.id,
        )
        self.sync_service.link_evidence_to_event(
            event_id=event.id,
            evidence_id=self.evidence_b.id,
            sync_offset_ms=1500,
            camera_label='BWC-B',
            linked_by_user_id=self.user.id,
        )

        # Create sync group
        sg_result = self.sync_service.create_sync_group(
            event_id=event.id,
            evidence_ids=[self.evidence_a.id, self.evidence_b.id],
            offsets_ms={self.evidence_a.id: 0, self.evidence_b.id: 1500},
            reference_evidence_id=self.evidence_a.id,
            sync_label='Test Sync',
            sync_method=SyncMethod.MANUAL.value,
            created_by_user_id=self.user.id,
        )
        self.assertTrue(sg_result.success)
        return event, sg_result.data


# ====================================================================
# 1. Sync Integrity Hash  (4 tests)
# ====================================================================


class TestSyncIntegrityHash(ForensicTestBase):
    """Sync integrity hash must be deterministic, order-independent,
    and tamper-detectable."""

    def test_hash_determinism(self):
        """Same inputs always produce the same hash."""
        data = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1500},
        ]
        h1 = CameraSyncGroup.compute_integrity_hash(data)
        h2 = CameraSyncGroup.compute_integrity_hash(data)
        self.assertEqual(h1, h2)

    def test_hash_order_independence(self):
        """Hash is identical regardless of input order."""
        forward = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1500},
        ]
        reverse = [
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1500},
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
        ]
        self.assertEqual(
            CameraSyncGroup.compute_integrity_hash(forward),
            CameraSyncGroup.compute_integrity_hash(reverse),
        )

    def test_hash_detects_offset_change(self):
        """Changing an offset produces a different hash."""
        original = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1500},
        ]
        modified = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1501},
        ]
        self.assertNotEqual(
            CameraSyncGroup.compute_integrity_hash(original),
            CameraSyncGroup.compute_integrity_hash(modified),
        )

    def test_hash_detects_evidence_change(self):
        """Changing an evidence hash produces a different hash."""
        original = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'b' * 64, 'offset_ms': 1500},
        ]
        modified = [
            {'evidence_sha256': 'a' * 64, 'offset_ms': 0},
            {'evidence_sha256': 'c' * 64, 'offset_ms': 1500},
        ]
        self.assertNotEqual(
            CameraSyncGroup.compute_integrity_hash(original),
            CameraSyncGroup.compute_integrity_hash(modified),
        )


# ====================================================================
# 2. Event Constraints  (5 tests)
# ====================================================================


class TestEventConstraints(ForensicTestBase):
    """Events enforce temporal, naming, and case-scope constraints."""

    def test_event_requires_name(self):
        """Events reject empty names."""
        result = self.sync_service.create_event(
            case_id=self.case.id,
            event_name='',
            created_by_user_id=self.user.id,
        )
        self.assertFalse(result.success)

    def test_event_rejects_end_before_start(self):
        """Events reject end time before start time."""
        result = self.sync_service.create_event(
            case_id=self.case.id,
            event_name='Bad Time',
            event_start=datetime(2025, 1, 15, 15, 0, tzinfo=timezone.utc),
            event_end=datetime(2025, 1, 15, 14, 0, tzinfo=timezone.utc),
            created_by_user_id=self.user.id,
        )
        self.assertFalse(result.success)

    def test_event_accepts_valid_times(self):
        """Events accept valid start/end times and get UUID ids."""
        result = self._create_event()
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIsInstance(result.data.id, str)
        self.assertEqual(len(result.data.id), 36)

    def test_event_rejects_invalid_case(self):
        """Events reject non-existent case IDs."""
        result = self.sync_service.create_event(
            case_id=999999,
            event_name='Orphan Event',
            created_by_user_id=self.user.id,
        )
        self.assertFalse(result.success)

    def test_evidence_link_enforces_case_scope(self):
        """Evidence can only be linked to events in the same case."""
        other_case = LegalCase(
            case_number='TC-2025-002',
            case_name='Other Case',
            case_type='civil',
            jurisdiction='Other District',
            created_by_id=self.user.id,
        )
        db.session.add(other_case)
        db.session.commit()

        other_evidence = EvidenceItem(
            original_filename='other.mp4',
            evidence_type='video',
            hash_sha256='d' * 64,
            origin_case_id=other_case.id,
        )
        db.session.add(other_evidence)
        db.session.commit()

        link = CaseEvidence(
            case_id=other_case.id,
            evidence_id=other_evidence.id,
            linked_by_id=self.user.id,
        )
        db.session.add(link)
        db.session.commit()

        # Create event in first case
        result = self._create_event()
        self.assertTrue(result.success)
        event = result.data

        # Try to link other case's evidence — should fail
        link_result = self.sync_service.link_evidence_to_event(
            event_id=event.id,
            evidence_id=other_evidence.id,
            linked_by_user_id=self.user.id,
        )
        self.assertFalse(link_result.success)


# ====================================================================
# 3. Sync Group Lifecycle  (6 tests)
# ====================================================================


class TestSyncGroupLifecycle(ForensicTestBase):
    """Sync groups enforce integrity, validate inputs, and detect
    tampering."""

    def test_sync_group_creation(self):
        """Sync group is created with correct integrity hash."""
        event, group = self._create_event_and_group()
        self.assertIsNotNone(group)
        self.assertIsNotNone(group.integrity_hash)
        self.assertEqual(len(group.integrity_hash), 64)

    def test_sync_group_verification_passes(self):
        """Verify passes when sync data is unaltered."""
        event, group = self._create_event_and_group()
        result = self.sync_service.verify_sync_group(group.id)
        self.assertTrue(result.success)
        self.assertTrue(result.data['verified'])

    def test_sync_group_detects_tampered_offset(self):
        """Verify fails when a sync offset is altered."""
        event, group = self._create_event_and_group()

        link = EventEvidence.query.filter_by(
            event_id=event.id,
            evidence_id=self.evidence_b.id,
        ).first()
        link.sync_offset_ms = 9999
        db.session.commit()

        result = self.sync_service.verify_sync_group(group.id)
        self.assertTrue(result.success)
        self.assertFalse(result.data['verified'])

    def test_sync_group_detects_tampered_evidence_hash(self):
        """Verify fails when evidence hash is altered."""
        event, group = self._create_event_and_group()

        self.evidence_a.hash_sha256 = 'x' * 64
        db.session.commit()

        result = self.sync_service.verify_sync_group(group.id)
        self.assertTrue(result.success)
        self.assertFalse(result.data['verified'])

    def test_sync_group_requires_min_two_evidence(self):
        """Sync group creation rejects fewer than 2 evidence items."""
        result = self._create_event()
        event = result.data

        sg_result = self.sync_service.create_sync_group(
            event_id=event.id,
            evidence_ids=[self.evidence_a.id],
            offsets_ms={self.evidence_a.id: 0},
            reference_evidence_id=self.evidence_a.id,
            sync_label='Invalid Sync',
            sync_method=SyncMethod.MANUAL.value,
            created_by_user_id=self.user.id,
        )
        self.assertFalse(sg_result.success)

    def test_sync_group_requires_reference_in_list(self):
        """Sync group rejects reference evidence not in evidence list."""
        result = self._create_event()
        event = result.data

        sg_result = self.sync_service.create_sync_group(
            event_id=event.id,
            evidence_ids=[self.evidence_a.id, self.evidence_b.id],
            offsets_ms={self.evidence_a.id: 0, self.evidence_b.id: 1500},
            reference_evidence_id=self.evidence_c.id,
            sync_label='Bad Reference',
            sync_method=SyncMethod.MANUAL.value,
            created_by_user_id=self.user.id,
        )
        self.assertFalse(sg_result.success)


# ====================================================================
# 4. Timeline Derivation  (3 tests)
# ====================================================================


class TestTimelineDerivation(ForensicTestBase):
    """Timeline entries are derived from events, evidence, and audit data."""

    def test_timeline_includes_events(self):
        """Timeline includes event start/end entries."""
        result = self._create_event()
        event = result.data

        entries = self.sync_service.generate_case_timeline(self.case.id)
        event_entries = [e for e in entries if e.event_id == event.id]
        self.assertGreaterEqual(len(event_entries), 1)

    def test_timeline_includes_evidence(self):
        """Timeline includes evidence ingest entries."""
        entries = self.sync_service.generate_case_timeline(self.case.id)
        evidence_entries = [
            e for e in entries
            if e.entry_type == TimelineEntryType.EVIDENCE_INGEST.value
        ]
        self.assertGreaterEqual(len(evidence_entries), 1)

    def test_timeline_sorted_chronologically(self):
        """Timeline entries are in chronological order."""
        self._create_event()
        entries = self.sync_service.generate_case_timeline(self.case.id)
        timestamps = [e.timestamp for e in entries]
        self.assertEqual(timestamps, sorted(timestamps))


# ====================================================================
# 5. Evidence Immutability  (4 tests)
# ====================================================================


class TestEvidenceImmutability(ForensicTestBase):
    """Evidence hashes must not change through sync/link operations."""

    def test_linking_preserves_hash(self):
        """Linking evidence to an event does not alter its hash."""
        original_hash = self.evidence_a.hash_sha256

        result = self._create_event()
        event = result.data

        self.sync_service.link_evidence_to_event(
            event_id=event.id,
            evidence_id=self.evidence_a.id,
            sync_offset_ms=0,
            linked_by_user_id=self.user.id,
        )

        ev = db.session.get(EvidenceItem, self.evidence_a.id)
        self.assertEqual(ev.hash_sha256, original_hash)

    def test_sync_group_preserves_all_hashes(self):
        """Creating a sync group does not alter any evidence hash."""
        original_hashes = {
            self.evidence_a.id: self.evidence_a.hash_sha256,
            self.evidence_b.id: self.evidence_b.hash_sha256,
        }

        self._create_event_and_group()

        for eid, expected_hash in original_hashes.items():
            ev = db.session.get(EvidenceItem, eid)
            self.assertEqual(
                ev.hash_sha256, expected_hash,
                f'Hash changed for evidence {eid}',
            )

    def test_unlinking_preserves_hash(self):
        """Unlinking evidence from an event does not alter its hash."""
        original_hash = self.evidence_a.hash_sha256

        result = self._create_event()
        event = result.data

        self.sync_service.link_evidence_to_event(
            event_id=event.id,
            evidence_id=self.evidence_a.id,
            sync_offset_ms=0,
            linked_by_user_id=self.user.id,
        )
        self.sync_service.unlink_evidence_from_event(
            event_id=event.id,
            evidence_id=self.evidence_a.id,
        )

        ev = db.session.get(EvidenceItem, self.evidence_a.id)
        self.assertEqual(ev.hash_sha256, original_hash)

    def test_timeline_generation_preserves_hashes(self):
        """Generating a timeline does not alter any evidence hash."""
        original_hashes = {
            self.evidence_a.id: self.evidence_a.hash_sha256,
            self.evidence_b.id: self.evidence_b.hash_sha256,
            self.evidence_c.id: self.evidence_c.hash_sha256,
        }

        self._create_event()
        self.sync_service.generate_case_timeline(self.case.id)

        for eid, expected_hash in original_hashes.items():
            ev = db.session.get(EvidenceItem, eid)
            self.assertEqual(ev.hash_sha256, expected_hash)


if __name__ == '__main__':
    unittest.main()
