"""
Multi-Tenant Isolation Guard
==============================
Decorators and query filters that enforce organization-level data isolation.

Design principles:
  - Every case belongs to an organization (via organization_id FK).
  - Authenticated users can only access cases within their organization.
  - Admin users bypass tenant isolation (for platform-level oversight).
  - Tenant boundaries are enforced at the query layer, not the UI layer.
  - Violations are logged and rejected with 403.

Usage:
    @app.route('/cases/<int:case_id>')
    @login_required
    @tenant_case_access
    def view_case(case_id):
        ...  # case is guaranteed to belong to current_user's org
"""

import logging
from functools import wraps
from typing import Optional

from flask import abort, g, request
from flask_login import current_user

logger = logging.getLogger(__name__)


def _get_user_org_id() -> Optional[int]:
    """
    Retrieve the organization_id of the current user.

    Returns None if:
      - The user has no organization_id attribute.
      - The user is a platform admin (admins bypass tenant isolation).
    """
    if not current_user.is_authenticated:
        return None

    # Admins see all tenants
    from auth.models import UserRole
    if getattr(current_user, "role", None) == UserRole.ADMIN:
        return None  # Signals "no filter"

    return getattr(current_user, "organization_id", None)


def tenant_case_access(f):
    """
    Decorator: reject access to cases outside the user's organization.

    Expects the decorated function to accept a `case_id` kwarg.
    Loads the case, checks organization_id, and passes the case via `g.case`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        case_id = kwargs.get("case_id")
        if case_id is None:
            abort(400)

        from models.legal_case import LegalCase
        from auth.models import db
        case = db.session.get(LegalCase, case_id)
        if case is None:
            abort(404)

        org_id = _get_user_org_id()
        if org_id is not None:
            # Non-admin user: enforce tenant boundary
            if case.organization_id is not None and case.organization_id != org_id:
                logger.warning(
                    "Tenant isolation violation: user=%s org=%s attempted case=%d (org=%s)",
                    current_user.id,
                    org_id,
                    case_id,
                    case.organization_id,
                )
                abort(403)

        g.case = case
        return f(*args, **kwargs)
    return decorated


def tenant_filter_cases(query):
    """
    Apply tenant filter to a SQLAlchemy query on LegalCase.

    Admin users receive the query unmodified.
    Non-admin users receive only their organization's cases.

    Usage:
        q = LegalCase.query
        q = tenant_filter_cases(q)
        cases = q.all()
    """
    org_id = _get_user_org_id()
    if org_id is None:
        return query  # Admin or no org filter

    from models.legal_case import LegalCase
    return query.filter(
        (LegalCase.organization_id == org_id) | (LegalCase.organization_id.is_(None))
    )
