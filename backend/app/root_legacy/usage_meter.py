from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Smart Meter Usage Tracking System
Comprehensive tracking of every user action and resource consumption
"""

from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps

from flask import g, request
from flask_login import current_user

from .models_auth import User, db


class SmartMeterEvent(db.Model):
    """Track individual usage events with detailed metadata"""

    __tablename__ = "smart_meter_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Event Classification
    event_type = db.Column(
        db.String(50), nullable=False, index=True
    )  # 'ai_request', 'file_upload', 'analysis', etc.
    event_category = db.Column(
        db.String(50), nullable=False, index=True
    )  # 'compute', 'storage', 'api', 'feature'
    resource_name = db.Column(
        db.String(100)
    )  # Specific resource used (e.g., 'gpt-4', 'claude-3-5')

    # Quantitative Metrics
    quantity = db.Column(db.Float, default=1.0)  # Generic quantity (files, requests, etc.)
    tokens_input = db.Column(db.Integer, default=0)  # AI input tokens
    tokens_output = db.Column(db.Integer, default=0)  # AI output tokens
    duration_seconds = db.Column(db.Float, default=0.0)  # Processing time
    file_size_bytes = db.Column(db.BigInteger, default=0)  # File sizes

    # Cost Attribution
    cost_usd = db.Column(db.Numeric(12, 6), default=0)  # Actual cost in USD
    cost_credits = db.Column(db.Integer, default=0)  # Internal credit system

    # Context & Metadata
    endpoint = db.Column(db.String(200))  # API endpoint called
    ip_address = db.Column(db.String(45))  # IPv4/IPv6
    user_agent = db.Column(db.String(500))  # Browser/client info
    session_id = db.Column(db.String(100))  # User session
    request_id = db.Column(db.String(100), index=True)  # Trace requests

    # Result Status
    status = db.Column(
        db.String(20), default="success"
    )  # 'success', 'error', 'throttled', 'denied'
    error_message = db.Column(db.Text)  # If failed

    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Relationships
    user = db.relationship("User", backref=db.backref("meter_events", lazy="dynamic"))

    def __repr__(self):
        return f"<SmartMeterEvent {self.event_type} user={self.user_id} cost=${self.cost_usd}>"


class UsageQuota(db.Model):
    """Real-time quota tracking per user with period resets"""

    __tablename__ = "usage_quotas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # Period Tracking
    period_start = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)

    # AI Usage (Tokens)
    ai_tokens_used = db.Column(db.BigInteger, default=0)
    ai_tokens_limit = db.Column(db.BigInteger, default=100000)
    ai_requests_count = db.Column(db.Integer, default=0)
    ai_requests_limit = db.Column(db.Integer, default=1000)

    # Storage
    storage_bytes_used = db.Column(db.BigInteger, default=0)
    storage_bytes_limit = db.Column(db.BigInteger, default=1073741824)  # 1GB default

    # Feature Counters
    files_uploaded_count = db.Column(db.Integer, default=0)
    files_uploaded_limit = db.Column(db.Integer, default=100)

    analyses_count = db.Column(db.Integer, default=0)
    analyses_limit = db.Column(db.Integer, default=50)

    workflows_executed_count = db.Column(db.Integer, default=0)
    workflows_executed_limit = db.Column(db.Integer, default=50)

    # API Usage
    api_calls_count = db.Column(db.Integer, default=0)
    api_calls_limit = db.Column(db.Integer, default=10000)

    # Cost Tracking
    total_cost_usd = db.Column(db.Numeric(12, 2), default=0)
    cost_limit_usd = db.Column(db.Numeric(12, 2), default=50)

    # Rate Limiting (per minute)
    requests_this_minute = db.Column(db.Integer, default=0)
    requests_per_minute_limit = db.Column(db.Integer, default=60)
    last_request_timestamp = db.Column(db.DateTime)

    # Alert Flags
    alert_80_percent_sent = db.Column(db.Boolean, default=False)
    alert_95_percent_sent = db.Column(db.Boolean, default=False)
    alert_100_percent_sent = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("usage_quota", uselist=False))

    def reset_if_new_period(self):
        """Reset quotas if we've entered a new billing period"""
        now = datetime.utcnow()
        if now >= self.period_end:
            # Calculate new period (monthly)
            new_start = self.period_end
            new_end = (new_start + timedelta(days=32)).replace(day=1)

            self.period_start = new_start
            self.period_end = new_end

            # Reset counters
            self.ai_tokens_used = 0
            self.ai_requests_count = 0
            self.storage_bytes_used = 0
            self.files_uploaded_count = 0
            self.analyses_count = 0
            self.workflows_executed_count = 0
            self.api_calls_count = 0
            self.total_cost_usd = Decimal("0")

            # Reset alerts
            self.alert_80_percent_sent = False
            self.alert_95_percent_sent = False
            self.alert_100_percent_sent = False

            db.session.commit()

Optional[def check_quota(self, quota_type: str, amount: float = 1) -> tuple[bool, str]]:
        """
        Check if user has quota available for a specific resource

        Returns: (has_quota: bool, error_message: Optional[str])
        """
        self.reset_if_new_period()

        quota_checks = {
            "ai_tokens": (self.ai_tokens_used + amount, self.ai_tokens_limit),
            "ai_requests": (self.ai_requests_count + amount, self.ai_requests_limit),
            "storage": (self.storage_bytes_used + amount, self.storage_bytes_limit),
            "files": (self.files_uploaded_count + amount, self.files_uploaded_limit),
            "analyses": (self.analyses_count + amount, self.analyses_limit),
            "workflows": (self.workflows_executed_count + amount, self.workflows_executed_limit),
            "api_calls": (self.api_calls_count + amount, self.api_calls_limit),
        }

        if quota_type not in quota_checks:
            return True, None

        current, limit = quota_checks[quota_type]

        # -1 means unlimited
        if limit == -1:
            return True, None

        if current > limit:
            return False, f"Quota exceeded for {quota_type}. Limit: {limit}, Current: {current}"

        return True, None

    def increment_quota(self, quota_type: str, amount: float = 1):
        """Increment a quota counter"""
        quota_fields = {
            "ai_tokens": "ai_tokens_used",
            "ai_requests": "ai_requests_count",
            "storage": "storage_bytes_used",
            "files": "files_uploaded_count",
            "analyses": "analyses_count",
            "workflows": "workflows_executed_count",
            "api_calls": "api_calls_count",
        }

        if quota_type in quota_fields:
            field = quota_fields[quota_type]
            current = getattr(self, field)
            setattr(self, field, current + amount)
            self.updated_at = datetime.utcnow()
            db.session.commit()

    def check_rate_limit(self) -> bool:
        """Check if user is within per-minute rate limit"""
        now = datetime.utcnow()

        # Reset counter if new minute
        if self.last_request_timestamp:
            seconds_since = (now - self.last_request_timestamp).total_seconds()
            if seconds_since >= 60:
                self.requests_this_minute = 0

        return self.requests_this_minute < self.requests_per_minute_limit

    def get_usage_percent(self, quota_type: str) -> float:
        """Get current usage as percentage of limit"""
        quota_map = {
            "ai_tokens": (self.ai_tokens_used, self.ai_tokens_limit),
            "ai_requests": (self.ai_requests_count, self.ai_requests_limit),
            "storage": (self.storage_bytes_used, self.storage_bytes_limit),
            "files": (self.files_uploaded_count, self.files_uploaded_limit),
            "analyses": (self.analyses_count, self.analyses_limit),
            "workflows": (self.workflows_executed_count, self.workflows_executed_limit),
            "api_calls": (self.api_calls_count, self.api_calls_limit),
        }

        if quota_type not in quota_map:
            return 0.0

        used, limit = quota_map[quota_type]

        if limit == -1:  # Unlimited
            return 0.0

        if limit == 0:
            return 100.0

        return min(100.0, (used / limit) * 100.0)

    def __repr__(self):
        return (
            f"<UsageQuota user={self.user_id} tokens={self.ai_tokens_used}/{self.ai_tokens_limit}>"
        )


class SmartMeter:
    """Smart meter service for tracking all user activities"""

    @staticmethod
    def initialize_user_quota(user_id: int):
        """Initialize quota for a new user based on their tier"""
        user = User.query.get(user_id)
        if not user:
            return None

        quota = UsageQuota.query.filter_by(user_id=user_id).first()
        if quota:
            return quota

        limits = user.get_tier_limits()
        now = datetime.utcnow()
        period_end = (now + timedelta(days=32)).replace(day=1)

        quota = UsageQuota(
            user_id=user_id,
            period_start=now,
            period_end=period_end,
            ai_tokens_limit=limits.get("ai_tokens_per_month", 100000),
            ai_requests_limit=limits.get("ai_requests_per_month", 1000),
            storage_bytes_limit=limits.get("storage_gb", 1) * 1073741824,  # GB to bytes
            files_uploaded_limit=limits.get("pdf_documents_per_month", 100),
            analyses_limit=limits.get("bwc_videos_per_month", 50),
            workflows_executed_limit=limits.get("workflows_per_month", 50),
            api_calls_limit=limits.get("api_calls_per_month", 10000),
            cost_limit_usd=Decimal(str(limits.get("monthly_budget_usd", 50))),
        )

        db.session.add(quota)
        db.session.commit()

        return quota

    @staticmethod
    def track_event(
        event_type: str,
        event_category: str,
Optional[user_id: int] = None,
Optional[resource_name: str] = None,
        quantity: float = 1.0,
        tokens_input: int = 0,
        tokens_output: int = 0,
        duration_seconds: float = 0.0,
        file_size_bytes: int = 0,
        cost_usd: float = 0.0,
        status: str = "success",
Optional[error_message: str] = None,
    ) -> SmartMeterEvent:
        """
        Track a usage event

        Args:
            event_type: Type of event ('ai_request', 'file_upload', 'analysis', etc.)
            event_category: Category ('compute', 'storage', 'api', 'feature')
            user_id: User ID (defaults to current_user)
            resource_name: Specific resource used
            quantity: Generic quantity metric
            tokens_input: AI input tokens
            tokens_output: AI output tokens
            duration_seconds: Processing duration
            file_size_bytes: File size
            cost_usd: Actual cost
            status: Event status ('success', 'error', 'throttled', 'denied')
            error_message: Error details if failed
        """
        if user_id is None and hasattr(current_user, "id"):
            user_id = current_user.id

        if not user_id:
            return None

        # Get request context
        endpoint = request.endpoint if request else None
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get("User-Agent", "")[:500] if request else None
        session_id = request.cookies.get("session") if request else None
        request_id = g.get("request_id") if hasattr(g, "request_id") else None

        event = SmartMeterEvent(
            user_id=user_id,
            event_type=event_type,
            event_category=event_category,
            resource_name=resource_name,
            quantity=quantity,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_seconds=duration_seconds,
            file_size_bytes=file_size_bytes,
            cost_usd=Decimal(str(cost_usd)),
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            status=status,
            error_message=error_message,
        )

        db.session.add(event)
        db.session.commit()

        return event

    @staticmethod
    def get_user_stats(user_id: int, days: int = 30) -> dict:
        """Get comprehensive usage statistics for a user"""
        since = datetime.utcnow() - timedelta(days=days)

        # Get quota
        quota = UsageQuota.query.filter_by(user_id=user_id).first()
        if not quota:
            quota = SmartMeter.initialize_user_quota(user_id)

        quota.reset_if_new_period()

        # Get events
        events = SmartMeterEvent.query.filter(
            SmartMeterEvent.user_id == user_id, SmartMeterEvent.timestamp >= since
        ).all()

        # Aggregate by event type
        by_type = {}
        total_cost = Decimal("0")
        total_tokens = 0

        for event in events:
            if event.event_type not in by_type:
                by_type[event.event_type] = {
                    "count": 0,
                    "total_cost": Decimal("0"),
                    "total_tokens": 0,
                }

            by_type[event.event_type]["count"] += 1
            by_type[event.event_type]["total_cost"] += event.cost_usd or 0
            by_type[event.event_type]["total_tokens"] += (event.tokens_input or 0) + (
                event.tokens_output or 0
            )

            total_cost += event.cost_usd or 0
            total_tokens += (event.tokens_input or 0) + (event.tokens_output or 0)

        return {
            "period": {
                "start": quota.period_start.isoformat(),
                "end": quota.period_end.isoformat(),
                "days_remaining": (quota.period_end - datetime.utcnow()).days,
            },
            "quotas": {
                "ai_tokens": {
                    "used": quota.ai_tokens_used,
                    "limit": quota.ai_tokens_limit,
                    "percent": quota.get_usage_percent("ai_tokens"),
                },
                "ai_requests": {
                    "used": quota.ai_requests_count,
                    "limit": quota.ai_requests_limit,
                    "percent": quota.get_usage_percent("ai_requests"),
                },
                "storage": {
                    "used": quota.storage_bytes_used,
                    "limit": quota.storage_bytes_limit,
                    "percent": quota.get_usage_percent("storage"),
                },
                "files": {
                    "used": quota.files_uploaded_count,
                    "limit": quota.files_uploaded_limit,
                    "percent": quota.get_usage_percent("files"),
                },
                "analyses": {
                    "used": quota.analyses_count,
                    "limit": quota.analyses_limit,
                    "percent": quota.get_usage_percent("analyses"),
                },
                "workflows": {
                    "used": quota.workflows_executed_count,
                    "limit": quota.workflows_executed_limit,
                    "percent": quota.get_usage_percent("workflows"),
                },
                "api_calls": {
                    "used": quota.api_calls_count,
                    "limit": quota.api_calls_limit,
                    "percent": quota.get_usage_percent("api_calls"),
                },
                "cost": {
                    "used": float(quota.total_cost_usd),
                    "limit": float(quota.cost_limit_usd),
                    "percent": (
                        min(
                            100.0, (float(quota.total_cost_usd) / float(quota.cost_limit_usd)) * 100
                        )
                        if quota.cost_limit_usd > 0
                        else 0
                    ),
                },
            },
            "recent_activity": {
                "total_events": len(events),
                "by_type": {k: v["count"] for k, v in by_type.items()},
                "total_cost_usd": float(total_cost),
                "total_tokens": total_tokens,
            },
        }


Optional[def track_usage(event_type: str, event_category: str = "feature", quota_type: str] = None):
    """
    Decorator to automatically track usage of functions

    Usage:
        @track_usage('ai_request', 'compute', quota_type='ai_requests')
        def call_ai_model():
            pass
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()

            # Check quota before executing
            if quota_type and hasattr(current_user, "id"):
                quota = UsageQuota.query.filter_by(user_id=current_user.id).first()
                if not quota:
                    quota = SmartMeter.initialize_user_quota(current_user.id)

                has_quota, error_msg = quota.check_quota(quota_type)
                if not has_quota:
                    SmartMeter.track_event(
                        event_type=event_type,
                        event_category=event_category,
                        status="denied",
                        error_message=error_msg,
                    )
                    from flask import jsonify

                    return (
                        jsonify(
                            {
                                "error": "Quota exceeded",
                                "message": error_msg,
                                "upgrade_url": "/pricing",
                            }
                        ),
                        429,
                    )

            # Execute function
            try:
                result = f(*args, **kwargs)
                status = "success"
                error_msg = None
            except Exception as e:
                result = None
                status = "error"
                error_msg = str(e)
                raise
            finally:
                # Track event
                duration = (datetime.utcnow() - start_time).total_seconds()
                SmartMeter.track_event(
                    event_type=event_type,
                    event_category=event_category,
                    duration_seconds=duration,
                    status=status,
                    error_message=error_msg,
                )

                # Increment quota
                if quota_type and hasattr(current_user, "id"):
                    quota = UsageQuota.query.filter_by(user_id=current_user.id).first()
                    if quota:
                        quota.increment_quota(quota_type)

            return result

        return wrapper

    return decorator