"""
Append-Only Audit Stream
=========================
Records every significant event in the evidence lifecycle.

Design principles:
  - Append-only: no edits, no deletes.
  - Every entry is timestamped in UTC.
  - Entries include actor, action, and context.
  - The audit stream is persisted to both:
    (a) the SQLAlchemy database (ChainOfCustody table), and
    (b) the evidence manifest JSON (for export packaging).
  - Dual writes ensure defensibility even if one store is compromised.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from flask import request

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audit actions (constants for consistency)
# ---------------------------------------------------------------------------

class AuditAction:
    """Constants for audit action strings. Use these, not ad-hoc strings."""

    INGEST = "evidence.ingest"
    INGEST_DUPLICATE = "evidence.ingest_duplicate"
    HASH_COMPUTED = "evidence.hash_computed"
    DERIVATIVE_CREATED = "evidence.derivative_created"
    METADATA_EXTRACTED = "evidence.metadata_extracted"
    THUMBNAIL_GENERATED = "evidence.thumbnail_generated"
    PROXY_GENERATED = "evidence.proxy_generated"
    TRANSCRIPT_CREATED = "evidence.transcript_created"
    ACCESSED = "evidence.accessed"
    DOWNLOADED = "evidence.downloaded"
    EXPORTED = "evidence.exported"
    INTEGRITY_VERIFIED = "evidence.integrity_verified"
    INTEGRITY_FAILED = "evidence.integrity_failed"


# ---------------------------------------------------------------------------
# Core audit writer
# ---------------------------------------------------------------------------


class AuditStream:
    """
    Writes audit entries to both the database and the evidence manifest.

    Usage:
        audit = AuditStream(db_session, evidence_store)
        audit.record(
            evidence_id="...",
            db_evidence_id=42,           # integer PK in evidence_item table
            action=AuditAction.INGEST,
            actor_id=1,
            actor_name="admin",
            details={"sha256": "abc123..."},
        )
    """

    def __init__(self, db_session, evidence_store):
        """
        Args:
            db_session: SQLAlchemy session (typically db.session).
            evidence_store: services.evidence_store.EvidenceStore instance.
        """
        self._db = db_session
        self._store = evidence_store

    def record(
        self,
        evidence_id: str,
        action: str,
        actor_id: Optional[int] = None,
        actor_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        db_evidence_id: Optional[int] = None,
        hash_before: Optional[str] = None,
        hash_after: Optional[str] = None,
    ) -> None:
        """
        Record an audit event to both stores.

        Args:
            evidence_id: UUID string (manifest key).
            action: One of AuditAction constants.
            actor_id: Database user ID.
            actor_name: Human-readable name.
            details: Arbitrary metadata dict.
            db_evidence_id: Integer PK of EvidenceItem (for ChainOfCustody FK).
            hash_before: SHA-256 before the action (if applicable).
            hash_after: SHA-256 after the action (if applicable).
        """
        now = datetime.now(timezone.utc)
        ip_address = _get_client_ip()
        user_agent = _get_user_agent()

        # 1. Write to database (ChainOfCustody)
        if db_evidence_id is not None:
            try:
                from models.evidence import ChainOfCustody

                record = ChainOfCustody(
                    evidence_id=db_evidence_id,
                    action=action,
                    actor_name=actor_name or "system",
                    actor_id=actor_id,
                    action_timestamp=now,
                    action_details=_serialize_details(details),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    hash_before=hash_before,
                    hash_after=hash_after,
                )
                self._db.add(record)
                self._db.commit()
            except Exception as exc:
                logger.error(
                    "Failed to write audit to DB for evidence %s: %s",
                    evidence_id,
                    exc,
                    exc_info=True,
                )
                self._db.rollback()

        # 2. Append to manifest
        self._store.append_audit(
            evidence_id=evidence_id,
            action=action,
            actor=actor_name,
            details={
                **(details or {}),
                "actor_id": actor_id,
                "ip_address": ip_address,
                "hash_before": hash_before,
                "hash_after": hash_after,
            },
        )

        logger.info(
            "Audit [%s] evidence=%s actor=%s",
            action,
            evidence_id[:12] if evidence_id else "?",
            actor_name or actor_id or "system",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_client_ip() -> Optional[str]:
    """Extract client IP from Flask request context, if available."""
    try:
        return request.remote_addr
    except RuntimeError:
        return None


def _get_user_agent() -> Optional[str]:
    """Extract user agent string from Flask request context, if available."""
    try:
        ua = request.headers.get("User-Agent", "")
        return ua[:500] if ua else None
    except RuntimeError:
        return None


def _serialize_details(details: Optional[Dict]) -> Optional[str]:
    """Serialize details dict to JSON string for DB storage."""
    if details is None:
        return None
    import json

    try:
        return json.dumps(details, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(details)
