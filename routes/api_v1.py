"""
Versioned REST API — /api/v1/
================================
Programmatic, JSON-only interface for cases, evidence, and audit records.

Design principles:
  - Read-only by default: no mutation of original evidence.
  - Bearer-token authentication (ApiToken).
  - Every request is audit-logged with token name and IP.
  - Pagination via `page` and `per_page` query parameters.
  - No PII leakage: evidence content bytes are never served.
  - Webhook management endpoints for subscriptions.
  - Token lifecycle endpoints (list, create, revoke own tokens).
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth.api_auth import api_admin_required, api_token_required
from auth.models import ApiToken, db

logger = logging.getLogger(__name__)

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Maximum items per page
MAX_PER_PAGE = 100
DEFAULT_PER_PAGE = 25


# ===================================================================
# Helpers
# ===================================================================


def _paginate(query, default_per_page=DEFAULT_PER_PAGE):
    """Apply page/per_page to a SQLAlchemy query. Return (items, meta)."""
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(MAX_PER_PAGE, max(1, request.args.get("per_page", default_per_page, type=int)))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    meta = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
    return pagination.items, meta


def _case_to_dict(case):
    """Serialise a LegalCase for the API (no PII, no evidence bytes)."""
    return {
        "id": case.id,
        "case_number": case.case_number,
        "case_name": case.case_name,
        "case_type": case.case_type,
        "status": case.status,
        "jurisdiction": case.jurisdiction,
        "jurisdiction_state": case.jurisdiction_state,
        "court_name": case.court_name,
        "filed_date": case.filed_date.isoformat() if case.filed_date else None,
        "trial_date": case.trial_date.isoformat() if case.trial_date else None,
        "discovery_deadline": (
            case.discovery_deadline.isoformat() if case.discovery_deadline else None
        ),
        "is_legal_hold": case.is_legal_hold,
        "evidence_count": case.evidence_count,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
    }


def _evidence_to_dict(item):
    """Serialise an EvidenceItem for the API (metadata + hash, no bytes)."""
    return {
        "id": item.id,
        "original_filename": item.original_filename,
        "evidence_type": item.evidence_type,
        "file_type": item.file_type,
        "file_size_bytes": item.file_size_bytes,
        "hash_sha256": item.hash_sha256,
        "hash_md5": item.hash_md5,
        "processing_status": item.processing_status,
        "collected_date": (
            item.collected_date.isoformat() if item.collected_date else None
        ),
        "collected_by": item.collected_by,
        "device_label": item.device_label,
        "device_type": item.device_type,
        "duration_seconds": item.duration_seconds,
        "is_under_legal_hold": item.is_under_legal_hold,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _audit_to_dict(entry):
    """Serialise a ChainOfCustody entry for the API."""
    return {
        "id": entry.id,
        "evidence_id": entry.evidence_id,
        "action": entry.action,
        "actor_name": entry.actor_name,
        "action_timestamp": (
            entry.action_timestamp.isoformat() if entry.action_timestamp else None
        ),
        "hash_before": entry.hash_before,
        "hash_after": entry.hash_after,
        "ip_address": entry.ip_address,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


# ===================================================================
# Cases
# ===================================================================


@api_v1_bp.route("/cases", methods=["GET"])
@api_token_required
def list_cases():
    """
    List cases (paginated).

    Query params:
        status (str, optional) — filter by case status
        case_type (str, optional) — filter by case type
        page (int, default 1)
        per_page (int, default 25, max 100)
    """
    from models.legal_case import LegalCase

    query = LegalCase.query.order_by(LegalCase.created_at.desc())

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    case_type = request.args.get("case_type")
    if case_type:
        query = query.filter_by(case_type=case_type)

    items, meta = _paginate(query)
    return jsonify({"cases": [_case_to_dict(c) for c in items], "meta": meta})


@api_v1_bp.route("/cases/<int:case_id>", methods=["GET"])
@api_token_required
def get_case(case_id):
    """Get a single case by ID, including evidence summary."""
    from models.legal_case import LegalCase

    case = db.session.get(LegalCase, case_id)
    if case is None:
        return jsonify({"error": "Case not found"}), 404

    data = _case_to_dict(case)
    data["evidence"] = [_evidence_to_dict(e) for e in case.evidence_items]
    return jsonify(data)


# ===================================================================
# Evidence
# ===================================================================


@api_v1_bp.route("/evidence", methods=["GET"])
@api_token_required
def list_evidence():
    """
    List evidence items (paginated).

    Query params:
        evidence_type (str, optional)
        processing_status (str, optional)
        page, per_page
    """
    from models.evidence import EvidenceItem

    query = EvidenceItem.query.order_by(EvidenceItem.created_at.desc())

    etype = request.args.get("evidence_type")
    if etype:
        query = query.filter_by(evidence_type=etype)

    pstatus = request.args.get("processing_status")
    if pstatus:
        query = query.filter_by(processing_status=pstatus)

    items, meta = _paginate(query)
    return jsonify({"evidence": [_evidence_to_dict(e) for e in items], "meta": meta})


@api_v1_bp.route("/evidence/<int:evidence_id>", methods=["GET"])
@api_token_required
def get_evidence(evidence_id):
    """Get a single evidence item by ID."""
    from models.evidence import EvidenceItem

    item = db.session.get(EvidenceItem, evidence_id)
    if item is None:
        return jsonify({"error": "Evidence item not found"}), 404

    return jsonify(_evidence_to_dict(item))


@api_v1_bp.route("/evidence/<int:evidence_id>/audit", methods=["GET"])
@api_token_required
def get_evidence_audit(evidence_id):
    """Get chain-of-custody entries for an evidence item (paginated)."""
    from models.evidence import ChainOfCustody, EvidenceItem

    item = db.session.get(EvidenceItem, evidence_id)
    if item is None:
        return jsonify({"error": "Evidence item not found"}), 404

    query = (
        ChainOfCustody.query
        .filter_by(evidence_id=evidence_id)
        .order_by(ChainOfCustody.action_timestamp.desc())
    )
    items, meta = _paginate(query)
    return jsonify({"audit_trail": [_audit_to_dict(e) for e in items], "meta": meta})


@api_v1_bp.route("/evidence/verify/<hash_sha256>", methods=["GET"])
@api_token_required
def verify_evidence_hash(hash_sha256):
    """
    Look up evidence by SHA-256 hash and return verification status.

    Returns 200 with match details if found, 404 if no match.
    """
    from models.evidence import EvidenceItem

    item = EvidenceItem.query.filter_by(hash_sha256=hash_sha256).first()
    if item is None:
        return jsonify({
            "verified": False,
            "hash_sha256": hash_sha256,
            "message": "No evidence found matching this hash",
        }), 404

    return jsonify({
        "verified": True,
        "hash_sha256": hash_sha256,
        "evidence_id": item.id,
        "original_filename": item.original_filename,
        "evidence_type": item.evidence_type,
        "processing_status": item.processing_status,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    })


# ===================================================================
# Audit (global)
# ===================================================================


@api_v1_bp.route("/audit", methods=["GET"])
@api_token_required
def list_audit():
    """
    List chain-of-custody entries across all evidence (paginated).

    Query params:
        action (str, optional) — filter by action type
        since (ISO datetime, optional) — entries after this timestamp
        page, per_page
    """
    from models.evidence import ChainOfCustody

    query = ChainOfCustody.query.order_by(ChainOfCustody.action_timestamp.desc())

    action_filter = request.args.get("action")
    if action_filter:
        query = query.filter_by(action=action_filter)

    since = request.args.get("since")
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.filter(ChainOfCustody.action_timestamp >= since_dt)
        except ValueError:
            return jsonify({"error": "Invalid 'since' datetime format"}), 400

    items, meta = _paginate(query)
    return jsonify({"audit_trail": [_audit_to_dict(e) for e in items], "meta": meta})


# ===================================================================
# Tokens (self-service)
# ===================================================================


@api_v1_bp.route("/tokens", methods=["GET"])
@api_token_required
def list_tokens():
    """List the authenticated user's API tokens (names + metadata, not secrets)."""
    tokens = ApiToken.query.filter_by(user_id=g.api_user.id).all()
    return jsonify({
        "tokens": [
            {
                "id": t.id,
                "name": t.name,
                "is_active": t.is_active,
                "last_used_at": t.last_used_at.isoformat() if t.last_used_at else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "expires_at": t.expires_at.isoformat() if t.expires_at else None,
            }
            for t in tokens
        ]
    })


@api_v1_bp.route("/tokens", methods=["POST"])
@api_token_required
def create_token():
    """
    Create a new API token for the authenticated user.

    JSON body:
        name (str, required) — human-readable token label
        expires_in_days (int, optional) — days until expiry (default: no expiry)
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Token name is required"}), 400

    from datetime import timedelta

    expires_in = data.get("expires_in_days")
    expires_at = None
    if expires_in is not None:
        try:
            expires_in = int(expires_in)
            if expires_in < 1:
                raise ValueError
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in)
        except (ValueError, TypeError):
            return jsonify({"error": "expires_in_days must be a positive integer"}), 400

    raw_token = ApiToken.generate_token()
    token_obj = ApiToken(
        token=raw_token,
        name=name,
        user_id=g.api_user.id,
        expires_at=expires_at,
    )
    db.session.add(token_obj)
    db.session.commit()

    logger.info("API token created: id=%d name=%s user=%s", token_obj.id, name, g.api_user.email)

    return jsonify({
        "id": token_obj.id,
        "name": token_obj.name,
        "token": raw_token,  # Returned ONCE — never retrievable again
        "expires_at": expires_at.isoformat() if expires_at else None,
    }), 201


@api_v1_bp.route("/tokens/<int:token_id>", methods=["DELETE"])
@api_token_required
def revoke_token(token_id):
    """Revoke (deactivate) an API token owned by the authenticated user."""
    token_obj = db.session.get(ApiToken, token_id)
    if token_obj is None or token_obj.user_id != g.api_user.id:
        return jsonify({"error": "Token not found"}), 404

    token_obj.is_active = False
    db.session.commit()

    logger.info("API token revoked: id=%d user=%s", token_id, g.api_user.email)
    return jsonify({"message": "Token revoked", "id": token_id})


# ===================================================================
# Webhooks
# ===================================================================


@api_v1_bp.route("/webhooks", methods=["GET"])
@api_token_required
def list_webhooks():
    """List webhook subscriptions for the authenticated user."""
    from services.webhook_service import WebhookService

    subs = WebhookService.list_subscriptions(g.api_user.id)
    return jsonify({"webhooks": [s.to_dict() for s in subs]})


@api_v1_bp.route("/webhooks", methods=["POST"])
@api_token_required
def create_webhook():
    """
    Register a new webhook subscription.

    JSON body:
        name (str, required)
        url (str, required) — must be HTTPS
        event_types (str, optional) — comma-separated, default "*"

    Returns the subscription WITH secret (returned once).
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    event_types = data.get("event_types", "*").strip()

    if not name or not url:
        return jsonify({"error": "name and url are required"}), 400

    if not url.startswith("https://"):
        return jsonify({"error": "Webhook URL must use HTTPS"}), 400

    try:
        from services.webhook_service import WebhookService

        sub = WebhookService.create_subscription(
            user_id=g.api_user.id,
            name=name,
            url=url,
            event_types=event_types,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify(sub.to_dict(include_secret=True)), 201


@api_v1_bp.route("/webhooks/<int:sub_id>", methods=["DELETE"])
@api_token_required
def delete_webhook(sub_id):
    """Deactivate a webhook subscription."""
    from services.webhook_service import WebhookService

    ok = WebhookService.delete_subscription(sub_id, g.api_user.id)
    if not ok:
        return jsonify({"error": "Webhook not found"}), 404
    return jsonify({"message": "Webhook deactivated", "id": sub_id})


# ===================================================================
# Health / version
# ===================================================================


@api_v1_bp.route("/health", methods=["GET"])
def api_health():
    """Public health check for the v1 API (no auth required)."""
    version_str = "unknown"
    try:
        with open("VERSION") as f:
            version_str = f.read().strip()
    except FileNotFoundError:
        pass

    return jsonify({
        "status": "ok",
        "api_version": "v1",
        "version": version_str,
    })
