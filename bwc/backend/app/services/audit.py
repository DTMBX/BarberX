"""Audit log — append-only dual-write to DB + bwc/rag_context/audit_log.jsonl."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_event import AuditEvent

logger = logging.getLogger(__name__)

# Resolve the path to bwc/rag_context/audit_log.jsonl
_RAG_AUDIT_PATH = Path(settings.suite_root) / "rag_context" / "audit_log.jsonl"


def append_audit_event(
    db: Session,
    case_id: uuid.UUID | None,
    event_type: str,
    payload: dict,
) -> AuditEvent:
    """
    Dual-write an audit event:
      1. Insert into the audit_events DB table.
      2. Append a JSON line to bwc/rag_context/audit_log.jsonl (never truncate).
    """
    now = datetime.now(timezone.utc)
    event_id = uuid.uuid4()

    # ── DB insert ────────────────────────────────────────────────────
    row = AuditEvent(
        id=event_id,
        case_id=case_id,
        event_type=event_type,
        payload_json=payload,
        created_at=now,
    )
    db.add(row)
    db.flush()  # ensure row is visible within the same transaction

    # ── File append (append-only, never overwrite) ───────────────────
    line = {
        "event_id": str(event_id),
        "case_id": str(case_id) if case_id else None,
        "event_type": event_type,
        "payload": payload,
        "created_at": now.isoformat(),
    }
    try:
        _RAG_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_RAG_AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, separators=(",", ":"), sort_keys=True) + "\n")
    except OSError as exc:
        # Log but do not fail the request — DB is authoritative
        logger.warning("Could not append to %s: %s", _RAG_AUDIT_PATH, exc)

    return row
