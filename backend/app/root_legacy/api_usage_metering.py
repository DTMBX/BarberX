from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
API Usage Metering Service
Secure, encrypted, and verifiable usage tracking for OpenAI and other API providers

Features:
- Encrypted API key storage (Fernet/AES-256)
- Per-user usage metering with real-time tracking
- Verifiable usage logs with SHA-256 checksums
- Cost estimation and budget alerts
- Rate limiting per tier
- Audit trail with cryptographic verification
"""

import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import g
from sqlalchemy import func

from .models_auth import UsageTracking, User, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENCRYPTION UTILITIES
# =============================================================================


class SecureKeyManager:
    """
    Secure key management for API key encryption
    Uses Fernet (AES-128-CBC with HMAC) for authenticated encryption
    """

    _instance = None
    _fernet = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._fernet is None:
            self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize Fernet encryption with secure key derivation"""
        # Get master key from environment
        master_key = os.getenv("API_KEY_ENCRYPTION_KEY")

        if not master_key:
            # Generate a warning but allow operation with derived key
            logger.warning(
                "API_KEY_ENCRYPTION_KEY not set. Using derived key (not recommended for production)"
            )
            master_key = self._derive_fallback_key()

        # Ensure key is proper Fernet format (32 bytes, base64 encoded)
        try:
            # Try to use as-is if already valid Fernet key
            self._fernet = Fernet(
                master_key.encode() if isinstance(master_key, str) else master_key
            )
        except Exception:
            # Derive a proper key using PBKDF2
            self._fernet = Fernet(self._derive_key(master_key))

    def _derive_fallback_key(self) -> str:
        """Derive a fallback key from system entropy (NOT for production)"""
        # Use multiple sources of entropy
        entropy_sources = [
            os.getenv("SECRET_KEY", "Evident-default"),
            os.getenv("FLASK_SECRET_KEY", ""),
            str(os.getpid()),
        ]
        combined = ":".join(entropy_sources)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def _derive_key(self, master_key: str) -> bytes:
        """Derive a Fernet-compatible key using PBKDF2"""
        salt = b"Evident-api-key-salt-v1"  # Static salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return key

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string (e.g., API key)

        Returns:
            Base64-encoded encrypted data with version prefix
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty value")

        encrypted = self._fernet.encrypt(plaintext.encode())
        # Add version prefix for future key rotation
        return f"v1:{encrypted.decode()}"

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string

        Returns:
            Decrypted plaintext

        Raises:
            InvalidToken: If decryption fails
        """
        if not ciphertext:
            raise ValueError("Cannot decrypt empty value")

        # Handle versioned format
        if ciphertext.startswith("v1:"):
            ciphertext = ciphertext[3:]

        try:
            decrypted = self._fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except InvalidToken:
            logger.error("Failed to decrypt API key - invalid token")
            raise

    def rotate_key(self, old_ciphertext: str, new_fernet: Fernet) -> str:
        """Rotate encryption to new key"""
        plaintext = self.decrypt(old_ciphertext)
        new_encrypted = new_fernet.encrypt(plaintext.encode())
        return f"v2:{new_encrypted.decode()}"


# =============================================================================
# USAGE TRACKING MODELS
# =============================================================================


class APIProvider(Enum):
    """Supported API providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class UsageRecord:
    """Single usage record with verification"""

    user_id: int
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: Decimal
    timestamp: datetime
    request_hash: str  # SHA-256 of request for verification
    response_hash: str  # SHA-256 of response for verification

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": str(self.estimated_cost_usd),
            "timestamp": self.timestamp.isoformat(),
            "request_hash": self.request_hash,
            "response_hash": self.response_hash,
        }

    def compute_verification_hash(self) -> str:
        """Compute verification hash for this record"""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class APIUsageLog(db.Model):
    """Detailed API usage log with cryptographic verification"""

    __tablename__ = "api_usage_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Provider & Model
    provider = db.Column(db.String(50), nullable=False, index=True)  # openai, anthropic, etc.
    model = db.Column(db.String(100), nullable=False, index=True)  # gpt-4, claude-3, etc.

    # Token Usage
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)

    # Cost Tracking
    estimated_cost_usd = db.Column(db.Numeric(10, 6), default=0)  # 6 decimal precision

    # Request Context
    endpoint = db.Column(db.String(200))  # /chat/completions, /embeddings, etc.
    request_type = db.Column(db.String(50))  # chat, completion, embedding, transcription

    # Verification Hashes (for audit trail)
    request_hash = db.Column(db.String(64))  # SHA-256 of request payload
    response_hash = db.Column(db.String(64))  # SHA-256 of response payload
    record_hash = db.Column(db.String(64))  # SHA-256 of this record for integrity

    # Status
    success = db.Column(db.Boolean, default=True)
    error_type = db.Column(db.String(50))  # rate_limit, auth_error, etc.

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship("User", backref=db.backref("api_usage_logs", lazy="dynamic"))

    def compute_record_hash(self) -> str:
        """Compute integrity hash for this record"""
        data = {
            "user_id": self.user_id,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": str(self.estimated_cost_usd),
            "request_hash": self.request_hash,
            "response_hash": self.response_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify record integrity"""
        return self.record_hash == self.compute_record_hash()


class UserAPIQuota(db.Model):
    """Per-user API quota and budget tracking"""

    __tablename__ = "user_api_quotas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # Monthly Limits (based on tier)
    monthly_token_limit = db.Column(db.Integer, default=100000)  # Tokens per month
    monthly_cost_limit_usd = db.Column(db.Numeric(10, 2), default=10.00)  # USD per month

    # Current Period Usage
    period_start = db.Column(db.DateTime, default=datetime.utcnow)
    tokens_used_this_period = db.Column(db.Integer, default=0)
    cost_this_period_usd = db.Column(db.Numeric(10, 6), default=0)

    # Alerts
    alert_threshold_percent = db.Column(db.Integer, default=80)  # Alert at 80% usage
    alert_sent = db.Column(db.Boolean, default=False)

    # Rate Limiting
    requests_per_minute = db.Column(db.Integer, default=60)
    last_request_at = db.Column(db.DateTime)
    requests_this_minute = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("api_quota", uselist=False))

    def reset_if_new_period(self):
        """Reset counters if new billing period"""
        if self.period_start:
            # Check if we're in a new month
            now = datetime.utcnow()
            if now.year > self.period_start.year or now.month > self.period_start.month:
                self.period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                self.tokens_used_this_period = 0
                self.cost_this_period_usd = Decimal("0")
                self.alert_sent = False
                db.session.commit()

    def check_rate_limit(self) -> bool:
        """Check if user is within rate limit"""
        now = datetime.utcnow()

        # Reset counter if new minute
        if self.last_request_at:
            if (now - self.last_request_at).total_seconds() >= 60:
                self.requests_this_minute = 0

        return self.requests_this_minute < self.requests_per_minute

    def increment_request(self):
        """Increment request counter"""
        self.last_request_at = datetime.utcnow()
        self.requests_this_minute += 1
        db.session.commit()


class EncryptedAPIKey(db.Model):
    """Securely stored API keys with encryption"""

    __tablename__ = "encrypted_api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Key Info
    provider = db.Column(db.String(50), nullable=False)  # openai, anthropic, etc.
    key_name = db.Column(db.String(100))  # User-friendly name
    encrypted_key = db.Column(db.Text, nullable=False)  # Fernet encrypted
    key_prefix = db.Column(db.String(10))  # First few chars for identification (sk-...)
    key_hash = db.Column(db.String(64), nullable=False, unique=True)  # SHA-256 for dedup

    # Validation
    is_active = db.Column(db.Boolean, default=True)
    is_valid = db.Column(db.Boolean, default=True)
    last_validated_at = db.Column(db.DateTime)
    validation_error = db.Column(db.String(255))

    # Usage Stats
    total_requests = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    total_cost_usd = db.Column(db.Numeric(10, 2), default=0)
    last_used_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("encrypted_api_keys", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "provider", "key_hash", name="unique_user_provider_key"),
    )


# =============================================================================
# PRICING CALCULATOR
# =============================================================================


class APIPricingCalculator:
    """Calculate API costs based on provider and model"""

    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "openai": {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
            "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
            "gpt-3.5-turbo-16k": {"prompt": 0.001, "completion": 0.002},
            "text-embedding-3-small": {"prompt": 0.00002, "completion": 0},
            "text-embedding-3-large": {"prompt": 0.00013, "completion": 0},
            "whisper-1": {"prompt": 0.006, "completion": 0},  # Per minute
        },
        "anthropic": {
            "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
            "claude-3.5-sonnet": {"prompt": 0.003, "completion": 0.015},
        },
        "google": {
            "gemini-pro": {"prompt": 0.00025, "completion": 0.0005},
            "gemini-pro-vision": {"prompt": 0.00025, "completion": 0.0005},
        },
    }

    @classmethod
    def calculate_cost(
        cls,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> Decimal:
        """
        Calculate cost for API usage

        Args:
            provider: API provider (openai, anthropic, etc.)
            model: Model name
            prompt_tokens: Number of prompt/input tokens
            completion_tokens: Number of completion/output tokens

        Returns:
            Estimated cost in USD
        """
        provider_pricing = cls.PRICING.get(provider.lower(), {})

        # Find matching model (handle variations like gpt-4-0613)
        model_pricing = None
        model_lower = model.lower()

        # First try exact match
        if model_lower in provider_pricing:
            model_pricing = provider_pricing[model_lower]
        else:
            # Sort keys by length descending to match more specific models first
            # e.g., "gpt-4o-mini" should match before "gpt-4"
            sorted_keys = sorted(provider_pricing.keys(), key=len, reverse=True)
            for model_key in sorted_keys:
                if model_lower.startswith(model_key) or model_key in model_lower:
                    model_pricing = provider_pricing[model_key]
                    break

        if not model_pricing:
            # Default fallback pricing
            logger.warning(f"Unknown model {model} for provider {provider}, using default pricing")
            model_pricing = {"prompt": 0.01, "completion": 0.03}

        prompt_cost = Decimal(str(prompt_tokens)) / 1000 * Decimal(str(model_pricing["prompt"]))
        completion_cost = (
            Decimal(str(completion_tokens)) / 1000 * Decimal(str(model_pricing["completion"]))
        )

        return prompt_cost + completion_cost


# =============================================================================
# MAIN METERING SERVICE
# =============================================================================


class APIUsageMeteringService:
    """
    Comprehensive API usage metering service

    Features:
    - Encrypted API key storage
    - Real-time usage tracking
    - Verifiable audit logs
    - Per-tier rate limiting
    - Cost estimation and alerts
    """

    def __init__(self):
        self.key_manager = SecureKeyManager()
        self.pricing_calculator = APIPricingCalculator()
        self.logger = logging.getLogger(__name__)

    # -------------------------------------------------------------------------
    # API Key Management
    # -------------------------------------------------------------------------

    def store_api_key(
        self,
        user_id: int,
        provider: str,
        api_key: str,
Optional[key_name: str] = None,
    ) -> dict[str, Any]:
        """
        Securely store an API key

        Args:
            user_id: User ID
            provider: API provider (openai, anthropic, etc.)
            api_key: The raw API key
            key_name: Optional friendly name

        Returns:
            Result dict with status and masked key
        """
        try:
            # Compute key hash for deduplication
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Check for duplicate
            existing = EncryptedAPIKey.query.filter_by(
                user_id=user_id,
                provider=provider,
                key_hash=key_hash,
            ).first()

            if existing:
                return {
                    "success": False,
                    "error": "This API key is already stored",
                    "key_id": existing.id,
                }

            # Encrypt the key
            encrypted = self.key_manager.encrypt(api_key)

            # Extract prefix for identification
            key_prefix = api_key[:7] if len(api_key) > 7 else api_key[:3]

            # Deactivate other keys for this provider
            EncryptedAPIKey.query.filter_by(
                user_id=user_id,
                provider=provider,
                is_active=True,
            ).update({"is_active": False})

            # Create new key record
            key_record = EncryptedAPIKey(
                user_id=user_id,
                provider=provider,
                key_name=key_name or f"{provider.title()} API Key",
                encrypted_key=encrypted,
                key_prefix=key_prefix,
                key_hash=key_hash,
                is_active=True,
            )

            db.session.add(key_record)
            db.session.commit()

            self.logger.info(f"Stored API key for user {user_id}, provider {provider}")

            return {
                "success": True,
                "key_id": key_record.id,
                "masked_key": f"{key_prefix}...{api_key[-4:]}",
                "provider": provider,
            }

        except Exception as e:
            self.logger.error(f"Failed to store API key: {str(e)}")
            db.session.rollback()
            return {"success": False, "error": str(e)}

Optional[def get_api_key(self, user_id: int, provider: str = "openai") -> str]:
        """
        Retrieve decrypted API key for user

        Args:
            user_id: User ID
            provider: API provider

        Returns:
            Decrypted API key or None
        """
        key_record = EncryptedAPIKey.query.filter_by(
            user_id=user_id,
            provider=provider,
            is_active=True,
            is_valid=True,
        ).first()

        if not key_record:
            return None

        try:
            decrypted = self.key_manager.decrypt(key_record.encrypted_key)
            return decrypted
        except InvalidToken:
            self.logger.error(f"Failed to decrypt API key for user {user_id}")
            key_record.is_valid = False
            key_record.validation_error = "Decryption failed"
            db.session.commit()
            return None

    def validate_api_key(self, user_id: int, provider: str = "openai") -> dict[str, Any]:
        """Validate stored API key by making a test request"""
        api_key = self.get_api_key(user_id, provider)

        if not api_key:
            return {"valid": False, "error": "No API key found"}

        try:
            if provider == "openai":
                import openai

                client = openai.OpenAI(api_key=api_key)
                models = client.models.list()

                # Update validation status
                key_record = EncryptedAPIKey.query.filter_by(
                    user_id=user_id,
                    provider=provider,
                    is_active=True,
                ).first()

                if key_record:
                    key_record.is_valid = True
                    key_record.last_validated_at = datetime.utcnow()
                    key_record.validation_error = None
                    db.session.commit()

                return {
                    "valid": True,
                    "models_available": [m.id for m in models.data if "gpt" in m.id.lower()][:10],
                }

            return {"valid": True, "message": "Key format validated"}

        except Exception as e:
            # Update validation status
            key_record = EncryptedAPIKey.query.filter_by(
                user_id=user_id,
                provider=provider,
                is_active=True,
            ).first()

            if key_record:
                key_record.is_valid = False
                key_record.validation_error = str(e)[:255]
                db.session.commit()

            return {"valid": False, "error": str(e)}

    def delete_api_key(self, user_id: int, key_id: int) -> dict[str, Any]:
        """Delete an API key"""
        key_record = EncryptedAPIKey.query.filter_by(
            id=key_id,
            user_id=user_id,
        ).first()

        if not key_record:
            return {"success": False, "error": "API key not found"}

        db.session.delete(key_record)
        db.session.commit()

        return {"success": True, "message": "API key deleted"}

    # -------------------------------------------------------------------------
    # Usage Tracking
    # -------------------------------------------------------------------------

    def record_usage(
        self,
        user_id: int,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
Optional[request_data: dict] = None,
Optional[response_data: dict] = None,
        endpoint: str = "/chat/completions",
        success: bool = True,
Optional[error_type: str] = None,
    ) -> APIUsageLog:
        """
        Record API usage with verification hashes

        Args:
            user_id: User ID
            provider: API provider
            model: Model used
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            request_data: Original request for hashing
            response_data: Response for hashing
            endpoint: API endpoint called
            success: Whether request succeeded
            error_type: Type of error if failed

        Returns:
            Created usage log record
        """
        total_tokens = prompt_tokens + completion_tokens

        # Calculate cost
        estimated_cost = self.pricing_calculator.calculate_cost(
            provider, model, prompt_tokens, completion_tokens
        )

        # Compute verification hashes
        request_hash = None
        response_hash = None

        if request_data:
            request_hash = hashlib.sha256(
                json.dumps(request_data, sort_keys=True).encode()
            ).hexdigest()

        if response_data:
            response_hash = hashlib.sha256(
                json.dumps(response_data, sort_keys=True).encode()
            ).hexdigest()

        # Create log entry
        log_entry = APIUsageLog(
            user_id=user_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
            endpoint=endpoint,
            request_type="chat" if "chat" in endpoint else "completion",
            request_hash=request_hash,
            response_hash=response_hash,
            success=success,
            error_type=error_type,
            created_at=datetime.utcnow(),
        )

        # Compute record integrity hash
        db.session.add(log_entry)
        db.session.flush()  # Get ID without committing
        log_entry.record_hash = log_entry.compute_record_hash()

        # Update quota tracking
        self._update_quota(user_id, total_tokens, estimated_cost)

        # Update API key stats
        self._update_key_stats(user_id, provider, total_tokens, estimated_cost)

        # Update general usage tracking
        self._update_usage_tracking(user_id, total_tokens)

        db.session.commit()

        self.logger.info(
            f"Recorded usage for user {user_id}: {total_tokens} tokens, ${estimated_cost:.6f}"
        )

        return log_entry

    def _update_quota(self, user_id: int, tokens: int, cost: Decimal):
        """Update user quota tracking"""
        quota = UserAPIQuota.query.filter_by(user_id=user_id).first()

        if not quota:
            # Create default quota based on user tier
            user = User.query.get(user_id)
            limits = user.get_tier_limits() if user else {}

            quota = UserAPIQuota(
                user_id=user_id,
                monthly_token_limit=limits.get("ai_tokens_per_month", 100000),
                monthly_cost_limit_usd=Decimal(str(limits.get("ai_budget_usd", 10.0))),
                period_start=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0),
            )
            db.session.add(quota)

        # Reset if new period
        quota.reset_if_new_period()

        # Update counters
        quota.tokens_used_this_period += tokens
        quota.cost_this_period_usd += cost

        # Check for alert threshold
        if not quota.alert_sent:
            usage_percent = (quota.tokens_used_this_period / quota.monthly_token_limit) * 100
            if usage_percent >= quota.alert_threshold_percent:
                quota.alert_sent = True
                self._send_usage_alert(user_id, usage_percent)

    def _update_key_stats(self, user_id: int, provider: str, tokens: int, cost: Decimal):
        """Update API key usage statistics"""
        key_record = EncryptedAPIKey.query.filter_by(
            user_id=user_id,
            provider=provider,
            is_active=True,
        ).first()

        if key_record:
            key_record.total_requests += 1
            key_record.total_tokens += tokens
            key_record.total_cost_usd += cost
            key_record.last_used_at = datetime.utcnow()

    def _update_usage_tracking(self, user_id: int, tokens: int):
        """Update general usage tracking"""
        usage = UsageTracking.get_or_create_current(user_id)
        usage.increment("api_calls_made", 1)

    def _send_usage_alert(self, user_id: int, usage_percent: float):
        """Send usage alert (placeholder for email/notification)"""
        self.logger.warning(f"User {user_id} has reached {usage_percent:.1f}% of their API quota")
        # TODO: Implement email notification

    # -------------------------------------------------------------------------
    # Rate Limiting
    # -------------------------------------------------------------------------

Optional[def check_rate_limit(self, user_id: int) -> tuple[bool, str]]:
        """
        Check if user is within rate limits

        Returns:
            Tuple of (allowed, error_message)
        """
        quota = UserAPIQuota.query.filter_by(user_id=user_id).first()

        if not quota:
            return True, None  # No quota = no limits (will be created on first use)

        # Check rate limit
        if not quota.check_rate_limit():
            return False, "Rate limit exceeded. Please wait before making more requests."

        # Check monthly token limit
        quota.reset_if_new_period()

        if quota.tokens_used_this_period >= quota.monthly_token_limit:
            return False, "Monthly token limit exceeded. Please upgrade your plan."

        # Check monthly cost limit
        if quota.cost_this_period_usd >= quota.monthly_cost_limit_usd:
            return False, "Monthly budget limit exceeded. Please upgrade your plan."

        return True, None

    def increment_rate_limit(self, user_id: int):
        """Increment rate limit counter"""
        quota = UserAPIQuota.query.filter_by(user_id=user_id).first()
        if quota:
            quota.increment_request()

    # -------------------------------------------------------------------------
    # Usage Reports
    # -------------------------------------------------------------------------

    def get_usage_summary(
        self,
        user_id: int,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Get usage summary for user

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Usage summary dict
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get aggregated stats
        stats = (
            db.session.query(
                func.sum(APIUsageLog.total_tokens).label("total_tokens"),
                func.sum(APIUsageLog.estimated_cost_usd).label("total_cost"),
                func.count(APIUsageLog.id).label("total_requests"),
                func.sum(APIUsageLog.prompt_tokens).label("prompt_tokens"),
                func.sum(APIUsageLog.completion_tokens).label("completion_tokens"),
            )
            .filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.created_at >= cutoff,
            )
            .first()
        )

        # Get per-model breakdown
        model_breakdown = (
            db.session.query(
                APIUsageLog.model,
                func.sum(APIUsageLog.total_tokens).label("tokens"),
                func.sum(APIUsageLog.estimated_cost_usd).label("cost"),
                func.count(APIUsageLog.id).label("requests"),
            )
            .filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.created_at >= cutoff,
            )
            .group_by(APIUsageLog.model)
            .all()
        )

        # Get daily usage
        daily_usage = (
            db.session.query(
                func.date(APIUsageLog.created_at).label("date"),
                func.sum(APIUsageLog.total_tokens).label("tokens"),
                func.sum(APIUsageLog.estimated_cost_usd).label("cost"),
            )
            .filter(
                APIUsageLog.user_id == user_id,
                APIUsageLog.created_at >= cutoff,
            )
            .group_by(func.date(APIUsageLog.created_at))
            .all()
        )

        # Get quota status
        quota = UserAPIQuota.query.filter_by(user_id=user_id).first()

        return {
            "period_days": days,
            "summary": {
                "total_tokens": stats.total_tokens or 0,
                "total_cost_usd": float(stats.total_cost or 0),
                "total_requests": stats.total_requests or 0,
                "prompt_tokens": stats.prompt_tokens or 0,
                "completion_tokens": stats.completion_tokens or 0,
            },
            "by_model": [
                {
                    "model": m.model,
                    "tokens": m.tokens,
                    "cost_usd": float(m.cost),
                    "requests": m.requests,
                }
                for m in model_breakdown
            ],
            "daily_usage": [
                {
                    "date": str(d.date),
                    "tokens": d.tokens,
                    "cost_usd": float(d.cost),
                }
                for d in daily_usage
            ],
            "quota": {
                "monthly_token_limit": quota.monthly_token_limit if quota else 100000,
                "tokens_used": quota.tokens_used_this_period if quota else 0,
                "monthly_cost_limit_usd": float(quota.monthly_cost_limit_usd) if quota else 10.0,
                "cost_used_usd": float(quota.cost_this_period_usd) if quota else 0,
                "period_start": quota.period_start.isoformat() if quota else None,
            },
        }

    def verify_usage_log(self, log_id: int) -> dict[str, Any]:
        """
        Verify integrity of a usage log entry

        Args:
            log_id: Usage log ID

        Returns:
            Verification result
        """
        log_entry = APIUsageLog.query.get(log_id)

        if not log_entry:
            return {"verified": False, "error": "Log entry not found"}

        is_valid = log_entry.verify_integrity()

        return {
            "verified": is_valid,
            "log_id": log_id,
            "stored_hash": log_entry.record_hash,
            "computed_hash": log_entry.compute_record_hash(),
            "timestamp": log_entry.created_at.isoformat(),
        }

    def export_usage_audit(
        self,
        user_id: int,
Optional[start_date: datetime] = None,
Optional[end_date: datetime] = None,
    ) -> list[dict]:
        """
        Export verifiable usage audit trail

        Args:
            user_id: User ID
            start_date: Start of period
            end_date: End of period

        Returns:
            List of usage records with verification hashes
        """
        query = APIUsageLog.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(APIUsageLog.created_at >= start_date)
        if end_date:
            query = query.filter(APIUsageLog.created_at <= end_date)

        logs = query.order_by(APIUsageLog.created_at).all()

        return [
            {
                "id": log.id,
                "provider": log.provider,
                "model": log.model,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "total_tokens": log.total_tokens,
                "estimated_cost_usd": str(log.estimated_cost_usd),
                "request_hash": log.request_hash,
                "response_hash": log.response_hash,
                "record_hash": log.record_hash,
                "verified": log.verify_integrity(),
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]


# =============================================================================
# FLASK INTEGRATION HELPERS
# =============================================================================


def get_metering_service() -> APIUsageMeteringService:
    """Get or create metering service instance"""
    if "metering_service" not in g:
        g.metering_service = APIUsageMeteringService()
    return g.metering_service


def require_api_key(provider: str = "openai"):
    """Decorator to require valid API key"""
    from functools import wraps

    from flask import jsonify
    from flask_login import current_user

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            service = get_metering_service()
            api_key = service.get_api_key(current_user.id, provider)

            if not api_key:
                return (
                    jsonify(
                        {
                            "error": f"No {provider.title()} API key configured. Please add your API key in settings."
                        }
                    ),
                    400,
                )

            # Store in g for use in route
            g.api_key = api_key
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_rate_limit():
    """Decorator to check rate limits"""
    from functools import wraps

    from flask import jsonify
    from flask_login import current_user

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            service = get_metering_service()
            allowed, error = service.check_rate_limit(current_user.id)

            if not allowed:
                return jsonify({"error": error}), 429

            service.increment_rate_limit(current_user.id)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# =============================================================================
# CLI / TESTING
# =============================================================================


if __name__ == "__main__":
    # Test encryption
    print("Testing SecureKeyManager...")
    km = SecureKeyManager()

    test_key = "sk-test1234567890abcdefghijklmnopqrstuvwxyz"
    encrypted = km.encrypt(test_key)
    print(f"Encrypted: {encrypted[:50]}...")

    decrypted = km.decrypt(encrypted)
    assert decrypted == test_key, "Decryption failed!"
    print("✓ Encryption/decryption works correctly")

    # Test pricing calculator
    print("\nTesting APIPricingCalculator...")
    cost = APIPricingCalculator.calculate_cost("openai", "gpt-4", 1000, 500)
    print(f"GPT-4 (1000 prompt + 500 completion tokens): ${cost:.4f}")

    cost = APIPricingCalculator.calculate_cost("openai", "gpt-4o-mini", 10000, 5000)
    print(f"GPT-4o-mini (10000 prompt + 5000 completion tokens): ${cost:.6f}")

    print("\n✓ API Usage Metering Service ready!")