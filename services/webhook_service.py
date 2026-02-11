"""
Webhook Delivery Service
==========================
Dispatches event notifications to registered webhook subscriptions.

Design principles:
  - Fire-and-forget with retry tolerance (not blocking the caller).
  - Every delivery attempt is logged to WebhookDeliveryLog.
  - Payloads are signed with HMAC-SHA256 using the subscription secret.
  - Subscriptions auto-disable after 10 consecutive failures.
  - No sensitive data (passwords, tokens) is included in payloads.

Usage:
    from services.webhook_service import WebhookService
    WebhookService.dispatch("evidence.ingested", {
        "evidence_id": 42,
        "hash_sha256": "abc123...",
    })
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Timeout for webhook HTTP calls (seconds)
_DELIVERY_TIMEOUT = 10


class WebhookService:
    """Dispatches events to registered webhook subscriptions."""

    @staticmethod
    def dispatch(event_type: str, payload: Dict[str, Any]) -> int:
        """
        Send an event to all matching active subscriptions.

        Parameters
        ----------
        event_type : str
            One of WebhookSubscription.VALID_EVENTS.
        payload : dict
            JSON-serialisable event data.  Must not contain secrets.

        Returns
        -------
        int
            Number of subscriptions notified (attempts, not successes).
        """
        from auth.models import db
        from models.webhook import WebhookSubscription

        subs = (
            WebhookSubscription.query
            .filter_by(is_active=True)
            .all()
        )

        matching = [s for s in subs if s.matches_event(event_type)]
        if not matching:
            return 0

        envelope = _build_envelope(event_type, payload)
        payload_bytes = json.dumps(envelope, sort_keys=True, default=str).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        count = 0
        for sub in matching:
            _deliver(sub, event_type, payload_bytes, payload_hash)
            count += 1

        db.session.commit()
        return count

    @staticmethod
    def create_subscription(
        user_id: int,
        name: str,
        url: str,
        event_types: str = "*",
    ) -> "WebhookSubscription":
        """
        Register a new webhook subscription.

        Returns the subscription with the secret populated (returned once).
        """
        from auth.models import db
        from models.webhook import WebhookSubscription

        # Validate event types
        if event_types.strip() != "*":
            requested = {e.strip() for e in event_types.split(",") if e.strip()}
            invalid = requested - WebhookSubscription.VALID_EVENTS
            if invalid:
                raise ValueError(f"Invalid event types: {', '.join(sorted(invalid))}")

        secret = WebhookSubscription.generate_secret()
        sub = WebhookSubscription(
            user_id=user_id,
            name=name,
            url=url,
            secret=secret,
            event_types=event_types,
        )
        db.session.add(sub)
        db.session.commit()

        logger.info("Webhook subscription created: id=%d name=%s url=%s", sub.id, name, url)
        return sub

    @staticmethod
    def delete_subscription(subscription_id: int, user_id: int) -> bool:
        """
        Deactivate (soft-delete) a webhook subscription.

        Returns True if deactivated, False if not found or not owned.
        """
        from auth.models import db
        from models.webhook import WebhookSubscription

        sub = db.session.get(WebhookSubscription, subscription_id)
        if sub is None or sub.user_id != user_id:
            return False

        sub.is_active = False
        db.session.commit()

        logger.info("Webhook subscription deactivated: id=%d", subscription_id)
        return True

    @staticmethod
    def list_subscriptions(user_id: int) -> list:
        """Return all subscriptions for a user (active and inactive)."""
        from models.webhook import WebhookSubscription

        return (
            WebhookSubscription.query
            .filter_by(user_id=user_id)
            .order_by(WebhookSubscription.created_at.desc())
            .all()
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_envelope(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap payload in a standard envelope with event metadata."""
    return {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


def _deliver(
    sub: "WebhookSubscription",
    event_type: str,
    payload_bytes: bytes,
    payload_hash: str,
) -> None:
    """
    Attempt a single webhook delivery.  Logs the result to WebhookDeliveryLog.
    """
    from auth.models import db
    from models.webhook import WebhookDeliveryLog, WebhookSubscription

    signature = WebhookSubscription.sign_payload(sub.secret, payload_bytes)

    headers = {
        "Content-Type": "application/json",
        "X-Evident-Event": event_type,
        "X-Evident-Signature": signature,
        "X-Evident-Delivery": payload_hash[:16],
        "User-Agent": "Evident-Webhook/1.0",
    }

    start = time.monotonic()
    success = False
    status_code: Optional[int] = None
    body_preview: Optional[str] = None
    error_msg: Optional[str] = None

    try:
        import requests as http_lib

        resp = http_lib.post(
            sub.url,
            data=payload_bytes,
            headers=headers,
            timeout=_DELIVERY_TIMEOUT,
        )
        status_code = resp.status_code
        body_preview = resp.text[:500] if resp.text else None
        success = 200 <= resp.status_code < 300

    except Exception as exc:
        error_msg = str(exc)[:1024]
        logger.warning(
            "Webhook delivery failed: sub=%d url=%s error=%s",
            sub.id,
            sub.url,
            error_msg,
        )

    duration_ms = int((time.monotonic() - start) * 1000)

    # Update subscription health
    if success:
        sub.record_success()
    else:
        sub.record_failure(error_msg or f"HTTP {status_code}")

    # Append-only delivery log
    log_entry = WebhookDeliveryLog(
        subscription_id=sub.id,
        event_type=event_type,
        payload_hash=payload_hash,
        response_status=status_code,
        response_body_preview=body_preview,
        error_message=error_msg,
        success=success,
        duration_ms=duration_ms,
    )
    db.session.add(log_entry)
