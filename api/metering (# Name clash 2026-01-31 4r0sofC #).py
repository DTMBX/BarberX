# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
API Usage Metering Routes
REST endpoints for managing API keys and usage tracking
"""

from datetime import datetime, timedelta
from functools import wraps

from api_usage_metering import (
    APIUsageMeteringService,
    EncryptedAPIKey,
    UserAPIQuota,
    check_rate_limit,
    get_metering_service,
    require_api_key,
)
from flask import Blueprint, g, jsonify, request
from flask_login import current_user, login_required
from models_auth import db
from tier_gating import check_tier_access

# Create blueprint
metering_bp = Blueprint("metering", __name__, url_prefix="/api/v1/metering")


# =============================================================================
# API KEY MANAGEMENT
# =============================================================================


@metering_bp.route("/api-keys", methods=["GET"])
@login_required
def list_api_keys():
    """
    List user's stored API keys (masked)

    Returns:
        List of API key metadata (no actual keys exposed)
    """
    keys = EncryptedAPIKey.query.filter_by(user_id=current_user.id).all()

    return jsonify(
        {
            "success": True,
            "api_keys": [
                {
                    "id": k.id,
                    "provider": k.provider,
                    "key_name": k.key_name,
                    "key_prefix": k.key_prefix,
                    "is_active": k.is_active,
                    "is_valid": k.is_valid,
                    "total_requests": k.total_requests,
                    "total_tokens": k.total_tokens,
                    "total_cost_usd": float(k.total_cost_usd) if k.total_cost_usd else 0,
                    "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                    "last_validated_at": (
                        k.last_validated_at.isoformat() if k.last_validated_at else None
                    ),
                    "validation_error": k.validation_error,
                    "created_at": k.created_at.isoformat(),
                }
                for k in keys
            ],
        }
    )


@metering_bp.route("/api-keys", methods=["POST"])
@login_required
def store_api_key():
    """
    Store a new API key (encrypted)

    Request JSON:
        {
            "provider": "openai",
            "api_key": "sk-...",
            "key_name": "My Production Key"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Request body required"}), 400

    provider = data.get("provider", "openai")
    api_key = data.get("api_key")
    key_name = data.get("key_name")

    if not api_key:
        return jsonify({"success": False, "error": "api_key is required"}), 400

    # Validate key format
    if provider == "openai" and not api_key.startswith("sk-"):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Invalid OpenAI API key format. Key should start with 'sk-'",
                }
            ),
            400,
        )

    service = get_metering_service()
    result = service.store_api_key(
        user_id=current_user.id,
        provider=provider,
        api_key=api_key,
        key_name=key_name,
    )

    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@metering_bp.route("/api-keys/<int:key_id>", methods=["DELETE"])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    service = get_metering_service()
    result = service.delete_api_key(current_user.id, key_id)

    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 404


@metering_bp.route("/api-keys/<int:key_id>/validate", methods=["POST"])
@login_required
def validate_api_key(key_id):
    """
    Validate a stored API key by making a test request
    """
    key_record = EncryptedAPIKey.query.filter_by(
        id=key_id,
        user_id=current_user.id,
    ).first()

    if not key_record:
        return jsonify({"success": False, "error": "API key not found"}), 404

    service = get_metering_service()
    result = service.validate_api_key(current_user.id, key_record.provider)

    return jsonify(
        {
            "success": result.get("valid", False),
            "provider": key_record.provider,
            "models_available": result.get("models_available", []),
            "error": result.get("error"),
        }
    )


@metering_bp.route("/api-keys/<int:key_id>/activate", methods=["POST"])
@login_required
def activate_api_key(key_id):
    """Set a key as the active key for its provider"""
    key_record = EncryptedAPIKey.query.filter_by(
        id=key_id,
        user_id=current_user.id,
    ).first()

    if not key_record:
        return jsonify({"success": False, "error": "API key not found"}), 404

    # Deactivate other keys for this provider
    EncryptedAPIKey.query.filter_by(
        user_id=current_user.id,
        provider=key_record.provider,
    ).update({"is_active": False})

    # Activate this key
    key_record.is_active = True
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": f"API key '{key_record.key_name}' is now active for {key_record.provider}",
        }
    )


# =============================================================================
# USAGE TRACKING
# =============================================================================


@metering_bp.route("/usage", methods=["GET"])
@login_required
def get_usage():
    """
    Get usage summary for current user

    Query params:
        days: Number of days to look back (default: 30)
    """
    days = request.args.get("days", 30, type=int)
    days = min(max(days, 1), 365)  # Clamp between 1 and 365

    service = get_metering_service()
    summary = service.get_usage_summary(current_user.id, days)

    return jsonify(
        {
            "success": True,
            "usage": summary,
        }
    )


@metering_bp.route("/usage/daily", methods=["GET"])
@login_required
def get_daily_usage():
    """
    Get daily usage breakdown

    Query params:
        days: Number of days (default: 7)
    """
    days = request.args.get("days", 7, type=int)
    days = min(max(days, 1), 90)

    service = get_metering_service()
    summary = service.get_usage_summary(current_user.id, days)

    return jsonify(
        {
            "success": True,
            "daily_usage": summary.get("daily_usage", []),
            "period_days": days,
        }
    )


@metering_bp.route("/usage/by-model", methods=["GET"])
@login_required
def get_usage_by_model():
    """Get usage breakdown by model"""
    days = request.args.get("days", 30, type=int)

    service = get_metering_service()
    summary = service.get_usage_summary(current_user.id, days)

    return jsonify(
        {
            "success": True,
            "by_model": summary.get("by_model", []),
            "period_days": days,
        }
    )


# =============================================================================
# QUOTA MANAGEMENT
# =============================================================================


@metering_bp.route("/quota", methods=["GET"])
@login_required
def get_quota():
    """Get current quota status"""
    quota = UserAPIQuota.query.filter_by(user_id=current_user.id).first()

    if not quota:
        # Return default limits based on tier
        limits = current_user.get_tier_limits()
        return jsonify(
            {
                "success": True,
                "quota": {
                    "monthly_token_limit": limits.get("ai_tokens_per_month", 100000),
                    "tokens_used": 0,
                    "tokens_remaining": limits.get("ai_tokens_per_month", 100000),
                    "usage_percent": 0,
                    "monthly_cost_limit_usd": limits.get("ai_budget_usd", 10.0),
                    "cost_used_usd": 0,
                    "cost_remaining_usd": limits.get("ai_budget_usd", 10.0),
                    "period_start": None,
                    "requests_per_minute": 60,
                },
            }
        )

    # Reset if new period
    quota.reset_if_new_period()

    tokens_remaining = max(0, quota.monthly_token_limit - quota.tokens_used_this_period)
    usage_percent = (
        (quota.tokens_used_this_period / quota.monthly_token_limit * 100)
        if quota.monthly_token_limit > 0
        else 0
    )
    cost_remaining = float(quota.monthly_cost_limit_usd - quota.cost_this_period_usd)

    return jsonify(
        {
            "success": True,
            "quota": {
                "monthly_token_limit": quota.monthly_token_limit,
                "tokens_used": quota.tokens_used_this_period,
                "tokens_remaining": tokens_remaining,
                "usage_percent": round(usage_percent, 2),
                "monthly_cost_limit_usd": float(quota.monthly_cost_limit_usd),
                "cost_used_usd": float(quota.cost_this_period_usd),
                "cost_remaining_usd": max(0, cost_remaining),
                "period_start": quota.period_start.isoformat() if quota.period_start else None,
                "requests_per_minute": quota.requests_per_minute,
                "alert_threshold_percent": quota.alert_threshold_percent,
                "alert_sent": quota.alert_sent,
            },
        }
    )


@metering_bp.route("/quota/check", methods=["GET"])
@login_required
def check_quota():
    """Quick check if user can make API requests"""
    service = get_metering_service()
    allowed, error = service.check_rate_limit(current_user.id)

    return jsonify(
        {
            "success": True,
            "allowed": allowed,
            "error": error,
        }
    )


# =============================================================================
# AUDIT & VERIFICATION
# =============================================================================


@metering_bp.route("/audit", methods=["GET"])
@login_required
def get_audit_trail():
    """
    Get verifiable usage audit trail

    Query params:
        start_date: ISO date string
        end_date: ISO date string
        limit: Max records (default: 100)
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", 100, type=int)
    limit = min(max(limit, 1), 1000)

    # Parse dates
    start = None
    end = None

    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"success": False, "error": "Invalid start_date format"}), 400

    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"success": False, "error": "Invalid end_date format"}), 400

    service = get_metering_service()
    audit_records = service.export_usage_audit(
        current_user.id,
        start_date=start,
        end_date=end,
    )[:limit]

    # Compute overall verification hash
    all_hashes = [r["record_hash"] for r in audit_records if r["record_hash"]]
    combined_hash = None
    if all_hashes:
        import hashlib

        combined_hash = hashlib.sha256(":".join(all_hashes).encode()).hexdigest()

    return jsonify(
        {
            "success": True,
            "records": audit_records,
            "total_records": len(audit_records),
            "verification_hash": combined_hash,
            "all_verified": all(r["verified"] for r in audit_records),
        }
    )


@metering_bp.route("/audit/<int:log_id>/verify", methods=["GET"])
@login_required
def verify_usage_log(log_id):
    """Verify integrity of a specific usage log entry"""
    from api_usage_metering import APIUsageLog

    # Verify ownership
    log = APIUsageLog.query.filter_by(
        id=log_id,
        user_id=current_user.id,
    ).first()

    if not log:
        return jsonify({"success": False, "error": "Log entry not found"}), 404

    service = get_metering_service()
    result = service.verify_usage_log(log_id)

    return jsonify(
        {
            "success": True,
            "verification": result,
        }
    )


# =============================================================================
# COST ESTIMATION
# =============================================================================


@metering_bp.route("/estimate", methods=["POST"])
@login_required
def estimate_cost():
    """
    Estimate cost for a planned API call

    Request JSON:
        {
            "provider": "openai",
            "model": "gpt-4",
            "prompt_tokens": 1000,
            "completion_tokens": 500
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Request body required"}), 400

    provider = data.get("provider", "openai")
    model = data.get("model", "gpt-4")
    prompt_tokens = data.get("prompt_tokens", 0)
    completion_tokens = data.get("completion_tokens", 0)

    from api_usage_metering import APIPricingCalculator

    cost = APIPricingCalculator.calculate_cost(provider, model, prompt_tokens, completion_tokens)

    return jsonify(
        {
            "success": True,
            "estimate": {
                "provider": provider,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "estimated_cost_usd": float(cost),
                "formatted_cost": f"${cost:.6f}",
            },
        }
    )


@metering_bp.route("/pricing", methods=["GET"])
def get_pricing():
    """Get current API pricing information"""
    from api_usage_metering import APIPricingCalculator

    return jsonify(
        {
            "success": True,
            "pricing": APIPricingCalculator.PRICING,
            "note": "Prices are per 1,000 tokens in USD",
        }
    )


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================


def admin_required(f):
    """Decorator to require admin access"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if not current_user.is_admin_user:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


@metering_bp.route("/admin/usage/all", methods=["GET"])
@login_required
@admin_required
def admin_get_all_usage():
    """
    [Admin] Get usage across all users

    Query params:
        days: Number of days (default: 30)
        limit: Max users (default: 100)
    """
    from api_usage_metering import APIUsageLog
    from sqlalchemy import func

    days = request.args.get("days", 30, type=int)
    limit = request.args.get("limit", 100, type=int)

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Aggregate by user
    user_stats = (
        db.session.query(
            APIUsageLog.user_id,
            func.sum(APIUsageLog.total_tokens).label("total_tokens"),
            func.sum(APIUsageLog.estimated_cost_usd).label("total_cost"),
            func.count(APIUsageLog.id).label("total_requests"),
        )
        .filter(
            APIUsageLog.created_at >= cutoff,
        )
        .group_by(
            APIUsageLog.user_id,
        )
        .order_by(
            func.sum(APIUsageLog.total_tokens).desc(),
        )
        .limit(limit)
        .all()
    )

    return jsonify(
        {
            "success": True,
            "period_days": days,
            "user_usage": [
                {
                    "user_id": s.user_id,
                    "total_tokens": s.total_tokens or 0,
                    "total_cost_usd": float(s.total_cost or 0),
                    "total_requests": s.total_requests or 0,
                }
                for s in user_stats
            ],
        }
    )


@metering_bp.route("/admin/quota/<int:user_id>", methods=["PUT"])
@login_required
@admin_required
def admin_update_quota(user_id):
    """
    [Admin] Update user's quota limits

    Request JSON:
        {
            "monthly_token_limit": 500000,
            "monthly_cost_limit_usd": 50.00,
            "requests_per_minute": 120
        }
    """
    data = request.get_json()

    quota = UserAPIQuota.query.filter_by(user_id=user_id).first()

    if not quota:
        quota = UserAPIQuota(user_id=user_id)
        db.session.add(quota)

    if "monthly_token_limit" in data:
        quota.monthly_token_limit = data["monthly_token_limit"]
    if "monthly_cost_limit_usd" in data:
        from decimal import Decimal

        quota.monthly_cost_limit_usd = Decimal(str(data["monthly_cost_limit_usd"]))
    if "requests_per_minute" in data:
        quota.requests_per_minute = data["requests_per_minute"]
    if "alert_threshold_percent" in data:
        quota.alert_threshold_percent = data["alert_threshold_percent"]

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": f"Quota updated for user {user_id}",
            "quota": {
                "monthly_token_limit": quota.monthly_token_limit,
                "monthly_cost_limit_usd": float(quota.monthly_cost_limit_usd),
                "requests_per_minute": quota.requests_per_minute,
            },
        }
    )


# =============================================================================
# REGISTRATION
# =============================================================================


def register_metering_routes(app):
    """Register metering blueprint with Flask app"""
    app.register_blueprint(metering_bp)
