# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Authentication & Tier System
Database models for users, tiers, and usage tracking
"""

from datetime import UTC, datetime, timedelta
from enum import Enum

from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
bcrypt = Bcrypt()

# Constants
USERS_ID_FK = "users.id"
GREETING_WELCOME_BACK = "Welcome back"


def utc_now():
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


class TierLevel(Enum):
    """Subscription tier levels with fair scaling"""

    FREE = 0
    STARTER = 29  # Entry tier for price-sensitive users
    PROFESSIONAL = 79  # Main tier for solo/small firms
    PREMIUM = 199  # Power users with soft caps
    ENTERPRISE = 599  # Organizations with soft caps
    ADMIN = 9999


class User(UserMixin, db.Model):
    """User account model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile
    full_name = db.Column(db.String(100))
    organization = db.Column(db.String(200))

    # Tier & subscription
    tier = db.Column(db.Enum(TierLevel), default=TierLevel.FREE, nullable=False)
    subscription_start = db.Column(db.DateTime, default=utc_now)
    subscription_end = db.Column(db.DateTime)

    # Stripe subscription tracking
    stripe_customer_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(100), unique=True, nullable=True)
    stripe_subscription_status = db.Column(
        db.String(50), nullable=True
    )  # active, canceled, past_due, etc.
    stripe_current_period_end = db.Column(db.DateTime, nullable=True)
    trial_end = db.Column(db.DateTime, nullable=True)  # For 3-day trial tracking
    is_on_trial = db.Column(db.Boolean, default=False)

    # FREE tier one-time upload tracking
    one_time_upload_used = db.Column(
        db.Boolean, default=False
    )  # Track if FREE user used their one upload
    one_time_upload_date = db.Column(db.DateTime, nullable=True)  # When they used it

    # Storage tracking
    storage_used_mb = db.Column(db.Float, default=0.0)

    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=utc_now)
    last_login = db.Column(db.DateTime)

    # Relationships
    usage = db.relationship(
        "UsageTracking", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = utc_now()
        db.session.commit()

    @property
    def is_subscription_active(self):
        """Check if subscription is active"""
        if self.tier == TierLevel.ADMIN:
            return True
        if not self.subscription_end:
            return self.tier == TierLevel.FREE
        return utc_now() < self.subscription_end

    @property
    def tier_name(self):
        """Get professional tier display name"""
        tier_display_names = {
            TierLevel.FREE: "Explorer",
            TierLevel.STARTER: "Practitioner",
            TierLevel.PROFESSIONAL: "Counselor",
            TierLevel.PREMIUM: "Advocate",
            TierLevel.ENTERPRISE: "Enterprise",
            TierLevel.ADMIN: "Administrator",
        }
        return tier_display_names.get(self.tier, self.tier.name.title())

    @property
    def tier_greeting(self):
        """Get professional greeting for tier"""
        greetings = {
            TierLevel.FREE: "Welcome",
            TierLevel.STARTER: GREETING_WELCOME_BACK,
            TierLevel.PROFESSIONAL: "Good to see you",
            TierLevel.PREMIUM: GREETING_WELCOME_BACK,
            TierLevel.ENTERPRISE: "Welcome",
            TierLevel.ADMIN: GREETING_WELCOME_BACK,
        }
        return greetings.get(self.tier, "Welcome")

    @property
    def tier_price(self):
        """Get tier monthly price"""
        return self.tier.value

    @property
    def is_admin_user(self):
        """Check if user is an admin (via tier or role flag)"""
        return self.tier == TierLevel.ADMIN or self.is_admin

    @property
    def is_enterprise(self):
        """Check if user has enterprise or admin tier"""
        return self.tier in [TierLevel.ENTERPRISE, TierLevel.ADMIN]

    def get_tier_limits(self):
        """Get usage limits for current tier"""
        limits = {
            TierLevel.FREE: {
                # Zero-cost tier: Demo + One-time upload only
                "bwc_videos_per_month": 1,  # Limited demo
                "pdf_documents_per_month": 1,  # Limited demo
                "document_pages_per_month": 5,  # 5 pages max
                "one_time_file_upload": 1,  # ONE file ever (PDF or video)
                "one_time_upload_used": False,  # Track if used
                "max_video_duration_minutes": 5,  # 5 min max for video
                "max_pdf_pages": 10,  # 10 pages max for PDF
                "max_file_size_mb": 50,  # Reduced from 100
                "demo_cases_count": 3,  # Pre-loaded demo cases
                "transcription_minutes_per_month": 10,
                "search_queries_per_month": 100,
                "storage_gb": 1,  # Minimal storage for demo data
                "export_watermark": True,
                "data_retention_days": 7,  # Auto-delete after 7 days
                "case_limit": 1,  # 1 personal case (from one-time upload)
                "ai_assistant_access": "basic",
                "court_ready_reports": False,
                "educational_access": True,  # Access to guides & templates
                "template_downloads": True,  # Can download templates
                "overage_allowed": False,
            },
            TierLevel.STARTER: {  # ENTRY TIER ($29/mo) - HARD CAP for predictable pricing
                "bwc_videos_per_month": 10,  # Hard cap
                "bwc_video_hours_per_month": 10,  # 10 hours total (1hr per video avg)
                "max_file_size_mb": 512,
                "pdf_documents_per_month": 5,  # Hard cap
                "document_pages_per_month": 250,  # 50 pages per PDF avg
                "transcription_minutes_per_month": 60,
                "ai_assistant_access": "basic",
                "search_queries_per_month": -1,  # Unlimited
                "storage_gb": 10,
                "export_watermark": False,
                "case_limit": 5,  # Hard cap
                "court_ready_reports": "basic",
                "api_access": False,
                "trial_days": 7,  # 7-day free trial
                "overage_allowed": False,  # HARD CAP - no surprise bills
            },
            TierLevel.PROFESSIONAL: {
                "bwc_videos_per_month": 25,  # Soft cap
                "bwc_video_hours_per_month": 20,  # ~20 hrs video processing
                "max_file_size_mb": 1024,
                "pdf_documents_per_month": 50,  # Soft cap
                "document_pages_per_month": 2500,
                "transcription_minutes_per_month": 1200,  # 20 hours
                "ai_assistant_access": "premium",
                "search_queries_per_month": -1,  # Unlimited
                "storage_gb": 25,  # 25GB
                "export_watermark": False,
                "case_limit": 25,  # Soft cap
                "court_ready_reports": "basic",
                "trial_days": 7,  # 7-day free trial
                "api_access": False,
                # Premium AI token limits (sustainable pricing)
                "claude_tokens_per_month": 500_000,  # ~$22 value
                "gpt_tokens_per_month": 500_000,  # ~$4 value
                "gemini_tokens_per_month": 1_000_000,  # ~$3 value
                "reasoning_ai_models": ["claude-opus", "gpt-5", "gemini-pro"],
                "overage_allowed": True,  # SOFT CAP - pay for what you use
                "overage_fee_per_video": 1.50,
                "overage_fee_per_pdf": 0.75,
                "overage_fee_per_case": 3.00,
                "overage_fee_per_gb": 0.40,
                "overage_fee_per_1k_tokens": 0.05,  # $50/1M tokens overage
            },
            TierLevel.PREMIUM: {
                "bwc_videos_per_month": 200,  # Soft cap
                "bwc_video_hours_per_month": 100,  # ~100 hrs video processing
                "max_file_size_mb": 5120,
                "pdf_documents_per_month": 300,  # Soft cap
                "document_pages_per_month": 15000,
                "transcription_minutes_per_month": 6000,  # 100 hours
                "ai_assistant_access": "full",
                "search_queries_per_month": -1,  # Unlimited
                "storage_gb": 100,
                "export_watermark": False,
                "case_limit": 100,  # Soft cap
                "court_ready_reports": "advanced",
                "timeline_builder": True,
                "api_access": True,
                "forensic_analysis": True,
                "priority_support": True,
                # Premium AI token limits (generous for firm tier)
                "claude_tokens_per_month": 2_000_000,  # ~$90 value
                "gpt_tokens_per_month": 2_000_000,  # ~$16 value
                "gemini_tokens_per_month": 5_000_000,  # ~$15 value
                "reasoning_ai_models": ["claude-opus", "gpt-5", "gemini-pro", "llama-405b"],
                "priority_ai_queue": True,
                # Soft caps with overage billing
                "overage_allowed": True,
                "overage_fee_per_video": 2.00,
                "overage_fee_per_video_hour": 5.00,
                "overage_fee_per_pdf": 1.00,
                "overage_fee_per_case": 5.00,
                "overage_fee_per_1k_tokens": 0.04,  # $40/1M tokens overage (discount)
            },
            TierLevel.ENTERPRISE: {
                "bwc_videos_per_month": -1,  # Unlimited for Enterprise
                "bwc_video_hours_per_month": -1,  # Unlimited
                "max_file_size_mb": 20480,
                "pdf_documents_per_month": -1,  # Unlimited
                "document_pages_per_month": -1,  # Unlimited (alias)
                "transcription_minutes_per_month": -1,  # Unlimited
                "ai_assistant_access": "private_instance",
                "search_queries_per_month": -1,  # Unlimited
                "storage_gb": -1,  # Unlimited
                "export_watermark": False,
                "case_limit": -1,  # Unlimited
                "court_ready_reports": "firm_branded",
                "timeline_builder": True,
                "multi_bwc_sync": 20,
                "api_access": True,
                "forensic_analysis": True,
                "white_label": True,
                "priority_support": True,
                "sla_guaranteed": True,
                "dedicated_pm": True,
                "on_premises_data": True,
                "concurrent_users": -1,  # Unlimited
                "overage_allowed": False,  # No limits to exceed
                "is_unlimited": True,
            },
            TierLevel.ADMIN: {
                "bwc_videos_per_month": -1,
                "max_file_size_mb": -1,
                "document_pages_per_month": -1,
                "pdf_documents_per_month": -1,
                "transcription_minutes_per_month": -1,
                "search_queries_per_month": -1,
                "storage_gb": -1,
                "export_watermark": False,
                "multi_bwc_sync": -1,
                "api_access": True,
                "forensic_analysis": True,
                "white_label": True,
                "priority_support": True,
                "backend_access": True,
                "admin_dashboard": True,
                "is_unlimited": True,
            },
        }
        return limits.get(self.tier, limits[TierLevel.FREE])

    def can_access_feature(self, feature):
        """Check if user has access to a feature"""
        limits = self.get_tier_limits()
        return limits.get(feature, False)

    def can_analyze(self):
        """Check if user can perform analysis (based on monthly limits)"""
        limits = self.get_tier_limits()
        bwc_limit = limits.get("bwc_videos_per_month", 0)

        # Unlimited for some tiers
        if bwc_limit == -1:
            return True

        # Check current month usage
        usage = UsageTracking.get_or_create_current(self.id)

        return usage.bwc_videos_processed < bwc_limit

    def __repr__(self):
        return f"<User {self.email} ({self.tier_name})>"


class UsageTracking(db.Model):
    """Track user usage per month"""

    __tablename__ = "usage_tracking"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USERS_ID_FK), nullable=False)

    # Period
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    # Usage counters
    bwc_videos_processed = db.Column(db.Integer, default=0)
    bwc_video_hours_used = db.Column(db.Float, default=0.0)  # Track video hours
    pdf_documents_processed = db.Column(db.Integer, default=0)  # Track PDF count (not pages)
    document_pages_processed = db.Column(db.Integer, default=0)  # Still track pages for stats
    transcription_minutes_used = db.Column(db.Integer, default=0)
    search_queries_made = db.Column(db.Integer, default=0)
    storage_used_mb = db.Column(db.Float, default=0)
    api_calls_made = db.Column(db.Integer, default=0)
    cases_created = db.Column(db.Integer, default=0)  # Track case count

    # Timestamps
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    __table_args__ = (db.UniqueConstraint("user_id", "year", "month", name="unique_user_month"),)

    @staticmethod
    def get_or_create_current(user_id):
        """Get or create usage tracking for current month"""
        now = utc_now()
        usage = UsageTracking.query.filter_by(
            user_id=user_id, year=now.year, month=now.month
        ).first()

        if not usage:
            usage = UsageTracking(user_id=user_id, year=now.year, month=now.month)
            db.session.add(usage)
            db.session.commit()

        return usage

    def increment(self, field, amount=1):
        """Increment a usage counter"""
        current = getattr(self, field, 0)
        setattr(self, field, current + amount)
        self.updated_at = utc_now()
        db.session.commit()

    def check_limit(self, field, user):
        """Check if user has hit their limit for a field"""
        limits = user.get_tier_limits()
        limit = limits.get(field.replace("_used", "_per_month").replace("_made", "_per_month"), 0)

        # -1 means unlimited
        if limit == -1:
            return True

        current = getattr(self, field, 0)
        return current < limit

    def __repr__(self):
        return f"<UsageTracking User:{self.user_id} {self.year}-{self.month:02d}>"


class ApiKey(db.Model):
    """API keys for programmatic access"""

    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USERS_ID_FK), nullable=False)

    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))

    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime)

    user = db.relationship("User", backref="api_keys")

    @staticmethod
    def generate_key():
        """Generate a random API key"""
        import secrets

        return f"bx_{secrets.token_urlsafe(48)}"

    def is_valid(self):
        """Check if API key is valid"""
        if not self.is_active:
            return False
        if self.expires_at and utc_now() > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f"<ApiKey {self.name} ({self.key[:16]}...)>"


class PasswordResetToken(db.Model):
    """Persistent password reset tokens (replaces in-memory storage)"""

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USERS_ID_FK), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    user = db.relationship("User", backref="password_reset_tokens")

    @staticmethod
    def generate(user_id, expires_hours=1):
        """Generate a new password reset token for a user"""
        import secrets

        # Invalidate any existing unused tokens for this user
        PasswordResetToken.query.filter_by(user_id=user_id, used=False).update({"used": True})

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=utc_now() + timedelta(hours=expires_hours),
        )
        db.session.add(reset_token)
        db.session.commit()
        return token

    @staticmethod
    def validate(token):
        """Validate token and return associated user, or None if invalid"""
        reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
        if not reset_token:
            return None
        if utc_now() > reset_token.expires_at:
            return None
        return reset_token.user

    def mark_used(self):
        """Mark token as used after successful password reset"""
        self.used = True
        db.session.commit()

    def __repr__(self):
        return f"<PasswordResetToken user:{self.user_id} expires:{self.expires_at}>"


class EmailVerificationToken(db.Model):
    """Email verification tokens for new user signups"""

    __tablename__ = "email_verification_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USERS_ID_FK), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    user = db.relationship("User", backref="email_verification_tokens")

    @staticmethod
    def generate(user_id, expires_hours=24):
        """Generate a new verification token for a user"""
        import secrets

        # Invalidate previous tokens
        EmailVerificationToken.query.filter_by(user_id=user_id, used=False).update({"used": True})

        token = secrets.token_urlsafe(32)
        verify_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=utc_now() + timedelta(hours=expires_hours),
        )
        db.session.add(verify_token)
        db.session.commit()
        return token

    @staticmethod
    def validate(token):
        """Validate token and return associated user, or None if invalid"""
        verify_token = EmailVerificationToken.query.filter_by(token=token, used=False).first()
        if not verify_token:
            return None
        if utc_now() > verify_token.expires_at:
            return None
        return verify_token.user

    def mark_used(self):
        """Mark token as used after verification"""
        self.used = True
        db.session.commit()

    def __repr__(self):
        return f"<EmailVerificationToken user:{self.user_id}>"
