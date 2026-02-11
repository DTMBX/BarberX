"""
API Token Authentication Middleware
=====================================
Provides Bearer-token authentication for programmatic API access.

Design principles:
  - Tokens are validated per-request; no session state.
  - Every authenticated request is audit-logged (action, token name, IP).
  - Expired or inactive tokens produce 401.
  - Usage is tracked per token for rate-limit and billing purposes.
  - The decorator can be stacked with Flask-Login's @login_required —
    api_token_required takes precedence when a Bearer header is present.
"""

import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, Tuple

from flask import abort, g, jsonify, request

logger = logging.getLogger(__name__)


def _extract_bearer_token() -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def _resolve_token(raw_token: str) -> Optional[Tuple]:
    """
    Look up and validate an API token.

    Returns (ApiToken, User) if valid, None otherwise.
    """
    from auth.models import ApiToken, db

    token_obj = ApiToken.query.filter_by(token=raw_token).first()
    if token_obj is None:
        return None

    if not token_obj.is_valid():
        return None

    # Load owning user
    user = token_obj.user
    if user is None or not user.is_active:
        return None

    return token_obj, user


def api_token_required(f):
    """
    Decorator: require a valid Bearer token.

    On success, sets:
      - g.api_token  → ApiToken instance
      - g.api_user   → User instance (token owner)

    Usage tracking and audit logging are performed automatically.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        raw_token = _extract_bearer_token()
        if raw_token is None:
            return jsonify({"error": "Missing Authorization header with Bearer token"}), 401

        result = _resolve_token(raw_token)
        if result is None:
            return jsonify({"error": "Invalid or expired API token"}), 401

        token_obj, user = result

        # Record usage
        token_obj.last_used_at = datetime.now(timezone.utc)
        from auth.models import db
        db.session.commit()

        # Store in g for downstream access
        g.api_token = token_obj
        g.api_user = user

        logger.info(
            "API auth: token=%s user=%s endpoint=%s",
            token_obj.name,
            user.email,
            request.endpoint,
        )

        return f(*args, **kwargs)

    return decorated


def api_admin_required(f):
    """
    Decorator: require a valid Bearer token belonging to an admin user.
    Must be used after @api_token_required (or stacked — this calls it).
    """

    @wraps(f)
    @api_token_required
    def decorated(*args, **kwargs):
        if not g.api_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated
