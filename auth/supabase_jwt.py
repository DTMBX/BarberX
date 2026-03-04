"""
Supabase JWT Validation
=========================
Validates Supabase-issued JWTs using JWKS (JSON Web Key Set).

SECURITY PRINCIPLES:
  - Fail closed: any validation error returns 401, never silent pass.
  - JWKS is cached with TTL to avoid per-request network calls.
  - Token expiration is strictly enforced.
  - Audience must match "authenticated" (Supabase default).
  - Issuer must match the configured Supabase URL.

Environment variables:
  SUPABASE_URL       — Supabase project URL (e.g., https://xxx.supabase.co)
  SUPABASE_JWT_AUD   — Expected audience (default: "authenticated")

Usage with FastAPI:
    from auth.supabase_jwt import get_supabase_user_id, validate_supabase_token
    
    @app.get("/api/v1/protected")
    async def protected_route(user_id: str = Depends(get_supabase_user_id)):
        ...

Usage with Flask:
    from auth.supabase_jwt import supabase_token_required
    
    @app.route("/api/v1/protected")
    @supabase_token_required
    def protected_route():
        user_id = g.supabase_user_id
        ...
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Optional

import httpx
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWKError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_JWT_AUD = os.environ.get("SUPABASE_JWT_AUD", "authenticated")

# Cache settings
_JWKS_CACHE_TTL = timedelta(hours=1)
_jwks_cache: Optional[dict] = None
_jwks_fetched_at: Optional[datetime] = None


def _get_jwks_url() -> str:
    """Build JWKS URL from Supabase URL."""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable not set")
    base = SUPABASE_URL.rstrip("/")
    return f"{base}/auth/v1/.well-known/jwks.json"


# ---------------------------------------------------------------------------
# JWKS Fetching (with cache)
# ---------------------------------------------------------------------------


async def _fetch_jwks_async() -> dict:
    """Fetch JWKS from Supabase (async)."""
    global _jwks_cache, _jwks_fetched_at
    
    now = datetime.now(timezone.utc)
    if _jwks_cache and _jwks_fetched_at:
        if (now - _jwks_fetched_at) < _JWKS_CACHE_TTL:
            return _jwks_cache
    
    url = _get_jwks_url()
    logger.debug(f"Fetching JWKS from {url}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_fetched_at = now
        logger.info("JWKS refreshed successfully")
        return _jwks_cache


def _fetch_jwks_sync() -> dict:
    """Fetch JWKS from Supabase (sync for Flask)."""
    global _jwks_cache, _jwks_fetched_at
    
    now = datetime.now(timezone.utc)
    if _jwks_cache and _jwks_fetched_at:
        if (now - _jwks_fetched_at) < _JWKS_CACHE_TTL:
            return _jwks_cache
    
    url = _get_jwks_url()
    logger.debug(f"Fetching JWKS from {url}")
    
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_fetched_at = now
        logger.info("JWKS refreshed successfully")
        return _jwks_cache


# ---------------------------------------------------------------------------
# Token Validation
# ---------------------------------------------------------------------------


def _validate_token(token: str, jwks: dict) -> dict:
    """
    Validate a JWT against JWKS.
    
    Returns the decoded payload if valid.
    Raises JWTError or ValueError if invalid.
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL not configured")
    
    # Expected issuer is the Supabase auth URL
    expected_issuer = f"{SUPABASE_URL.rstrip('/')}/auth/v1"
    
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=SUPABASE_JWT_AUD,
            issuer=expected_issuer,
            options={
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
            }
        )
        return payload
    except ExpiredSignatureError:
        logger.warning("Token expired")
        raise ValueError("Token expired")
    except JWKError as e:
        logger.warning(f"JWK error: {e}")
        raise ValueError(f"Invalid token key: {e}")
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise ValueError(f"Invalid token: {e}")


async def validate_supabase_token_async(token: str) -> dict:
    """
    Validate a Supabase JWT (async).
    
    Returns decoded payload with:
      - sub: Supabase user UUID
      - email: User email
      - role: Supabase role (usually "authenticated")
      - user_metadata: Custom user metadata
      - app_metadata: App-level metadata
    
    Raises ValueError on any validation failure.
    """
    jwks = await _fetch_jwks_async()
    return _validate_token(token, jwks)


def validate_supabase_token_sync(token: str) -> dict:
    """
    Validate a Supabase JWT (sync for Flask).
    
    Same behavior as validate_supabase_token_async.
    """
    jwks = _fetch_jwks_sync()
    return _validate_token(token, jwks)


# ---------------------------------------------------------------------------
# FastAPI Dependency
# ---------------------------------------------------------------------------


async def get_supabase_user_id(authorization: str = None) -> str:
    """
    FastAPI dependency: extract and validate Supabase user ID from JWT.
    
    Usage:
        @app.get("/api/v1/me")
        async def get_me(user_id: str = Depends(get_supabase_user_id)):
            ...
    
    Raises HTTPException(401) if validation fails.
    """
    from fastapi import HTTPException, Header
    
    # Re-import Header to get the actual value
    # This function should be used with Depends, passing the header
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Empty token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = await validate_supabase_token_async(token)
        return payload.get("sub", "")
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Unexpected error validating token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


def supabase_token_dependency():
    """
    Factory for FastAPI dependency with proper Header injection.
    
    Usage:
        from fastapi import Depends, Header
        
        @app.get("/api/v1/me")
        async def get_me(
            user_id: str = Depends(supabase_user_id_dependency())
        ):
            ...
    """
    from fastapi import Depends, Header
    
    async def dependency(
        authorization: str = Header(..., alias="Authorization")
    ) -> str:
        return await get_supabase_user_id(authorization)
    
    return dependency


# ---------------------------------------------------------------------------
# Flask Decorator
# ---------------------------------------------------------------------------


def supabase_token_required(f):
    """
    Flask decorator: require valid Supabase JWT.
    
    On success, sets:
      - g.supabase_user_id  → Supabase user UUID (sub claim)
      - g.supabase_email    → User email
      - g.supabase_payload  → Full decoded payload
    
    Returns 401 JSON response on failure (fail closed).
    
    Usage:
        @app.route("/api/v1/me")
        @supabase_token_required
        def get_me():
            user_id = g.supabase_user_id
            ...
    """
    from flask import abort, g, jsonify, request
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Missing or invalid Authorization header",
                "code": "INVALID_AUTH_HEADER"
            }), 401
        
        token = auth_header[7:].strip()
        if not token:
            return jsonify({
                "error": "Empty token",
                "code": "EMPTY_TOKEN"
            }), 401
        
        try:
            payload = validate_supabase_token_sync(token)
        except ValueError as e:
            return jsonify({
                "error": str(e),
                "code": "INVALID_TOKEN"
            }), 401
        except Exception as e:
            logger.error(f"Unexpected error validating Supabase token: {e}")
            return jsonify({
                "error": "Token validation failed",
                "code": "VALIDATION_ERROR"
            }), 401
        
        # Set request context
        g.supabase_user_id = payload.get("sub", "")
        g.supabase_email = payload.get("email", "")
        g.supabase_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated


# ---------------------------------------------------------------------------
# User Resolution (maps Supabase UUID → Evident User)
# ---------------------------------------------------------------------------


class UserNotProvisionedError(Exception):
    """Raised when Supabase user is not provisioned in Evident."""
    pass


def get_user_by_supabase_id(supabase_user_id: str) -> Any:
    """
    Look up an Evident user by Supabase UUID.
    
    SECURITY: Does NOT auto-provision users. If a user authenticates via
    Supabase but has no Evident account, this raises UserNotProvisionedError.
    Users must be provisioned through an explicit admin workflow.
    
    Returns:
        User model instance if found.
    
    Raises:
        UserNotProvisionedError: If user not found in Evident database.
    """
    from auth.models import User
    
    user = User.query.filter_by(supabase_user_id=supabase_user_id).first()
    
    if not user:
        logger.warning(
            f"Supabase user {supabase_user_id} not provisioned in Evident. "
            "Access denied. Admin must provision user explicitly."
        )
        raise UserNotProvisionedError(
            f"User {supabase_user_id} is not provisioned in Evident"
        )
    
    if not user.is_active:
        logger.warning(f"User {supabase_user_id} is deactivated")
        raise UserNotProvisionedError("User account is deactivated")
    
    return user


# ---------------------------------------------------------------------------
# Combined Decorator (resolves Supabase user to Evident user)
# ---------------------------------------------------------------------------


def supabase_auth_required(f):
    """
    Flask decorator: require valid Supabase JWT and resolve to Evident user.
    
    Combines supabase_token_required with user resolution.
    
    SECURITY: Returns 403 Forbidden if Supabase user is not provisioned in
    Evident. Users are NOT auto-provisioned. Admin must explicitly create
    user records via proper provisioning workflow.
    
    On success, sets:
      - g.supabase_user_id  → Supabase user UUID
      - g.supabase_email    → User email
      - g.supabase_payload  → Full decoded payload
      - g.current_user      → Evident User model instance
    
    Returns:
      - 401 if JWT is invalid or missing
      - 403 if user not provisioned in Evident
    
    Usage:
        @app.route("/api/v1/me")
        @supabase_auth_required
        def get_me():
            user = g.current_user
            ...
    """
    from flask import g, jsonify
    
    @wraps(f)
    @supabase_token_required
    def decorated(*args, **kwargs):
        # Resolve Supabase user to Evident user (NO AUTO-PROVISIONING)
        try:
            user = get_user_by_supabase_id(g.supabase_user_id)
        except UserNotProvisionedError as e:
            return jsonify({
                "error": "User not provisioned",
                "detail": str(e),
                "code": "USER_NOT_PROVISIONED"
            }), 403
        
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------


def check_jwks_availability() -> dict:
    """
    Check if JWKS endpoint is reachable.
    
    Returns dict with status info for health checks.
    """
    if not SUPABASE_URL:
        return {
            "status": "unconfigured",
            "error": "SUPABASE_URL not set"
        }
    
    try:
        jwks = _fetch_jwks_sync()
        key_count = len(jwks.get("keys", []))
        return {
            "status": "healthy",
            "keys": key_count,
            "cache_age_seconds": (
                (datetime.now(timezone.utc) - _jwks_fetched_at).total_seconds()
                if _jwks_fetched_at else 0
            )
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
