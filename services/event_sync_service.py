"""
Event Synchronization Service
==============================
Manages event creation, evidence linking, multi-camera synchronization,
and timeline generation.

All operations are non-destructive:
  - No original evidence file is modified.
  - sync_offset_ms is metadata only.
  - Integrity hashes allow verification of sync parameters.
  - All actions are auditable.
  - Sealed events reject mutation operations.
"""

from collections import namedtuple
from datetime import datetime, timezone
from enum import Enum

from auth.models import db
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


SyncResult = namedtuple(
    'SyncResult', ['success', 'data', 'error'], defaults=[None, None, None],
)
SyncGroupResult = namedtuple(
    'SyncGroupResult',
    ['success', 'data', 'error', 'sync_group_id', 'integrity_hash'],
    defaults=[None, None, None, None, None],
)


# ---------------------------------------------------------------------------
# Audit action constants
# ---------------------------------------------------------------------------


class SyncAuditAction(str, Enum):
    """Constants for sync-related audit actions."""
    EVENT_CREATED = "event.created"
    EVENT_EVIDENCE_LINKED = "event.evidence_linked"
    EVENT_EVIDENCE_UNLINKED = "event.evidence_unlinked"
    SYNC_GROUP_CREATED = "sync_group.created"
    SYNC_MEMBER_ADDED = "sync_group.member_added"
    SYNC_GROUP_VERIFIED = "sync_group.verified"
    SYNC_OFFSET_UPDATED = "sync_group.offset_updated"
    EVENT_MUTATION_DENIED = "event.mutation_denied"


class EventSyncService:
    """Service for event management, evidence linking, and sync operations.

    Args:
        audit_stream: Optional audit recorder. If provided, all mutations
            call audit_stream.record(action=..., metadata=..., user_id=...).
            When None, the service falls back to the global AuditStream.
    """

    def __init__(self, audit_stream=None):
        self._external_audit = audit_stream

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def create_event(
        self,
        case_id,
        event_name=None,
        event_start=None,
        event_end=None,
        event_type=None,
        event_number=None,
        description=None,
        location_description=None,
        location_address=None,
        latitude=None,
        longitude=None,
        created_by_user_id=None,
        # Alias parameters for service compatibility
        event_label=None,
        start_time=None,
        end_time=None,
    ):
        """Create a new event within a case."""
        # Accept aliases
        if event_label is not None and event_name is None:
            event_name = event_label
        if start_time is not None and event_start is None:
            event_start = start_time
        if end_time is not None and event_end is None:
            event_end = end_time

        case = db.session.get(LegalCase, case_id)
        if not case:
            return SyncResult(success=False, error='Case not found')

        if not event_name or not event_name.strip():
            return SyncResult(success=False, error='Event name is required')

        if event_start and event_end and event_end < event_start:
            return SyncResult(
                success=False, error='End time cannot precede start time',
            )

        event = Event(
            case_id=case_id,
            event_name=event_name.strip(),
            event_type=event_type,
            event_number=event_number,
            event_start=event_start,
            event_end=event_end,
            description=description,
            location_description=location_description,
            location_address=location_address,
            latitude=latitude,
            longitude=longitude,
            created_by_user_id=created_by_user_id,
        )
        db.session.add(event)
        db.session.commit()

        self._audit(SyncAuditAction.EVENT_CREATED, metadata={
            'event_id': event.id,
            'case_id': case_id,
            'event_name': event.event_name,
        }, user_id=created_by_user_id)

        return SyncResult(success=True, data=event)

    # ------------------------------------------------------------------
    # Evidence linking
    # ------------------------------------------------------------------

    def link_evidence_to_event(
        self,
        event_id,
        evidence_id,
        sync_offset_ms=None,
        camera_label=None,
        linked_by_user_id=None,
        # Alias accepted for backward compatibility
        temporal_offset_ms=None,
    ):
        """Link an evidence item to an event (case-scope enforced)."""
        # Accept alias
        if temporal_offset_ms is not None and sync_offset_ms is None:
            sync_offset_ms = temporal_offset_ms

        event = db.session.get(Event, event_id)
        if not event:
            return SyncResult(success=False, error='Event not found')

        # Sealed-event enforcement
        if event.is_sealed:
            self._audit(SyncAuditAction.EVENT_MUTATION_DENIED, metadata={
                'event_id': event_id,
                'attempted_action': 'link_evidence',
                'evidence_id': evidence_id,
                'reason': 'Event is sealed',
            })
            raise ValueError(f"Event {event_id} is sealed — evidence linking denied")

        evidence = db.session.get(EvidenceItem, evidence_id)
        if not evidence:
            return SyncResult(success=False, error='Evidence not found')

        # Case-scope enforcement
        active_link = CaseEvidence.query.filter_by(
            case_id=event.case_id,
            evidence_id=evidence_id,
        ).filter(CaseEvidence.unlinked_at.is_(None)).first()

        origin_match = (evidence.origin_case_id == event.case_id)

        if not active_link and not origin_match:
            return SyncResult(
                success=False,
                error='Evidence does not belong to this case',
            )

        # Duplicate check
        existing = EventEvidence.query.filter_by(
            event_id=event_id,
            evidence_id=evidence_id,
        ).first()
        if existing:
            return SyncResult(
                success=False,
                error='Evidence already linked to this event',
            )

        link = EventEvidence(
            event_id=event_id,
            evidence_id=evidence_id,
            sync_offset_ms=sync_offset_ms,
            camera_label=camera_label,
            linked_by_user_id=linked_by_user_id,
        )
        db.session.add(link)
        db.session.commit()

        self._audit(SyncAuditAction.EVENT_EVIDENCE_LINKED, metadata={
            'event_id': event_id,
            'evidence_id': evidence_id,
            'sync_offset_ms': sync_offset_ms,
        }, user_id=linked_by_user_id)

        return SyncResult(success=True, data=link)

    def unlink_evidence_from_event(self, event_id, evidence_id):
        """Remove an evidence-to-event link."""
        event = db.session.get(Event, event_id)
        if event and event.is_sealed:
            self._audit(SyncAuditAction.EVENT_MUTATION_DENIED, metadata={
                'event_id': event_id,
                'attempted_action': 'unlink_evidence',
                'evidence_id': evidence_id,
                'reason': 'Event is sealed',
            })
            raise ValueError(f"Event {event_id} is sealed — evidence unlinking denied")

        link = EventEvidence.query.filter_by(
            event_id=event_id,
            evidence_id=evidence_id,
        ).first()
        if not link:
            return SyncResult(success=False, error='Link not found')

        db.session.delete(link)
        db.session.commit()

        self._audit(SyncAuditAction.EVENT_EVIDENCE_UNLINKED, metadata={
            'event_id': event_id,
            'evidence_id': evidence_id,
        })

        return SyncResult(success=True, data={'unlinked': True})

    # ------------------------------------------------------------------
    # Sync groups
    # ------------------------------------------------------------------

    def create_sync_group(
        self,
        event_id,
        evidence_ids=None,
        offsets_ms=None,
        reference_evidence_id=None,
        sync_label=None,
        sync_method=SyncMethod.MANUAL.value,
        created_by_user_id=None,
        # Alias parameters accepted by test_case_management.py
        member_evidence_ids=None,
    ):
        """Create a multi-camera sync group within an event."""
        # Accept alias
        if member_evidence_ids is not None and evidence_ids is None:
            evidence_ids = member_evidence_ids
        if offsets_ms is None:
            offsets_ms = {}

        if len(evidence_ids) < 2:
            return SyncGroupResult(
                success=False,
                error='Sync group requires at least 2 evidence items',
            )

        if reference_evidence_id not in evidence_ids:
            return SyncGroupResult(
                success=False,
                error='Reference evidence must be in evidence list',
            )

        event = db.session.get(Event, event_id)
        if not event:
            return SyncGroupResult(success=False, error='Event not found')

        # Sealed-event enforcement
        if event.is_sealed:
            self._audit(SyncAuditAction.EVENT_MUTATION_DENIED, metadata={
                'event_id': event_id,
                'attempted_action': 'create_sync_group',
                'reason': 'Event is sealed',
            })
            return SyncGroupResult(
                success=False,
                error=f'Event {event_id} is sealed — sync group creation denied',
            )

        # Gather member data and compute integrity hash
        member_data = []
        for eid in evidence_ids:
            evidence = db.session.get(EvidenceItem, eid)
            if not evidence or not evidence.hash_sha256:
                return SyncGroupResult(
                    success=False,
                    error=f'Evidence {eid} not found or missing hash',
                )
            member_data.append({
                'evidence_sha256': evidence.hash_sha256,
                'offset_ms': offsets_ms.get(eid, 0),
            })

        integrity_hash = CameraSyncGroup.compute_integrity_hash(member_data)

        group = CameraSyncGroup(
            event_id=event_id,
            sync_label=sync_label,
            reference_evidence_id=reference_evidence_id,
            sync_method=sync_method,
            integrity_hash=integrity_hash,
            created_by_user_id=created_by_user_id,
        )
        db.session.add(group)
        db.session.flush()  # obtain group.id

        # Create or update EventEvidence records
        for eid in evidence_ids:
            link = EventEvidence.query.filter_by(
                event_id=event_id,
                evidence_id=eid,
            ).first()

            if link:
                link.sync_offset_ms = offsets_ms.get(eid, 0)
                link.is_sync_anchor = (eid == reference_evidence_id)
                link.sync_group_id = group.id
            else:
                link = EventEvidence(
                    event_id=event_id,
                    evidence_id=eid,
                    sync_offset_ms=offsets_ms.get(eid, 0),
                    is_sync_anchor=(eid == reference_evidence_id),
                    sync_group_id=group.id,
                    linked_by_user_id=created_by_user_id,
                )
                db.session.add(link)

        db.session.commit()

        self._audit(SyncAuditAction.SYNC_GROUP_CREATED, metadata={
            'group_id': group.id,
            'event_id': event_id,
            'integrity_hash': integrity_hash,
            'evidence_ids': evidence_ids,
        }, user_id=created_by_user_id)

        # Emit per-member audit entries
        for eid in evidence_ids:
            self._audit(SyncAuditAction.SYNC_MEMBER_ADDED, metadata={
                'group_id': group.id,
                'evidence_id': eid,
            }, user_id=created_by_user_id)

        return SyncGroupResult(
            success=True,
            data=group,
            sync_group_id=group.id,
            integrity_hash=integrity_hash,
        )

    def verify_sync_group(self, group_id):
        """Verify a sync group's integrity hash."""
        group = db.session.get(CameraSyncGroup, group_id)
        if not group:
            return SyncGroupResult(success=False, error='Sync group not found')

        verified = group.verify_integrity()

        self._audit(SyncAuditAction.SYNC_GROUP_VERIFIED, metadata={
            'group_id': group_id,
            'verified': verified,
            'integrity_hash': group.integrity_hash,
        })

        return SyncGroupResult(success=True, data={
            'group_id': group_id,
            'verified': verified,
            'integrity_hash': group.integrity_hash,
        })

    # ------------------------------------------------------------------
    # Sync offset updates
    # ------------------------------------------------------------------

    def update_sync_offset(self, group_id, evidence_id, new_offset_ms):
        """
        Update the sync offset for one evidence item within a sync group.

        Recomputes the group integrity hash after the update.
        Rejects mutations on sealed events.
        """
        group = db.session.get(CameraSyncGroup, group_id)
        if not group:
            return SyncGroupResult(success=False, error='Sync group not found')

        event = db.session.get(Event, group.event_id)
        if event and event.is_sealed:
            self._audit(SyncAuditAction.EVENT_MUTATION_DENIED, metadata={
                'event_id': event.id,
                'attempted_action': 'update_sync_offset',
                'group_id': group_id,
                'evidence_id': evidence_id,
                'reason': 'Event is sealed',
            })
            return SyncGroupResult(
                success=False,
                error=f'Event {event.id} is sealed — offset update denied',
            )

        link = EventEvidence.query.filter_by(
            sync_group_id=group_id,
            evidence_id=evidence_id,
        ).first()
        if not link:
            return SyncGroupResult(
                success=False,
                error=f'Evidence {evidence_id} not in sync group {group_id}',
            )

        old_offset = link.sync_offset_ms
        link.sync_offset_ms = new_offset_ms

        # Recompute integrity hash
        member_data = []
        for member in group.members:
            ev = member.evidence
            if ev and ev.hash_sha256:
                member_data.append({
                    'evidence_sha256': ev.hash_sha256,
                    'offset_ms': member.sync_offset_ms or 0,
                })
        new_hash = CameraSyncGroup.compute_integrity_hash(member_data)
        old_hash = group.integrity_hash
        group.integrity_hash = new_hash

        db.session.commit()

        self._audit(SyncAuditAction.SYNC_OFFSET_UPDATED, metadata={
            'group_id': group_id,
            'evidence_id': evidence_id,
            'old_offset_ms': old_offset,
            'new_offset_ms': new_offset_ms,
            'old_integrity_hash': old_hash,
            'new_integrity_hash': new_hash,
        })

        return SyncGroupResult(
            success=True,
            data=group,
            sync_group_id=group_id,
            integrity_hash=new_hash,
        )

    # ------------------------------------------------------------------
    # Temporal overlap detection
    # ------------------------------------------------------------------

    def detect_temporal_overlaps(self, event_id):
        """
        Detect temporal overlaps between evidence streams in an event.

        Uses sync_offset_ms and duration_seconds to compute time windows.
        An overlap exists when two streams have a positive time intersection.

        Returns a list of overlap dicts:
            [{"evidence_a": id, "evidence_b": id,
              "window_start_ms": N, "window_end_ms": N, "overlap_ms": N}, ...]
        """
        links = EventEvidence.query.filter_by(event_id=event_id).all()

        # Build time windows: (evidence_id, start_ms, end_ms)
        windows = []
        for link in links:
            offset = link.sync_offset_ms or 0
            ev = link.evidence
            duration_ms = (ev.duration_seconds or 0) * 1000 if ev else 0
            if duration_ms > 0:
                windows.append({
                    'evidence_id': link.evidence_id,
                    'start_ms': offset,
                    'end_ms': offset + duration_ms,
                })

        # Pairwise overlap detection
        overlaps = []
        for i in range(len(windows)):
            for j in range(i + 1, len(windows)):
                a, b = windows[i], windows[j]
                overlap_start = max(a['start_ms'], b['start_ms'])
                overlap_end = min(a['end_ms'], b['end_ms'])
                if overlap_start < overlap_end:
                    overlaps.append({
                        'evidence_a': a['evidence_id'],
                        'evidence_b': b['evidence_id'],
                        'window_start_ms': overlap_start,
                        'window_end_ms': overlap_end,
                        'overlap_ms': overlap_end - overlap_start,
                    })

        return overlaps

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    def generate_case_timeline(self, case_id):
        """
        Derive a chronological timeline from events, evidence, and
        custody records.

        Timeline entries are derived views — they do not create new
        evidentiary state.
        """
        entries = []

        # Event start / end
        events = Event.query.filter_by(case_id=case_id).all()
        for event in events:
            if event.event_start:
                entries.append(CaseTimelineEntry(
                    case_id=case_id,
                    event_id=event.id,
                    timestamp=event.event_start,
                    entry_type=TimelineEntryType.EVENT_START.value,
                    label=f'Event: {event.event_name}',
                    description=event.description,
                    source='event_metadata',
                ))
            if event.event_end:
                entries.append(CaseTimelineEntry(
                    case_id=case_id,
                    event_id=event.id,
                    timestamp=event.event_end,
                    entry_type=TimelineEntryType.EVENT_END.value,
                    label=f'Event ended: {event.event_name}',
                    source='event_metadata',
                ))

        # Evidence ingest timestamps
        links = CaseEvidence.query.filter_by(case_id=case_id).filter(
            CaseEvidence.unlinked_at.is_(None),
        ).all()
        for link in links:
            ev = link.evidence
            if ev and link.linked_at:
                entries.append(CaseTimelineEntry(
                    case_id=case_id,
                    evidence_id=ev.id,
                    timestamp=link.linked_at,
                    entry_type=TimelineEntryType.EVIDENCE_INGEST.value,
                    label=f'Evidence: {ev.original_filename}',
                    source='case_evidence',
                ))

        # Chain of custody (if model is available)
        try:
            from models.evidence import ChainOfCustody
            custody = ChainOfCustody.query.join(
                CaseEvidence,
                CaseEvidence.evidence_id == ChainOfCustody.evidence_id,
            ).filter(
                CaseEvidence.case_id == case_id,
                CaseEvidence.unlinked_at.is_(None),
            ).all()
            for record in custody:
                ts = getattr(record, 'timestamp', None) or getattr(record, 'created_at', None)
                if ts:
                    entries.append(CaseTimelineEntry(
                        case_id=case_id,
                        evidence_id=record.evidence_id,
                        timestamp=ts,
                        entry_type=TimelineEntryType.CUSTODY_TRANSFER.value,
                        label=f'Custody: {getattr(record, "action", "transfer")}',
                        description=getattr(record, 'notes', None),
                        source='chain_of_custody',
                    ))
        except Exception:
            pass  # ChainOfCustody model may not exist

        # Sort chronologically
        entries.sort(key=lambda e: e.timestamp)

        # Persist (clear prior timeline, then insert)
        CaseTimelineEntry.query.filter_by(case_id=case_id).delete()
        for entry in entries:
            db.session.add(entry)
        db.session.commit()

        return entries

    # ------------------------------------------------------------------
    # Audit helper
    # ------------------------------------------------------------------

    def _audit(self, action, evidence_id=None, metadata=None, user_id=None):
        """
        Best-effort audit recording.

        If an external audit_stream was provided at construction time,
        it is called with keyword arguments:
            audit_stream.record(action=..., metadata=..., user_id=...)
        Otherwise, falls back to the global AuditStream.
        """
        # Normalize enum to string value
        action_str = action.value if isinstance(action, SyncAuditAction) else str(action)

        if self._external_audit is not None:
            try:
                self._external_audit.record(
                    action=action,
                    metadata=metadata or {},
                    user_id=user_id,
                    evidence_id=evidence_id,
                )
            except Exception:
                pass
            return

        try:
            from services.audit_stream import AuditStream
            audit = AuditStream()
            audit.record(
                action=action_str,
                evidence_id=evidence_id,
                metadata=metadata or {},
                user_id=user_id,
            )
        except Exception:
            pass
