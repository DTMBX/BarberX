# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Admin API Endpoints
Handles administrative functions (user management, system stats)
Requires admin role
"""

from functools import wraps

from flask import jsonify, request
from models_auth import User

from api import admin_api
from api.auth import jwt_required


def admin_required(f):
    """Decorator to require admin role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = request.current_user
        if user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


@admin_api.route("/users", methods=["GET"])
@jwt_required
@admin_required
def list_users():
    """
    List all users

    GET /api/v1/admin/users?page=1&limit=50
    Headers: Authorization: Bearer <token>
    Returns: {"users": [...], "total": 100}
    """
    page = int(request.args.get("page", 1))
    limit = min(int(request.args.get("limit", 50)), 100)

    # TODO: Query database with pagination
    return jsonify({"users": [], "total": 0, "page": page, "limit": limit}), 200


@admin_api.route("/users/<int:user_id>", methods=["GET"])
@jwt_required
@admin_required
def get_user(user_id):
    """
    Get user details

    GET /api/v1/admin/users/<user_id>
    Headers: Authorization: Bearer <token>
    Returns: {"user": {...}}
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

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
                }
            }
        ),
        200,
    )


@admin_api.route("/stats", methods=["GET"])
@jwt_required
@admin_required
def get_system_stats():
    """
    Get system statistics

    GET /api/v1/admin/stats
    Headers: Authorization: Bearer <token>
    Returns: {"users": 100, "uploads": 500, "analyses": 250}
    """
    # TODO: Calculate real stats
    return (
        jsonify(
            {
                "users": {
                    "total": 0,
                    "active": 0,
                    "by_tier": {"FREE": 0, "PRO": 0, "PREMIUM": 0, "ENTERPRISE": 0},
                },
                "uploads": {"total": 0, "today": 0},
                "analyses": {"total": 0, "in_progress": 0},
            }
        ),
        200,
    )
