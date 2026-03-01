"""Timeline API — derived timeline events for a case."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import TimelineEvent
from app.core.database import get_db
from app.models.audit_event import AuditEvent
from app.models.case import Case

router = APIRouter(tags=["timeline"])


@router.get("/cases/{case_id}/timeline", response_model=list[TimelineEvent])
def case_timeline(case_id: uuid.UUID, db: Session = Depends(get_db)):
    """Build a derived timeline from audit events and artifact timestamps."""
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    audit_rows = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at)
        .all()
    )

    events: list[TimelineEvent] = []
    for row in audit_rows:
        description = _describe_event(row.event_type, row.payload_json)
        evidence_id = None
        eid_str = row.payload_json.get("evidence_id")
        if eid_str:
            try:
                evidence_id = uuid.UUID(eid_str)
            except ValueError:
                pass

        events.append(
            TimelineEvent(
                timestamp=row.created_at,
                event_type=row.event_type,
                description=description,
                evidence_id=evidence_id,
                metadata=row.payload_json,
            )
        )

    return events


def _describe_event(event_type: str, payload: dict) -> str:
    """Generate a human-readable description from an audit event."""
    descriptions = {
        "case.created": "Case created by {created_by}",
        "evidence.init": "Upload initiated for {filename}",
        "evidence.complete": "Evidence finalized — SHA-256: {sha256}",
        "evidence.metadata_extracted": "Metadata extraction complete for evidence {evidence_id}",
        "job.enqueued": "Processing job enqueued ({task_type})",
        "job.failed": "Processing job failed: {reason}",
        "artifact.created": "Artifact created: {artifact_type}",
        "manifest.exported": "Case manifest exported",
        "chat.ask": "Chat question asked",
        "courtlistener.search": "CourtListener search executed",
    }
    template = descriptions.get(event_type, event_type)
    try:
        return template.format(**payload)
    except (KeyError, IndexError):
        return f"{event_type}: {payload}"
