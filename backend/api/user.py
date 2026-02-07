# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
User API Endpoints
Handles user profile management, preferences, and subscription info
"""

from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from api import user_api
from api.auth import jwt_required
from models_auth import db


@user_api.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    """
    Get current user profile

    GET /api/v1/user/profile
    Headers: Authorization: Bearer <token>
    Returns: {"user": {...}}
    """
    user = request.current_user

    return (
        jsonify(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "tier": user.tier,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                }
            }
        ),
        200,
    )


@user_api.route("/profile", methods=["PUT"])
@jwt_required
def update_profile():
    """
    Update user profile

    PUT /api/v1/user/profile
    Headers: Authorization: Bearer <token>
    Body: {"name": "John Doe"}
    Returns: {"user": {...}}
    """
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update allowed fields
    if "name" in data:
        user.name = data["name"]

    db.session.commit()

    return (
        jsonify(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "tier": user.tier,
                }
            }
        ),
        200,
    )


@user_api.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    """
    Change user password

    POST /api/v1/user/change-password
    Headers: Authorization: Bearer <token>
    Body: {"current_password": "old123", "new_password": "new123"}
    Returns: {"message": "Password updated"}
    """
    user = request.current_user
    data = request.get_json()

    if not data or not data.get("current_password") or not data.get("new_password"):
        return jsonify({"error": "Current and new password required"}), 400

    # Verify current password
    if not check_password_hash(user.password_hash, data["current_password"]):
        return jsonify({"error": "Current password is incorrect"}), 401

    # Update password
    user.password_hash = generate_password_hash(data["new_password"])
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200


@user_api.route("/subscription", methods=["GET"])
@jwt_required
def get_subscription():
    """
    Get user subscription information

    GET /api/v1/user/subscription
    Headers: Authorization: Bearer <token>
    Returns: {"tier": "PRO", "plan_details": {...}}
    """
    user = request.current_user

    # TODO: Fetch Stripe subscription details
    return (
        jsonify(
            {
                "tier": user.tier,
                "plan_details": {
                    "name": user.tier,
                    "billing_period": "monthly",
                    "next_billing_date": None,
                    "amount": 0 if user.tier == "FREE" else 49.99,
                },
            }
        ),
        200,
    )


@user_api.route("/usage", methods=["GET"])
@jwt_required
def get_usage_stats():
    """
    Get usage statistics for current billing period

    GET /api/v1/user/usage
    Headers: Authorization: Bearer <token>
    Returns: {"uploads": 5, "analyses": 3, "storage_mb": 125}
    """
    user = request.current_user

    # TODO: Calculate actual usage from database
    return (
        jsonify(
            {
                "uploads": {"count": 0, "limit": 10 if user.tier == "FREE" else -1},
                "analyses": {"count": 0, "limit": 5 if user.tier == "FREE" else -1},
                "storage_mb": {"used": 0, "limit": 100 if user.tier == "FREE" else -1},
            }
        ),
        200,
    )
