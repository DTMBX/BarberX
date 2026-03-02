"""
AI Assistant Action Endpoint
=============================
Single entry point for all assistant-initiated actions.

POST /assistant/action
    - Validates capability_id
    - Enforces role
    - Validates input schema
    - Dispatches to handler
    - Returns result with audit reference

GET /assistant/capabilities
    - Lists all registered capabilities (metadata only)

GET /assistant/history
    - Returns recent audit log for assistant actions

All actions are logged. No silent execution.
"""

import uuid
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from backend.app.core.capability_registry import registry


assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")


@assistant_bp.route("/action", methods=["POST"])
@login_required
def execute_action():
    """
    Execute an assistant capability action.

    Request JSON:
        {
            "capability_id": "case.create_note",
            "case_id": "abc-123",        (optional, depends on capability)
            "args": { ... },
            "request_id": "req-uuid"      (optional, generated if missing)
        }

    Response JSON:
        {
            "status": "success" | "denied" | "validation_error" | "error",
            "result": { ... },            (on success)
            "errors": [...],              (on validation_error)
            "error": "...",               (on error/denied)
            "audit_reference": "uuid"
        }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True) or {}
    capability_id = data.get("capability_id")

    if not capability_id:
        return jsonify({"error": "Missing required field: capability_id"}), 400

    # Build execution context from authenticated user
    context = {
        "request_id": data.get("request_id", str(uuid.uuid4())),
        "case_id": data.get("case_id"),
        "actor_id": getattr(current_user, "id", None),
        "actor_name": (
            getattr(current_user, "username", None)
            or getattr(current_user, "email", "unknown")
        ),
        "actor_role": (
            current_user.role.value
            if hasattr(current_user, "role") and hasattr(current_user.role, "value")
            else str(getattr(current_user, "role", "USER"))
        ),
        "ip_address": request.remote_addr,
    }

    args = data.get("args", {})

    result = registry.execute(
        capability_id=capability_id,
        args=args,
        context=context,
    )

    # Map status to HTTP codes
    status_codes = {
        "success": 200,
        "denied": 403,
        "validation_error": 422,
        "error": 500,
    }
    http_status = status_codes.get(result.get("status"), 500)

    return jsonify(result), http_status


@assistant_bp.route("/capabilities", methods=["GET"])
@login_required
def list_capabilities():
    """Return all registered capabilities (metadata, no handlers)."""
    capabilities = registry.list_capabilities()
    return jsonify({
        "capabilities": capabilities,
        "count": len(capabilities),
    })


@assistant_bp.route("/history", methods=["GET"])
@login_required
def action_history():
    """Return recent assistant action audit log."""
    capability_filter = request.args.get("capability_id")
    limit = min(int(request.args.get("limit", 50)), 200)

    records = registry.get_audit_log(
        capability_id=capability_filter,
        limit=limit,
    )

    return jsonify({
        "records": records,
        "count": len(records),
    })
