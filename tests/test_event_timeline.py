"""
Forensic Invariant Tests — Event Timeline Builder
==================================================
Verifies that the EventTimelineBuilder service preserves all
forensic invariants required for court-admissible timeline
alignment.

Invariants under test:
  1. Timeline hash is deterministic (same inputs → same hash).
  2. Hash changes when offsets change (tamper-detectable).
  3. Hash excludes generated_at (reproducible across calls).
  4. Audit entry is recorded for every successful build.
  5. Non-video evidence is handled gracefully (no crash).
  6. Empty events produce a clear failure result.
  7. Missing events produce a clear failure result.
  8. Duration extraction falls back correctly.
  9. Tracks are sorted anchor-first then by offset.
  10. Metadata-only notice is always present.
  11. No original evidence is altered by timeline build.
"""

import hashlib
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app_config import create_app
from auth.models import db, User
from models.case_event import Event, EventEvidence
from models.evidence import CaseEvidence, EvidenceItem
from models.legal_case import LegalCase
from services.event_timeline import EventTimelineBuilder, TimelineBuildResult


# ====================================================================
# Base
# ====================================================================


class TimelineTestBase(unittest.TestCase):
    """Shared setUp / tearDown for timeline tests."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # User
        self.user = User(
            username="timeline_tester",
            email="timeline@evident.test",
            full_name="Timeline Tester",
        )
        self.user.set_password("TestPassword123!")
        db.session.add(self.user)
        db.session.commit()

        # Case
        self.case = LegalCase(
            case_number="TL-2025-001",
            case_name="Timeline Test Case",
            case_type="criminal",
            jurisdiction="Test District",
            created_by_id=self.user.id,
        )
        db.session.add(self.case)
        db.session.commit()

        self.builder = EventTimelineBuilder()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _evidence(self, filename, sha256, duration_seconds=None, file_type="mp4",
                  mime_type="video/mp4", device_label=None):
        """Create an EvidenceItem + CaseEvidence link."""
        item = EvidenceItem(
            original_filename=filename,
            evidence_type="video",
            hash_sha256=sha256,
            origin_case_id=self.case.id,
            duration_seconds=duration_seconds,
            file_type=file_type,
            mime_type=mime_type,
            device_label=device_label,
        )
        db.session.add(item)
        db.session.commit()

        link = CaseEvidence(
            case_id=self.case.id,
            evidence_id=item.id,
            linked_by_id=self.user.id,
            link_purpose="intake",
        )
        db.session.add(link)
        db.session.commit()
        return item

    def _event(self, name="Incident Alpha"):
        """Create an Event."""
        import uuid
        event = Event(
            id=str(uuid.uuid4()),
            case_id=self.case.id,
            event_name=name,
            event_start=datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
            event_end=datetime(2025, 1, 15, 15, 0, tzinfo=timezone.utc),
            created_by_user_id=self.user.id,
        )
        db.session.add(event)
        db.session.commit()
        return event

    def _link(self, event, evidence, offset_ms=0, camera_label="Camera",
              is_anchor=False):
        """Link evidence to an event."""
        link = EventEvidence(
            event_id=event.id,
            evidence_id=evidence.id,
            sync_offset_ms=offset_ms,
            camera_label=camera_label,
            is_sync_anchor=is_anchor,
            linked_by_user_id=self.user.id,
        )
        db.session.add(link)
        db.session.commit()
        return link


# ====================================================================
# 1. Hash Determinism  (3 tests)
# ====================================================================


class TestTimelineHashDeterminism(TimelineTestBase):
    """Timeline hash must be deterministic and tamper-detectable."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_same_inputs_same_hash(self, mock_audit):
        """Building the same event twice yields identical hashes."""
        ev = self._event()
        cam_a = self._evidence("bodycam_a.mp4", "a" * 64, duration_seconds=120)
        cam_b = self._evidence("bodycam_b.mp4", "b" * 64, duration_seconds=90)
        self._link(ev, cam_a, offset_ms=0, camera_label="BWC-A", is_anchor=True)
        self._link(ev, cam_b, offset_ms=1500, camera_label="BWC-B")

        r1 = self.builder.build(ev.id, user_id=self.user.id)
        r2 = self.builder.build(ev.id, user_id=self.user.id)

        self.assertTrue(r1.success)
        self.assertTrue(r2.success)
        self.assertEqual(r1.hash, r2.hash)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_hash_changes_with_offset(self, mock_audit):
        """Changing an offset produces a different hash (tamper-detectable)."""
        ev = self._event()
        cam_a = self._evidence("cam_a.mp4", "a" * 64, duration_seconds=60)
        self._link(ev, cam_a, offset_ms=0, camera_label="Cam-A")

        r1 = self.builder.build(ev.id)

        # Change offset
        link = EventEvidence.query.filter_by(
            event_id=ev.id, evidence_id=cam_a.id,
        ).one()
        link.sync_offset_ms = 500
        db.session.commit()

        r2 = self.builder.build(ev.id)

        self.assertNotEqual(r1.hash, r2.hash)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_hash_excludes_generated_at(self, mock_audit):
        """Hash must not depend on the generated_at timestamp."""
        ev = self._event()
        cam = self._evidence("dash.mp4", "d" * 64, duration_seconds=300)
        self._link(ev, cam, offset_ms=0, camera_label="Dash")

        r1 = self.builder.build(ev.id)
        r2 = self.builder.build(ev.id)

        # generated_at differs, hash must not
        self.assertNotEqual(
            r1.timeline["generated_at"],
            r2.timeline["generated_at"],
        )
        self.assertEqual(r1.hash, r2.hash)


# ====================================================================
# 2. Hash Computation  (2 tests)
# ====================================================================


class TestTimelineHashComputation(TimelineTestBase):
    """Verify the hash computation itself is canonical."""

    def test_compute_hash_canonical(self):
        """Hash is SHA-256 of canonical JSON of event_id + tracks."""
        timeline = {
            "event_id": "abc-123",
            "tracks": [{"evidence_id": 1, "offset_ms": 0}],
            "generated_at": "2025-01-01T00:00:00+00:00",
        }
        expected_input = {"event_id": "abc-123", "tracks": [{"evidence_id": 1, "offset_ms": 0}]}
        expected_json = json.dumps(expected_input, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(expected_json.encode("utf-8")).hexdigest()

        actual = EventTimelineBuilder._compute_hash(timeline)
        self.assertEqual(actual, expected_hash)

    def test_compute_hash_is_64_hex_chars(self):
        """Hash output is always 64 lowercase hex characters."""
        timeline = {"event_id": "x", "tracks": []}
        h = EventTimelineBuilder._compute_hash(timeline)
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))


# ====================================================================
# 3. Track Ordering  (2 tests)
# ====================================================================


class TestTrackOrdering(TimelineTestBase):
    """Tracks must be sorted: anchor-first, then ascending offset."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_anchor_first(self, mock_audit):
        """The sync anchor must appear as the first track."""
        ev = self._event()
        cam_a = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        cam_b = self._evidence("b.mp4", "b" * 64, duration_seconds=60)
        # B is anchor even though A has lower offset
        self._link(ev, cam_a, offset_ms=100, camera_label="A")
        self._link(ev, cam_b, offset_ms=200, camera_label="B", is_anchor=True)

        result = self.builder.build(ev.id)
        self.assertTrue(result.success)
        self.assertTrue(result.timeline["tracks"][0]["is_sync_anchor"])
        self.assertEqual(result.timeline["tracks"][0]["camera_label"], "B")

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_ascending_offset_within_non_anchors(self, mock_audit):
        """Non-anchor tracks are sorted by ascending offset_ms."""
        ev = self._event()
        cam_a = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        cam_b = self._evidence("b.mp4", "b" * 64, duration_seconds=60)
        cam_c = self._evidence("c.mp4", "c" * 64, duration_seconds=60)
        self._link(ev, cam_a, offset_ms=3000, camera_label="A")
        self._link(ev, cam_b, offset_ms=1000, camera_label="B")
        self._link(ev, cam_c, offset_ms=2000, camera_label="C")

        result = self.builder.build(ev.id)
        non_anchors = [t for t in result.timeline["tracks"] if not t["is_sync_anchor"]]
        offsets = [t["offset_ms"] for t in non_anchors]
        self.assertEqual(offsets, sorted(offsets))


# ====================================================================
# 4. Timeline Bounds  (2 tests)
# ====================================================================


class TestTimelineBounds(TimelineTestBase):
    """Total duration and start/end offsets are computed correctly."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_total_duration(self, mock_audit):
        """total_duration_ms = max(offset + duration) - min(offset)."""
        ev = self._event()
        # Track A: offset 0, duration 60_000 ms
        # Track B: offset 5000, duration 30_000 ms
        # Expected: max(60000, 35000) - 0 = 60000
        cam_a = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        cam_b = self._evidence("b.mp4", "b" * 64, duration_seconds=30)
        self._link(ev, cam_a, offset_ms=0, camera_label="A")
        self._link(ev, cam_b, offset_ms=5000, camera_label="B")

        result = self.builder.build(ev.id)
        self.assertEqual(result.timeline["total_duration_ms"], 60000)
        self.assertEqual(result.timeline["timeline_start_offset_ms"], 0)
        self.assertEqual(result.timeline["timeline_end_offset_ms"], 60000)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_negative_offset(self, mock_audit):
        """Negative offsets shift the timeline start earlier."""
        ev = self._event()
        cam_a = self._evidence("a.mp4", "a" * 64, duration_seconds=30)
        cam_b = self._evidence("b.mp4", "b" * 64, duration_seconds=30)
        self._link(ev, cam_a, offset_ms=-2000, camera_label="A")
        self._link(ev, cam_b, offset_ms=0, camera_label="B")

        result = self.builder.build(ev.id)
        self.assertEqual(result.timeline["timeline_start_offset_ms"], -2000)
        # max end = max(-2000+30000, 0+30000) = 30000
        self.assertEqual(result.timeline["timeline_end_offset_ms"], 30000)
        self.assertEqual(result.timeline["total_duration_ms"], 32000)


# ====================================================================
# 5. Duration Extraction  (2 tests)
# ====================================================================


class TestDurationExtraction(TimelineTestBase):
    """Duration comes from EvidenceItem.duration_seconds first."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_duration_from_column(self, mock_audit):
        """Uses duration_seconds when populated."""
        ev = self._event()
        cam = self._evidence("vid.mp4", "v" * 64, duration_seconds=45)
        self._link(ev, cam, camera_label="Cam")

        result = self.builder.build(ev.id)
        track = result.timeline["tracks"][0]
        self.assertEqual(track["duration_ms"], 45000)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_duration_none_when_missing(self, mock_audit):
        """Returns None duration when no source is available."""
        ev = self._event()
        cam = self._evidence("doc.pdf", "p" * 64, file_type="pdf", mime_type="application/pdf")
        self._link(ev, cam, camera_label="Doc")

        result = self.builder.build(ev.id)
        track = result.timeline["tracks"][0]
        self.assertIsNone(track["duration_ms"])


# ====================================================================
# 6. Error Handling  (3 tests)
# ====================================================================


class TestTimelineErrors(TimelineTestBase):
    """Builder returns clear failures for invalid inputs."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_missing_event(self, mock_audit):
        """Non-existent event_id returns failure."""
        result = self.builder.build("nonexistent-uuid-9999")
        self.assertFalse(result.success)
        self.assertIn("not found", result.error.lower())

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_event_with_no_evidence(self, mock_audit):
        """Event with zero evidence links returns failure."""
        ev = self._event()
        result = self.builder.build(ev.id)
        self.assertFalse(result.success)
        self.assertIn("no evidence", result.error.lower())

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_result_type(self, mock_audit):
        """Builder always returns a TimelineBuildResult."""
        result = self.builder.build("does-not-exist")
        self.assertIsInstance(result, TimelineBuildResult)


# ====================================================================
# 7. Audit Recording  (2 tests)
# ====================================================================


class TestTimelineAudit(TimelineTestBase):
    """Every successful build must produce an audit entry."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_audit_called_on_success(self, mock_audit):
        """_audit is invoked when the build succeeds."""
        ev = self._event()
        cam = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        self._link(ev, cam, camera_label="A")

        result = self.builder.build(ev.id, user_id=self.user.id)
        self.assertTrue(result.success)
        mock_audit.assert_called_once()

        # Verify audit payload contains required fields
        call_kwargs = mock_audit.call_args[1]
        self.assertEqual(call_kwargs["event_id"], ev.id)
        self.assertIn(cam.id, call_kwargs["evidence_ids"])
        self.assertEqual(call_kwargs["timeline_hash"], result.hash)
        self.assertEqual(call_kwargs["user_id"], self.user.id)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_audit_not_called_on_failure(self, mock_audit):
        """_audit is not invoked when the build fails."""
        result = self.builder.build("missing-event-id")
        self.assertFalse(result.success)
        mock_audit.assert_not_called()


# ====================================================================
# 8. Metadata-Only Guarantee  (2 tests)
# ====================================================================


class TestMetadataOnlyGuarantee(TimelineTestBase):
    """Timeline build must never alter original evidence."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_evidence_hash_unchanged(self, mock_audit):
        """Evidence SHA-256 is unchanged after timeline build."""
        ev = self._event()
        cam = self._evidence("bodycam.mp4", "f" * 64, duration_seconds=120)
        original_hash = cam.hash_sha256
        self._link(ev, cam, camera_label="BWC")

        result = self.builder.build(ev.id)
        self.assertTrue(result.success)

        # Reload from DB
        refreshed = db.session.get(EvidenceItem, cam.id)
        self.assertEqual(refreshed.hash_sha256, original_hash)

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_metadata_notice_present(self, mock_audit):
        """Timeline always includes the metadata-only notice."""
        ev = self._event()
        cam = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        self._link(ev, cam, camera_label="A")

        result = self.builder.build(ev.id)
        self.assertIn("metadata_only_notice", result.timeline)
        self.assertIn("metadata-only", result.timeline["metadata_only_notice"].lower())
        self.assertIn("unaltered", result.timeline["metadata_only_notice"].lower())


# ====================================================================
# 9. Timeline Output Structure  (2 tests)
# ====================================================================


class TestTimelineStructure(TimelineTestBase):
    """Timeline output contains all required fields."""

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_top_level_fields(self, mock_audit):
        """Timeline dict has all required top-level keys."""
        ev = self._event()
        cam = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        self._link(ev, cam, camera_label="A")

        result = self.builder.build(ev.id)
        required_keys = {
            "event_id", "event_name", "case_id",
            "timeline_start_offset_ms", "timeline_end_offset_ms",
            "total_duration_ms", "track_count", "tracks",
            "generated_at", "metadata_only_notice", "timeline_hash",
        }
        self.assertTrue(required_keys.issubset(result.timeline.keys()))

    @patch("services.event_timeline.EventTimelineBuilder._audit")
    def test_track_fields(self, mock_audit):
        """Each track dict has all required fields."""
        ev = self._event()
        cam = self._evidence("a.mp4", "a" * 64, duration_seconds=60)
        self._link(ev, cam, camera_label="A")

        result = self.builder.build(ev.id)
        track = result.timeline["tracks"][0]
        required_keys = {
            "evidence_id", "evidence_store_id", "camera_label",
            "original_filename", "file_type", "mime_type",
            "hash_sha256", "offset_ms", "duration_ms", "is_sync_anchor",
        }
        self.assertTrue(required_keys.issubset(track.keys()))


# ====================================================================
# Run
# ====================================================================

if __name__ == "__main__":
    unittest.main()
