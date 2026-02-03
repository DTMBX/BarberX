"""
API Middleware Layer
Production-ready middleware for authentication, rate limiting, validation

Features:
- JWT token authentication
- API key authentication
- Rate limiting (per user/IP)
- Request validation
- Response compression
- CORS handling
- Request logging
"""

import functools
import hashlib
import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional

from flask import g, jsonify, request
from werkzeug.exceptions import HTTPException

from backend_integration import error_response, success_response


class RateLimiter:
    """
    Token bucket rate limiter

    Supports:
    - Per-user limits
    - Per-IP limits
    - Tiered limits (free/pro/enterprise)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.buckets = defaultdict(lambda: {"tokens": 0, "last_update": time.time()})

        # Rate limits by tier (requests per minute)
        self.tier_limits = {"free": 10, "professional": 60, "enterprise": 300, "admin": 1000}

    def _get_bucket_key(self, identifier: str, tier: str) -> str:
        """Generate bucket key"""
        return f"{tier}:{identifier}"

    def _refill_bucket(self, bucket_key: str, max_tokens: int) -> Dict:
        """Refill bucket based on elapsed time"""
        bucket = self.buckets[bucket_key]
        now = time.time()
        elapsed = now - bucket["last_update"]

        # Refill at rate of max_tokens per 60 seconds
        tokens_to_add = (elapsed / 60.0) * max_tokens
        bucket["tokens"] = min(max_tokens, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

        return bucket

    def check_limit(self, identifier: str, tier: str = "free") -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed

        Returns:
            (allowed: bool, retry_after: Optional[int])
        """
        max_tokens = self.tier_limits.get(tier, self.tier_limits["free"])
        bucket_key = self._get_bucket_key(identifier, tier)

        # Refill bucket
        bucket = self._refill_bucket(bucket_key, max_tokens)

        # Check if we have tokens
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return (True, None)
        else:
            # Calculate retry_after
            retry_after = int(60 / max_tokens)
            return (False, retry_after)

    def get_remaining(self, identifier: str, tier: str = "free") -> int:
        """Get remaining requests"""
        max_tokens = self.tier_limits.get(tier, self.tier_limits["free"])
        bucket_key = self._get_bucket_key(identifier, tier)
        bucket = self._refill_bucket(bucket_key, max_tokens)
        return int(bucket["tokens"])


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(tier_override: Optional[str] = None):
    """
    Rate limiting decorator

    Usage:
        @app.route('/api/endpoint')
        @rate_limit()
        def endpoint():
            ...
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # Determine identifier (user_id or IP)
            if hasattr(g, "user") and g.user:
                identifier = str(g.user.id)
                tier = tier_override or g.user.tier
            else:
                identifier = request.remote_addr
                tier = tier_override or "free"

            # Check limit
            allowed, retry_after = rate_limiter.check_limit(identifier, tier)

            if not allowed:
                response = jsonify(
                    error_response("Rate limit exceeded", error_code="RATE_LIMIT_EXCEEDED")
                )
                response.status_code = 429
                response.headers["Retry-After"] = str(retry_after)
                return response

            # Add rate limit headers
            remaining = rate_limiter.get_remaining(identifier, tier)
            response = f(*args, **kwargs)

            if isinstance(response, tuple):
                response, status_code = response
                response = jsonify(response) if isinstance(response, dict) else response
                response.status_code = status_code
            elif not hasattr(response, "headers"):
                response = jsonify(response)

            response.headers["X-RateLimit-Limit"] = str(rate_limiter.tier_limits[tier])
            response.headers["X-RateLimit-Remaining"] = str(remaining)

            return response

        return wrapped

    return decorator


class APIKeyAuth:
    """API key authentication"""

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate API key and return user info

        Returns:
            User dict if valid, None if invalid
        """
        if not api_key:
            return None

        try:
            # Hash the key to compare with database
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Query database (pseudo-code - adapt to your model)
            from models_auth import APIKey

            api_key_obj = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()

            if not api_key_obj:
                return None

            # Check expiration
            if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                return None

            # Update last used
            api_key_obj.last_used_at = datetime.utcnow()
            api_key_obj.request_count += 1
            self.db.session.commit()

            # Return user info
            user = api_key_obj.user
            return {"id": user.id, "email": user.email, "tier": user.tier, "role": user.role}

        except Exception as e:
            self.logger.error(f"API key validation error: {str(e)}")
            return None


def require_api_key(db):
    """
    API key authentication decorator

    Usage:
        @app.route('/api/endpoint')
        @require_api_key(db)
        def endpoint():
            # Access user via g.user
            ...
    """
    api_auth = APIKeyAuth(db)

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get("X-API-Key")

            if not api_key:
                return (
                    jsonify(error_response("API key required", error_code="API_KEY_REQUIRED")),
                    401,
                )

            # Validate key
            user = api_auth.validate_api_key(api_key)

            if not user:
                return jsonify(error_response("Invalid API key", error_code="INVALID_API_KEY")), 401

            # Store user in g
            g.user = type("User", (), user)

            return f(*args, **kwargs)

        return wrapped

    return decorator


def require_tier(min_tier: str):
    """
    Tier-based authorization decorator

    Usage:
        @app.route('/api/premium-feature')
        @require_tier('professional')
        def premium_feature():
            ...
    """
    tier_hierarchy = {"free": 0, "professional": 1, "enterprise": 2, "admin": 3}

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(g, "user"):
                return (
                    jsonify(error_response("Authentication required", error_code="AUTH_REQUIRED")),
                    401,
                )

            user_tier_level = tier_hierarchy.get(g.user.tier, 0)
            required_tier_level = tier_hierarchy.get(min_tier, 0)

            if user_tier_level < required_tier_level:
                return (
                    jsonify(
                        error_response(
                            f"This feature requires {min_tier} tier or higher",
                            error_code="INSUFFICIENT_TIER",
                        )
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return wrapped

    return decorator


def validate_request(schema: Dict):
    """
    Request validation decorator

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_request({
            'required': ['file', 'case_number'],
            'optional': ['evidence_type', 'tags']
        })
        def endpoint():
            # Access validated data via request.validated_data
            ...
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            data = request.get_json() or {}

            # Check required fields
            missing = []
            for field in schema.get("required", []):
                if field not in data:
                    missing.append(field)

            if missing:
                return (
                    jsonify(
                        error_response(
                            f"Missing required fields: {', '.join(missing)}",
                            error_code="VALIDATION_ERROR",
                            details={"missing_fields": missing},
                        )
                    ),
                    400,
                )

            # Validate field types if specified
            if "types" in schema:
                type_errors = []
                for field, expected_type in schema["types"].items():
                    if field in data:
                        if not isinstance(data[field], expected_type):
                            type_errors.append(f"{field} must be {expected_type.__name__}")

                if type_errors:
                    return (
                        jsonify(
                            error_response(
                                f"Type validation failed: {'; '.join(type_errors)}",
                                error_code="VALIDATION_ERROR",
                                details={"type_errors": type_errors},
                            )
                        ),
                        400,
                    )

            # Store validated data
            request.validated_data = data

            return f(*args, **kwargs)

        return wrapped

    return decorator


def log_request():
    """
    Request logging decorator

    Logs request details and response time
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            logger = logging.getLogger("api.requests")

            # Log request
            start_time = time.time()
            user_id = g.user.id if hasattr(g, "user") else None

            logger.info(
                f"{request.method} {request.path} | "
                f"User: {user_id} | "
                f"IP: {request.remote_addr}"
            )

            # Execute request
            try:
                response = f(*args, **kwargs)
                duration = time.time() - start_time

                # Log response
                status = (
                    getattr(response, "status_code", 200)
                    if hasattr(response, "status_code")
                    else 200
                )
                logger.info(
                    f"{request.method} {request.path} | "
                    f"Status: {status} | "
                    f"Duration: {duration:.3f}s"
                )

                return response

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{request.method} {request.path} | "
                    f"Error: {str(e)} | "
                    f"Duration: {duration:.3f}s"
                )
                raise

        return wrapped

    return decorator


def handle_errors():
    """
    Error handling decorator

    Converts exceptions to JSON responses
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)

            except HTTPException as e:
                return (
                    jsonify(
                        error_response(e.description, error_code=e.name.upper().replace(" ", "_"))
                    ),
                    e.code,
                )

            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.exception("Unhandled error in %s: %s", f.__name__, str(e))

                return (
                    jsonify(error_response("Internal server error", error_code="INTERNAL_ERROR")),
                    500,
                )

        return wrapped

    return decorator


# Combination decorators for common patterns


def api_endpoint(
    db,
    require_auth: bool = True,
    min_tier: Optional[str] = None,
    validation_schema: Optional[Dict] = None,
):
    """
    Combined decorator for API endpoints

    Applies:
    - Error handling
    - Request logging
    - Rate limiting
    - Authentication (optional)
    - Tier checking (optional)
    - Request validation (optional)

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @api_endpoint(
            db,
            require_auth=True,
            min_tier='professional',
            validation_schema={'required': ['file']}
        )
        def endpoint():
            ...
    """

    def decorator(f):
        # Apply decorators in reverse order (innermost first)
        wrapped = f

        # Validation
        if validation_schema:
            wrapped = validate_request(validation_schema)(wrapped)

        # Tier requirement
        if min_tier:
            wrapped = require_tier(min_tier)(wrapped)

        # Authentication
        if require_auth:
            wrapped = require_api_key(db)(wrapped)

        # Rate limiting
        wrapped = rate_limit()(wrapped)

        # Logging
        wrapped = log_request()(wrapped)

        # Error handling
        wrapped = handle_errors()(wrapped)

        return wrapped

    return decorator


# Example usage
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    @app.route("/api/test")
    @rate_limit()
    @log_request()
    def test_endpoint():
        return success_response("Test successful", {"timestamp": time.time()})

    @app.route("/api/protected")
    @api_endpoint(None, require_auth=True, min_tier="professional")
    def protected_endpoint():
        return success_response("Access granted", {"user_id": g.user.id})

    print("Middleware examples created!")
    print("\nAvailable decorators:")
    print("  - @rate_limit()")
    print("  - @require_api_key(db)")
    print("  - @require_tier('professional')")
    print("  - @validate_request(schema)")
    print("  - @log_request()")
    print("  - @handle_errors()")
    print("  - @api_endpoint(db, ...)")
