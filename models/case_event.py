"""
Case + Event Data Models
========================
Core entity models for event-based evidence grouping within cases.

Design intent (non-negotiable):
  - Evidence can belong to multiple cases  (via CaseEvidence in models/evidence.py)
  - Cases contain events
  - Events group evidence by incident      (via EventEvidence below)
  - Evidence is never duplicated
  - sync_offset_ms is metadata only — no video frames are altered

Entity mapping
--------------
  Case           →  LegalCase     models/legal_case.py   tablename 'legal_case'
  Evidence       →  EvidenceItem  models/evidence.py     tablename 'evidence_item'
  Case↔Evidence  →  CaseEvidence  models/evidence.py     tablename 'case_evidence'
  Event          →  Event         (this file)            tablename 'events'
  Event↔Evidence →  EventEvidence (this file)            tablename 'event_evidence'

Forensic invariants:
  - Evidence originals are never mutated by event or sync operations.
  - Sync integrity hashes are computed from constituent evidence hashes
    and temporal offsets — any change is detectable.
  - All records carry actor attribution and UTC timestamps.
  - Timeline entries are derived views; they reference existing records
    and do not create new evidentiary state.
"""

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from auth.models import db, User


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SyncMethod(Enum):
    """Method used to temporally align camera streams."""
    MANUAL = "manual"
    TIMECODE = "timecode"
    AUDIO_CORRELATION = "audio_correlation"
    GPS_TIME = "gps_time"
    NTP_TIMESTAMP = "ntp_timestamp"
    METADATA_TIMESTAMP = "metadata_timestamp"


class TimelineEntryType(Enum):
    """Classification of timeline entries."""
    EVENT_START = "event_start"
    EVENT_END = "event_end"
    EVIDENCE_INGEST = "evidence_ingest"
    CUSTODY_TRANSFER = "custody_transfer"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANNOTATION = "annotation"


# ============================================================================
# CORE: Event
# ============================================================================


class Event(db.Model):
    """
    An incident-level occurrence within a case.

    Events are factual time-and-place anchors. They record WHEN and WHAT
    happened. They NEVER encode fault, intent, or legal conclusions.
    """
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))

    # FK to LegalCase (the authoritative Case entity)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey('legal_case.id'),
        nullable=False,
        index=True,
    )

    event_name = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(100), nullable=True)       # traffic_stop, arrest, scene, etc.
    event_number = db.Column(db.String(100), nullable=True, index=True)  # agency-assigned #

    event_start = db.Column(db.DateTime, nullable=True)
    event_end = db.Column(db.DateTime, nullable=True)

    description = db.Column(db.Text, nullable=True)

    # Location (factual, not interpretive)
    location_description = db.Column(db.String(500), nullable=True)
    location_address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Sealed flag — once set, event metadata is immutable
    is_sealed = db.Column(db.Boolean, default=False, nullable=False)

    # Audit
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True,
    )

    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])
    evidence_links = db.relationship(
        'EventEvidence',
        backref='event',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    sync_groups = db.relationship(
        'CameraSyncGroup',
        backref='event',
        cascade='all, delete-orphan',
    )
    timeline_entries = db.relationship(
        'CaseTimelineEntry',
        backref='event',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<Event {self.id[:8]}: {self.event_name}>'

    # -- Allow service to construct with alias names --
    def __init__(self, **kwargs):
        # Map alias names to real column names
        aliases = {
            'event_label': 'event_name',
            'start_time': 'event_start',
            'end_time': 'event_end',
            'created_by_id': 'created_by_user_id',
        }
        for alias, real in aliases.items():
            if alias in kwargs and real not in kwargs:
                kwargs[real] = kwargs.pop(alias)
        super().__init__(**kwargs)

    # -- Property aliases for service compatibility --
    @property
    def event_label(self):
        return self.event_name

    @event_label.setter
    def event_label(self, value):
        self.event_name = value

    @property
    def start_time(self):
        return self.event_start

    @start_time.setter
    def start_time(self, value):
        self.event_start = value

    @property
    def end_time(self):
        return self.event_end

    @end_time.setter
    def end_time(self, value):
        self.event_end = value

    @property
    def created_by_id(self):
        return self.created_by_user_id

    @created_by_id.setter
    def created_by_id(self, value):
        self.created_by_user_id = value


# ============================================================================
# CORE: EventEvidence  (many-to-many, composite PK)
# ============================================================================


class EventEvidence(db.Model):
    """
    Links an evidence item to an event.

    sync_offset_ms is metadata only. No video frames are altered.
    No original evidence file is modified by any operation on this record.
    """
    __tablename__ = 'event_evidence'

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.String(36),
        db.ForeignKey('events.id'),
        nullable=False,
        index=True,
    )
    evidence_id = db.Column(
        db.Integer,
        db.ForeignKey('evidence_item.id'),
        nullable=False,
        index=True,
    )

    # Camera synchronization (metadata only)
    sync_offset_ms = db.Column(db.Integer, nullable=True)
    camera_label = db.Column(db.String(200), nullable=True)
    camera_position = db.Column(db.String(200), nullable=True)
    is_sync_anchor = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)

    # Optional sync group membership
    sync_group_id = db.Column(
        db.Integer,
        db.ForeignKey('camera_sync_group.id'),
        nullable=True,
    )

    # Audit
    linked_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    linked_by_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True,
    )

    # Relationships
    evidence = db.relationship('EvidenceItem', foreign_keys=[evidence_id])
    linked_by = db.relationship('User', foreign_keys=[linked_by_user_id])

    __table_args__ = (
        db.UniqueConstraint('event_id', 'evidence_id', name='uq_event_evidence'),
    )

    def __init__(self, **kwargs):
        aliases = {
            'temporal_offset_ms': 'sync_offset_ms',
            'created_by_id': 'linked_by_user_id',
        }
        for alias, real in aliases.items():
            if alias in kwargs and real not in kwargs:
                kwargs[real] = kwargs.pop(alias)
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f'<EventEvidence event={self.event_id[:8]} '
            f'evidence={self.evidence_id}>'
        )

    # -- Property aliases for service compatibility --
    @property
    def temporal_offset_ms(self):
        return self.sync_offset_ms

    @temporal_offset_ms.setter
    def temporal_offset_ms(self, value):
        self.sync_offset_ms = value

    @property
    def created_by_id(self):
        return self.linked_by_user_id

    @created_by_id.setter
    def created_by_id(self, value):
        self.linked_by_user_id = value


# ============================================================================
# EXTENSION: Multi-Camera Sync Group
# ============================================================================


class CameraSyncGroup(db.Model):
    """
    Groups multiple evidence streams within an event for synchronized
    temporal playback.

    This is a METADATA-ONLY construct. No original evidence is modified.
    The integrity_hash allows verification that synchronization parameters
    have not been altered since creation.

    Integrity hash = SHA-256 of canonical JSON:
        [{"evidence_sha256": "...", "offset_ms": N}, ...]
      sorted by evidence_sha256.
    """
    __tablename__ = 'camera_sync_group'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.String(36),
        db.ForeignKey('events.id'),
        nullable=False,
        index=True,
    )

    sync_label = db.Column(db.String(300), nullable=False)

    reference_evidence_id = db.Column(
        db.Integer,
        db.ForeignKey('evidence_item.id'),
        nullable=False,
    )

    sync_method = db.Column(
        db.String(50),
        nullable=False,
        default=SyncMethod.MANUAL.value,
    )

    # Verification
    sync_verified = db.Column(db.Boolean, default=False)
    sync_verified_by_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True,
    )
    sync_verified_at = db.Column(db.DateTime, nullable=True)

    # Integrity
    integrity_hash = db.Column(db.String(64), nullable=False, index=True)

    # Audit
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True,
    )

    # Relationships
    reference_evidence = db.relationship(
        'EvidenceItem', foreign_keys=[reference_evidence_id],
    )
    sync_verified_by = db.relationship('User', foreign_keys=[sync_verified_by_id])
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])
    members = db.relationship(
        'EventEvidence',
        backref='sync_group',
        foreign_keys='EventEvidence.sync_group_id',
    )

    def __repr__(self):
        return f'<CameraSyncGroup {self.id}: {self.sync_label}>'

    def __init__(self, **kwargs):
        aliases = {
            'created_by_id': 'created_by_user_id',
        }
        for alias, real in aliases.items():
            if alias in kwargs and real not in kwargs:
                kwargs[real] = kwargs.pop(alias)
        super().__init__(**kwargs)

    # -- Property aliases for service compatibility --
    @property
    def created_by_id(self):
        return self.created_by_user_id

    @created_by_id.setter
    def created_by_id(self, value):
        self.created_by_user_id = value

    @staticmethod
    def compute_integrity_hash(member_data: list[dict]) -> str:
        """
        Compute canonical integrity hash for a sync group.

        Args:
            member_data: List of dicts with keys:
                evidence_sha256 (str), offset_ms (int).

        Returns:
            Hex SHA-256 of the canonical JSON.
        """
        canonical = sorted(
            [
                {
                    "evidence_sha256": m["evidence_sha256"],
                    "offset_ms": int(m["offset_ms"]),
                }
                for m in member_data
            ],
            key=lambda x: x["evidence_sha256"],
        )
        payload = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        """Recompute integrity hash and compare against stored value."""
        member_data = []
        for link in self.members:
            evidence = link.evidence
            if evidence and evidence.hash_sha256:
                member_data.append({
                    "evidence_sha256": evidence.hash_sha256,
                    "offset_ms": link.sync_offset_ms or 0,
                })
        recomputed = self.compute_integrity_hash(member_data)
        return recomputed == self.integrity_hash


# ============================================================================
# EXTENSION: Case Timeline
# ============================================================================


class CaseTimelineEntry(db.Model):
    """
    A chronological entry in a case's timeline.

    Timeline entries are DERIVED VIEWS — they reference existing events,
    evidence, and audit actions. They do not create new evidentiary state.
    """
    __tablename__ = 'case_timeline_entry'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey('legal_case.id'),
        nullable=False,
        index=True,
    )

    event_id = db.Column(
        db.String(36),
        db.ForeignKey('events.id'),
        nullable=True,
        index=True,
    )
    evidence_id = db.Column(
        db.Integer,
        db.ForeignKey('evidence_item.id'),
        nullable=True,
    )

    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    entry_type = db.Column(
        db.String(50),
        nullable=False,
        default=TimelineEntryType.ANNOTATION.value,
    )
    label = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)

    source = db.Column(db.String(200))       # "audit_stream", "manual", "metadata"
    source_reference = db.Column(db.String(300))

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True,
    )

    # Relationships
    evidence = db.relationship('EvidenceItem', foreign_keys=[evidence_id])
    created_by = db.relationship('User', foreign_keys=[created_by_user_id])

    def __repr__(self):
        return f'<CaseTimelineEntry {self.timestamp}: {self.label}>'


# ============================================================================
# EXTENSION: Case Export Record
# ============================================================================


class CaseExportRecord(db.Model):
    """
    Records each export of case materials.  package_sha256 allows
    verification that a previously exported package has not been altered.
    """
    __tablename__ = 'case_export_record'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey('legal_case.id'),
        nullable=False,
        index=True,
    )

    export_type = db.Column(db.String(50), nullable=False, default='full')
    included_event_ids = db.Column(db.Text)       # JSON array
    included_evidence_ids = db.Column(db.Text)     # JSON array

    file_count = db.Column(db.Integer, nullable=False, default=0)
    total_bytes = db.Column(db.Integer, nullable=False, default=0)
    package_sha256 = db.Column(db.String(64), index=True)
    export_path = db.Column(db.String(500))

    manifest_json = db.Column(db.Text, nullable=False)

    exported_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    exported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    exported_by = db.relationship('User', foreign_keys=[exported_by_id])

    def __repr__(self):
        return f'<CaseExportRecord case={self.case_id} type={self.export_type}>'


# ============================================================================
# Compatibility aliases — consumed by services/event_sync_service.py
# ============================================================================

CaseEvent = Event              # Service calls it CaseEvent
EventEvidenceLink = EventEvidence  # Service calls it EventEvidenceLink
