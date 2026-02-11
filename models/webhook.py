"""
Webhook Subscription Model
=============================
Stores webhook endpoints that receive HMAC-signed event notifications.

Design principles:
  - HMAC-SHA256 signing: every payload is signed with the subscription's
    secret so recipients can verify authenticity.
  - Subscriptions are scoped to specific event types.
  - Failed deliveries are tracked (consecutive failure count, last error).
  - Subscriptions are auto-disabled after MAX_CONSECUTIVE_FAILURES.
  - Secrets are stored as-is (server-side only, never sent after creation).
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from auth.models import db


class WebhookSubscription(db.Model):
    """
    A registered webhook endpoint that receives event notifications.

    One subscription can listen to multiple event types (stored as
    comma-separated list).  Each delivery is HMAC-SHA256 signed with
    the subscription's secret.
    """

    __tablename__ = "webhook_subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    # Owner
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    user = db.relationship("User")

    # Endpoint
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    secret = db.Column(db.String(128), nullable=False)

    # Event filter — comma-separated event types, or "*" for all
    event_types = db.Column(db.String(1024), nullable=False, default="*")

    # State
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Delivery health
    consecutive_failures = db.Column(db.Integer, default=0, nullable=False)
    last_failure_at = db.Column(db.DateTime, nullable=True)
    last_failure_reason = db.Column(db.String(1024), nullable=True)
    last_success_at = db.Column(db.DateTime, nullable=True)
    total_deliveries = db.Column(db.Integer, default=0, nullable=False)

    # Audit
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Auto-disable after this many consecutive failures
    MAX_CONSECUTIVE_FAILURES = 10

    # --------------- Valid event types ---------------

    VALID_EVENTS = frozenset(
        {
            "evidence.ingested",
            "evidence.integrity_verified",
            "evidence.integrity_failed",
            "evidence.exported",
            "case.created",
            "case.updated",
            "case.exported",
            "share_link.created",
            "share_link.accessed",
            "share_link.revoked",
            "audit.critical",
        }
    )

    # --------------- Helpers ---------------

    @staticmethod
    def generate_secret() -> str:
        """Generate a 64-character hex secret for HMAC signing."""
        return secrets.token_hex(32)

    @staticmethod
    def sign_payload(secret: str, payload_bytes: bytes) -> str:
        """
        Compute HMAC-SHA256 signature for a payload.

        Returns hex digest string.
        """
        return hmac.new(
            secret.encode("utf-8"), payload_bytes, hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_signature(secret: str, payload_bytes: bytes, signature: str) -> bool:
        """Constant-time comparison of expected vs. provided signature."""
        expected = WebhookSubscription.sign_payload(secret, payload_bytes)
        return hmac.compare_digest(expected, signature)

    def matches_event(self, event_type: str) -> bool:
        """Return True if this subscription listens for the given event type."""
        if not self.is_active:
            return False
        if self.event_types.strip() == "*":
            return True
        subscribed = {e.strip() for e in self.event_types.split(",") if e.strip()}
        return event_type in subscribed

    def record_success(self) -> None:
        """Record a successful delivery."""
        self.consecutive_failures = 0
        self.last_success_at = datetime.now(timezone.utc)
        self.total_deliveries += 1

    def record_failure(self, reason: str) -> None:
        """
        Record a failed delivery.  Auto-disables after MAX_CONSECUTIVE_FAILURES.
        """
        self.consecutive_failures += 1
        self.last_failure_at = datetime.now(timezone.utc)
        self.last_failure_reason = reason[:1024] if reason else None
        self.total_deliveries += 1

        if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self.is_active = False

    def to_dict(self, include_secret: bool = False) -> dict:
        """Serialise for API responses.  Secret is excluded by default."""
        d = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "event_types": self.event_types,
            "is_active": self.is_active,
            "consecutive_failures": self.consecutive_failures,
            "last_success_at": (
                self.last_success_at.isoformat() if self.last_success_at else None
            ),
            "total_deliveries": self.total_deliveries,
            "created_at": self.created_at.isoformat(),
        }
        if include_secret:
            d["secret"] = self.secret
        return d

    def __repr__(self):
        return f"<WebhookSubscription {self.name} → {self.url}>"


class WebhookDeliveryLog(db.Model):
    """
    Append-only log of every webhook delivery attempt.

    This table is never updated — each attempt creates a new row.
    """

    __tablename__ = "webhook_delivery_log"

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(
        db.Integer,
        db.ForeignKey("webhook_subscriptions.id"),
        nullable=False,
        index=True,
    )
    subscription = db.relationship("WebhookSubscription")

    event_type = db.Column(db.String(100), nullable=False, index=True)
    payload_hash = db.Column(db.String(64), nullable=False)  # SHA-256 of payload
    response_status = db.Column(db.Integer, nullable=True)  # HTTP status or None
    response_body_preview = db.Column(db.String(500), nullable=True)
    error_message = db.Column(db.String(1024), nullable=True)

    success = db.Column(db.Boolean, nullable=False)
    duration_ms = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
