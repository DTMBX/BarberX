"""
Secure Share-Link Model
========================
Expiring, revocable, audited share tokens for controlled external access.

Design principles:
  - Tokens are cryptographically random (32 bytes / 64 hex chars).
  - Token hashes (SHA-256) are stored, not plain tokens.
  - Every share link has a mandatory expiry.
  - Revocation is soft (revoked_at timestamp), preserving the audit trail.
  - Scope is explicit: which case, which evidence IDs, read-only vs. export.
  - All access through share links is recorded in ChainOfCustody.
"""

import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Optional

from auth.models import db


class ShareLink(db.Model):
    """
    A time-limited, revocable access token granting read-only access
    to a specific case or subset of evidence.

    The raw token is returned ONCE at creation and never stored.
    Only the SHA-256 hash of the token is persisted.
    """
    __tablename__ = "share_link"

    id = db.Column(db.Integer, primary_key=True)

    # Token identity — SHA-256 of the raw bearer token
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # What is shared
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    evidence_ids_json = db.Column(db.Text, nullable=True)  # JSON array, null = entire case

    # Scope
    scope = db.Column(db.String(30), nullable=False, default="read_only")
    # read_only  — view metadata + originals
    # export     — download court package

    # Recipient metadata (informational, not auth)
    recipient_name = db.Column(db.String(300), nullable=False)
    recipient_email = db.Column(db.String(255), nullable=True)
    recipient_role = db.Column(db.String(100), nullable=False)  # attorney, co-counsel, expert_witness, auditor

    # Lifecycle
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)
    revoked_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Access tracking
    access_count = db.Column(db.Integer, nullable=False, default=0)
    max_access_count = db.Column(db.Integer, nullable=True)  # null = unlimited
    last_accessed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    case = db.relationship("LegalCase", backref="share_links")
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    revoked_by = db.relationship("User", foreign_keys=[revoked_by_id])

    # -------------------------------------------------------------------
    # Class helpers
    # -------------------------------------------------------------------

    VALID_SCOPES = frozenset({"read_only", "export"})
    VALID_RECIPIENT_ROLES = frozenset({
        "attorney",
        "co_counsel",
        "expert_witness",
        "auditor",
        "opposing_counsel",
        "insurance_adjuster",
    })
    MAX_EXPIRY_DAYS = 90  # Hard ceiling

    @staticmethod
    def generate_token() -> str:
        """Return a cryptographically random 64-hex-char token."""
        return secrets.token_hex(32)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """SHA-256 hash of a raw token string."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _utcnow():
        """Timezone-aware UTC now, safe for SQLite (which strips tzinfo)."""
        return datetime.now(timezone.utc)

    @staticmethod
    def _ensure_aware(dt: datetime) -> datetime:
        """Ensure a datetime is timezone-aware (SQLite may strip tzinfo)."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @property
    def is_active(self) -> bool:
        """True if the link is neither expired nor revoked, and within access limits."""
        now = self._utcnow()
        if self.revoked_at is not None:
            return False
        if self._ensure_aware(self.expires_at) <= now:
            return False
        if self.max_access_count is not None and self.access_count >= self.max_access_count:
            return False
        return True

    @property
    def evidence_ids(self) -> Optional[list]:
        """Parse evidence_ids_json into a list (or None for whole-case)."""
        if self.evidence_ids_json is None:
            return None
        return json.loads(self.evidence_ids_json)

    @evidence_ids.setter
    def evidence_ids(self, ids: Optional[list]):
        if ids is None:
            self.evidence_ids_json = None
        else:
            self.evidence_ids_json = json.dumps(sorted(set(ids)))

    def record_access(self) -> None:
        """Increment access counter and update last-accessed timestamp."""
        self.access_count += 1
        self.last_accessed_at = datetime.now(timezone.utc)

    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f"<ShareLink id={self.id} case={self.case_id} scope={self.scope} [{status}]>"
