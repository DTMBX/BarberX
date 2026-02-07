# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Dashboard Enhancements - User Analytics & Churn Monitoring
Add retention metrics, risk scores, and engagement tracking
"""

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from .models_auth import UsageQuota, User
from .user_analytics import check_churn_risk

dashboard_bp = Blueprint("dashboard_analytics", __name__)


@dashboard_bp.route("/api/user/analytics")
@login_required
def get_user_analytics():
    """Get comprehensive user analytics for current user"""
    from login_security import login_security

    # Get churn risk
    churn_analysis = check_churn_risk(current_user)

    # Get usage quota
    quota = UsageQuota.query.filter_by(user_id=current_user.id).first()

    # Get login security status
    risk_assessment = login_security.get_risk_score(
        user_id=current_user.id, email=current_user.email
    )

    return jsonify(
        {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "tier": current_user.tier.name,
                "is_admin": current_user.is_admin,
                "created_at": current_user.created_at.isoformat(),
                "last_login": (
                    current_user.last_login.isoformat() if current_user.last_login else None
                ),
            },
            "churn_risk": churn_analysis,
            "security": {
                "device_fingerprint": risk_assessment.get("device_fingerprint"),
                "current_risk_score": risk_assessment.get("risk_score"),
                "is_suspicious": risk_assessment.get("is_suspicious"),
            },
            "usage": {
                "ai_requests": quota.ai_requests_count if quota else 0,
                "files_uploaded": quota.files_uploaded_count if quota else 0,
                "storage_used_mb": round(quota.storage_bytes_used / 1048576, 2) if quota else 0,
            },
        }
    )


@dashboard_bp.route("/api/admin/churn-monitoring")
@login_required
def admin_churn_monitoring():
    """Admin endpoint to monitor users at risk of churning"""
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    # Get all active users
    users = User.query.filter_by(is_active=True).all()

    at_risk_users = []

    for user in users:
        churn_analysis = check_churn_risk(user)

        if churn_analysis["risk_level"] in ["medium", "high"]:
            at_risk_users.append(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "tier": user.tier.name,
                    "risk_level": churn_analysis["risk_level"],
                    "risk_score": churn_analysis["risk_score"],
                    "factors": churn_analysis["factors"],
                    "recommendation": churn_analysis["recommendation"],
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                }
            )

    # Sort by risk score (highest first)
    at_risk_users.sort(key=lambda x: x["risk_score"], reverse=True)

    return jsonify(
        {
            "total_users": len(users),
            "at_risk_count": len(at_risk_users),
            "at_risk_users": at_risk_users,
        }
    )
