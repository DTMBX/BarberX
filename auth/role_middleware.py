"""
Centralized Role Enforcement Middleware
========================================
All role-based access control decisions are made here. No route should
perform ad-hoc role checks — use these decorators exclusively.

Role hierarchy (descending privilege):
    ADMIN > MODERATOR > PRO_USER > USER

Each decorator enforces server-side. Client-side role gating is cosmetic
only and must never be relied upon.

Design principles:
  - Fail closed: missing role → deny.
  - All denials are auditable.
  - No silent fallback.
"""

from functools import wraps
from typing import Sequence

from flask import abort, jsonify, request
from flask_login import current_user

from auth.models import UserRole


# ---------------------------------------------------------------------------
# Role hierarchy — higher index = more privilege
# ---------------------------------------------------------------------------

_ROLE_RANK = {
    UserRole.USER: 0,
    UserRole.PRO_USER: 1,
    UserRole.MODERATOR: 2,
    UserRole.ADMIN: 3,
}


def _user_rank() -> int:
    """Return the numeric rank of the current user's role."""
    if not current_user.is_authenticated:
        return -1
    return _ROLE_RANK.get(current_user.role, -1)


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------


def require_role(minimum_role: UserRole):
    """
    Decorator: require caller's role to be at least *minimum_role*.

    Usage:
        @app.route('/admin/dashboard')
        @login_required
        @require_role(UserRole.ADMIN)
        def admin_dashboard():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                if _is_api_request():
                    return jsonify({"error": "Authentication required"}), 401
                abort(401)

            required_rank = _ROLE_RANK.get(minimum_role, 999)
            if _user_rank() < required_rank:
                if _is_api_request():
                    return jsonify({
                        "error": "Insufficient permissions",
                        "required_role": minimum_role.value,
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated
    return decorator


def require_any_role(roles: Sequence[UserRole]):
    """
    Decorator: require caller to hold ANY of the listed roles.

    Usage:
        @require_any_role([UserRole.ADMIN, UserRole.MODERATOR])
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                if _is_api_request():
                    return jsonify({"error": "Authentication required"}), 401
                abort(401)

            if current_user.role not in roles:
                if _is_api_request():
                    return jsonify({
                        "error": "Insufficient permissions",
                        "allowed_roles": [r.value for r in roles],
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------------------------------------------------------------------------
# Role matrix — documents which roles can access which domains
# ---------------------------------------------------------------------------

ROLE_MATRIX = {
    "auth.login": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "auth.register": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "auth.profile": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "auth.admin": [UserRole.ADMIN],
    "cases.list": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "cases.create": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "cases.delete": [UserRole.ADMIN],
    "evidence.view": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "evidence.upload": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "evidence.download": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "evidence.delete": [UserRole.ADMIN],
    "jobs.view": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "jobs.start": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "jobs.cancel": [UserRole.MODERATOR, UserRole.ADMIN],
    "search.basic": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "search.advanced": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "export.create": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "export.verify": [UserRole.USER, UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "export.download": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "assistant.action": [UserRole.PRO_USER, UserRole.MODERATOR, UserRole.ADMIN],
    "admin.users": [UserRole.ADMIN],
    "admin.audit_log": [UserRole.ADMIN],
    "admin.system": [UserRole.ADMIN],
}


def check_permission(action: str) -> bool:
    """
    Check whether the current user is permitted to perform *action*.

    Returns True if allowed, False otherwise.
    Does NOT abort — caller decides how to handle denial.
    """
    allowed_roles = ROLE_MATRIX.get(action)
    if allowed_roles is None:
        # Undocumented action → deny by default (fail closed)
        return False
    if not current_user.is_authenticated:
        return False
    return current_user.role in allowed_roles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_api_request() -> bool:
    """Determine whether the current request expects JSON."""
    return (
        request.path.startswith("/api/")
        or request.path.startswith("/assistant/")
        or request.accept_mimetypes.best == "application/json"
        or request.content_type == "application/json"
    )
