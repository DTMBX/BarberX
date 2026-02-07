# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Authentication API Endpoints
Handles login, logout, registration, and JWT token management
"""

from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, jsonify, request

from api import auth_api
from models_auth import TierLevel, User, db


def generate_jwt_token(user_id, expires_in=86400):
    """
    Generate JWT token for user

    Args:
        user_id: User ID
        expires_in: Token expiration in seconds (default 24 hours)

    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    return token


def verify_jwt_token(token):
    """
    Verify JWT token and return user_id

    Args:
        token: JWT token string

    Returns:
        user_id if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    """
    Decorator to require JWT authentication
    Checks for Bearer token in Authorization header
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401

        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401

        user_id = verify_jwt_token(token)

        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Attach user to request context
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


@auth_api.route("/login", methods=["POST"])
def api_login():
    """
    Login endpoint - returns JWT token

    POST /api/v1/auth/login
    Body: {"email": "user@example.com", "password": "password123"}
    Returns: {"token": "jwt_token", "user": {...}, "expires_in": 86400}
    """
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    email = data["email"].lower().strip()
    password = data["password"]

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Check if account is active
    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate JWT token (24 hour expiry)
    token = generate_jwt_token(user.id, expires_in=86400)

    return (
        jsonify(
            {
                "token": token,
                "expires_in": 86400,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name or user.email,
                    "tier": user.tier.name,
                    "tier_display": user.tier_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                },
            }
        ),
        200,
    )


@auth_api.route("/register", methods=["POST"])
def api_register():
    """
    Register new user

    POST /api/v1/auth/register
    Body: {"email": "user@example.com", "password": "password123", "name": "John Doe"}
    Returns: {"token": "jwt_token", "user": {...}}
    """
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    email = data["email"].lower().strip()
    password = data["password"]
    name = data.get("name", "")

    # Validate email format
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    # Create new user
    user = User(
        email=email,
        full_name=name,
        tier=TierLevel.FREE,
        is_active=True,
        is_verified=False,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate JWT token
    token = generate_jwt_token(user.id)

    return (
        jsonify(
            {
                "token": token,
                "expires_in": 86400,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name or user.email,
                    "tier": user.tier.name,
                    "tier_display": user.tier_name,
                    "created_at": user.created_at.isoformat(),
                },
            }
        ),
        201,
    )


@auth_api.route("/refresh", methods=["POST"])
@jwt_required
def api_refresh_token():
    """
    Refresh JWT token

    POST /api/v1/auth/refresh
    Headers: Authorization: Bearer <token>
    Returns: {"token": "new_jwt_token", "expires_in": 86400}
    """
    user = request.current_user

    # Generate new token
    token = generate_jwt_token(user.id)

    return (
        jsonify(
            {
                "token": token,
                "expires_in": 86400,
            }
        ),
        200,
    )


@auth_api.route("/me", methods=["GET"])
@jwt_required
def api_get_current_user():
    """
    Get current authenticated user

    GET /api/v1/auth/me
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
                    "name": user.full_name or user.email,
                    "tier": user.tier.name,
                    "tier_display": user.tier_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                }
            }
        ),
        200,
    )


@auth_api.route("/logout", methods=["POST"])
@jwt_required
def api_logout():
    """
    Logout (client should discard token)

    POST /api/v1/auth/logout
    Headers: Authorization: Bearer <token>
    Returns: {"message": "Logged out successfully"}
    """
    # JWT is stateless, so we just return success
    # Client should delete the token
    return jsonify({"message": "Logged out successfully"}), 200
