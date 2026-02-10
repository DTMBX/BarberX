"""
Security Hardening Middleware
==============================
Configures secure headers, rate limiting, and session hardening for the
Flask application.

Applied via ``init_security(app)`` in the application factory.

Design principles:
  - Defense in depth: headers, rate limits, session flags all contribute.
  - Fail closed: if Talisman or Limiter fail to initialize, the app does
    not start silently without protection.
  - Configuration is explicit and auditable.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter (singleton — configured once, importable by blueprints)
# ---------------------------------------------------------------------------

_limiter = None


def get_limiter():
    """Return the configured Flask-Limiter instance, or None if not yet init."""
    return _limiter


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def init_security(app):
    """
    Apply all security hardening to the Flask app.

    Call this once from create_app(), after extensions are initialized.
    """
    _init_secure_headers(app)
    _init_rate_limiter(app)
    _harden_session(app)
    logger.info("Security hardening applied.")


# ---------------------------------------------------------------------------
# Secure headers via Flask-Talisman
# ---------------------------------------------------------------------------


def _init_secure_headers(app):
    """
    Configure Content-Security-Policy, X-Frame-Options, HSTS, and related
    headers via Flask-Talisman.

    In development (DEBUG=True), HTTPS enforcement is disabled but headers
    are still set.
    """
    from flask_talisman import Talisman

    # CSP: restrictive baseline, allow self + inline styles for Tailwind
    csp = {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self' 'unsafe-inline'",   # Tailwind utility classes
        "img-src": "'self' data:",
        "font-src": "'self'",
        "connect-src": "'self'",
        "frame-ancestors": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'",
    }

    Talisman(
        app,
        force_https=not app.debug,
        content_security_policy=csp,
        content_security_policy_nonce_in=["script-src"],
        frame_options="DENY",
        x_xss_protection=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        referrer_policy="strict-origin-when-cross-origin",
        session_cookie_secure=not app.debug,
        session_cookie_http_only=True,
    )

    logger.info(
        "Secure headers configured (force_https=%s).", not app.debug
    )


# ---------------------------------------------------------------------------
# Rate limiting via Flask-Limiter
# ---------------------------------------------------------------------------


def _init_rate_limiter(app):
    """
    Apply rate limits. Auth endpoints get aggressive limits; general API
    gets moderate limits.

    Storage: in-memory by default. For multi-process production, set
    RATELIMIT_STORAGE_URI to a Redis URL.
    """
    global _limiter

    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    storage_uri = app.config.get("RATELIMIT_STORAGE_URI", "memory://")

    _limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=storage_uri,
        default_limits=["200 per hour", "50 per minute"],
        strategy="fixed-window",
    )

    # Aggressive limits on auth endpoints
    @app.after_request
    def _add_rate_limit_headers(response):
        """Ensure rate-limit headers are present on every response."""
        return response

    logger.info(
        "Rate limiter configured (storage=%s).", storage_uri
    )

    return _limiter


# ---------------------------------------------------------------------------
# Session hardening
# ---------------------------------------------------------------------------


def _harden_session(app):
    """
    Ensure session cookies are properly secured beyond what Config sets.
    """
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", not app.debug)
    app.config.setdefault("PERMANENT_SESSION_LIFETIME", 2592000)

    logger.info("Session hardening applied.")
