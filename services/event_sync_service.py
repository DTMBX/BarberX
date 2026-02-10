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
"""

from collections import namedtuple
from datetime import datetime, timezone

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
    'SyncGroupResult', ['success', 'data', 'error'], defaults=[None, None, None],
)


class EventSyncService:
    """Service for event management, evidence linking, and sync operations."""

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def create_event(
        self,
        case_id,
        event_name,
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
    ):
        """Create a new event within a case."""
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

        self._audit('EVENT_CREATED', metadata={
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
    ):
        """Link an evidence item to an event (case-scope enforced)."""
        event = db.session.get(Event, event_id)
        if not event:
            return SyncResult(success=False, error='Event not found')

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

        self._audit('EVIDENCE_LINKED_TO_EVENT', metadata={
            'event_id': event_id,
            'evidence_id': evidence_id,
            'sync_offset_ms': sync_offset_ms,
        }, user_id=linked_by_user_id)

        return SyncResult(success=True, data=link)

    def unlink_evidence_from_event(self, event_id, evidence_id):
        """Remove an evidence-to-event link."""
        link = EventEvidence.query.filter_by(
            event_id=event_id,
            evidence_id=evidence_id,
        ).first()
        if not link:
            return SyncResult(success=False, error='Link not found')

        db.session.delete(link)
        db.session.commit()

        self._audit('EVIDENCE_UNLINKED_FROM_EVENT', metadata={
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
        evidence_ids,
        offsets_ms,
        reference_evidence_id,
        sync_label,
        sync_method=SyncMethod.MANUAL.value,
        created_by_user_id=None,
    ):
        """Create a multi-camera sync group within an event."""
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

        self._audit('SYNC_GROUP_CREATED', metadata={
            'group_id': group.id,
            'event_id': event_id,
            'integrity_hash': integrity_hash,
            'evidence_ids': evidence_ids,
        }, user_id=created_by_user_id)

        return SyncGroupResult(success=True, data=group)

    def verify_sync_group(self, group_id):
        """Verify a sync group's integrity hash."""
        group = db.session.get(CameraSyncGroup, group_id)
        if not group:
            return SyncGroupResult(success=False, error='Sync group not found')

        verified = group.verify_integrity()

        self._audit('SYNC_GROUP_VERIFIED', metadata={
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

    @staticmethod
    def _audit(action, evidence_id=None, metadata=None, user_id=None):
        """Best-effort audit recording; failures do not propagate."""
        try:
            from services.audit_stream import AuditStream
            audit = AuditStream()
            audit.record(
                action=action,
                evidence_id=evidence_id,
                metadata=metadata or {},
                user_id=user_id,
            )
        except Exception:
            pass
