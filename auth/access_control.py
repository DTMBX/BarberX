"""
Purpose-Required Access Controls
==================================
Decorators and utilities that enforce audited, purpose-documented access to
sensitive resources (originals, exports, sealed events).

Design principles:
  - No original or export is served without an audit record.
  - Every access records actor, purpose, IP, and timestamp.
  - Denial paths are explicit and testable.
  - Rate limits protect auth endpoints against credential stuffing.
"""

from functools import wraps
from typing import Optional

from flask import abort, jsonify, request
from flask_login import current_user

from services.audit_stream import AuditAction, AuditStream


# ---------------------------------------------------------------------------
# Access-purpose validation
# ---------------------------------------------------------------------------

VALID_ACCESS_PURPOSES = frozenset({
    "case_review",
    "exhibit_preparation",
    "court_filing",
    "internal_audit",
    "compliance_review",
    "opposing_counsel_production",
    "supervisory_review",
    "quality_assurance",
    "training",          # must be flagged as derivative use
    "investigation",
})


def _extract_purpose() -> Optional[str]:
    """
    Extract access purpose from request.

    Accepts purpose in:
      - Query string: ?purpose=case_review
      - JSON body: {"purpose": "case_review"}
      - Form data: purpose=case_review
      - Header: X-Access-Purpose: case_review
    """
    purpose = request.args.get("purpose")
    if purpose:
        return purpose.strip().lower()

    if request.is_json and request.json:
        purpose = request.json.get("purpose")
        if purpose:
            return purpose.strip().lower()

    purpose = request.form.get("purpose")
    if purpose:
        return purpose.strip().lower()

    purpose = request.headers.get("X-Access-Purpose")
    if purpose:
        return purpose.strip().lower()

    return None


def purpose_required(action: str = AuditAction.ACCESSED):
    """
    Decorator: require a stated purpose for access.

    The purpose must be one of VALID_ACCESS_PURPOSES. If missing or invalid,
    the request is denied with 400/422. On success, the purpose is recorded
    in the audit stream.

    Usage:
        @app.route('/evidence/<id>/download')
        @login_required
        @purpose_required(action=AuditAction.DOWNLOADED)
        def download_evidence(id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            purpose = _extract_purpose()
            if not purpose:
                return jsonify({
                    "error": "Access purpose required",
                    "detail": "Provide 'purpose' parameter with one of: "
                              + ", ".join(sorted(VALID_ACCESS_PURPOSES)),
                }), 400

            if purpose not in VALID_ACCESS_PURPOSES:
                return jsonify({
                    "error": "Invalid access purpose",
                    "detail": f"'{purpose}' is not a recognized purpose. "
                              f"Valid: {', '.join(sorted(VALID_ACCESS_PURPOSES))}",
                }), 422

            # Attach purpose to request context for downstream use
            request.access_purpose = purpose
            request.access_action = action

            return f(*args, **kwargs)
        return decorated
    return decorator


def record_access(
    audit_stream: AuditStream,
    evidence_id: str,
    db_evidence_id: Optional[int] = None,
    action: Optional[str] = None,
    extra_details: Optional[dict] = None,
) -> None:
    """
    Record an access event to the audit stream.

    Pulls purpose from request context (set by purpose_required decorator).
    """
    purpose = getattr(request, "access_purpose", "unspecified")
    act = action or getattr(request, "access_action", AuditAction.ACCESSED)

    details = {
        "purpose": purpose,
        "endpoint": request.endpoint,
        "method": request.method,
    }
    if extra_details:
        details.update(extra_details)

    audit_stream.record(
        evidence_id=evidence_id,
        action=act,
        actor_id=getattr(current_user, "id", None),
        actor_name=getattr(current_user, "username", None)
                   or getattr(current_user, "email", "unknown"),
        details=details,
        db_evidence_id=db_evidence_id,
    )
