# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Tier Access Gating Middleware
Enforces subscription tier limits and access control
"""

from functools import wraps

from flask import jsonify, request, session

from .models_auth import TierLevel, UsageTracking, User


def require_tier(minimum_tier):
    """
    Decorator to require minimum subscription tier

    Usage:
        @app.route('/api/premium-feature')
        @require_tier(TierLevel.PREMIUM)
        def premium_feature():
            return "Premium content"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if "user_id" not in session:
                return jsonify({"error": "Authentication required", "upgrade_required": False}), 401

            user = User.query.get(session["user_id"])
            if not user:
                return jsonify({"error": "User not found", "upgrade_required": False}), 404

            # Check tier level
            tier_values = {
                TierLevel.FREE: 0,
                TierLevel.PROFESSIONAL: 1,
                TierLevel.PREMIUM: 2,
                TierLevel.ENTERPRISE: 3,
                TierLevel.ADMIN: 999,
            }

            user_tier_value = tier_values.get(user.tier, 0)
            required_tier_value = tier_values.get(minimum_tier, 0)

            if user_tier_value < required_tier_value:
                return (
                    jsonify(
                        {
                            "error": f"This feature requires {minimum_tier.name} tier or higher",
                            "upgrade_required": True,
                            "current_tier": user.tier.name,
                            "required_tier": minimum_tier.name,
                            "upgrade_url": "/pricing",
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_usage_limit(limit_field, increment=0, hours=None):
    """
    Decorator to check usage limits before allowing access

    Args:
        limit_field: Field name in tier limits (e.g., 'pdf_documents_per_month')
        increment: Amount to increment counter (default 0 = check only)
        hours: For video uploads, the video duration in hours

    Usage:
        @app.route('/api/upload-pdf', methods=['POST'])
        @check_usage_limit('pdf_documents_per_month', increment=1)
        def upload_pdf():
            return "PDF uploaded"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401

            user = User.query.get(session["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 404

            # Get tier limits
            limits = user.get_tier_limits()
            limit = limits.get(limit_field, 0)

            # Get usage tracking
            usage = UsageTracking.get_or_create_current(user.id)

            # Map limit field to usage field
            usage_field_map = {
                "pdf_documents_per_month": "pdf_documents_processed",
                "bwc_videos_per_month": "bwc_videos_processed",
                "bwc_video_hours_per_month": "bwc_video_hours_used",
                "transcription_minutes_per_month": "transcription_minutes_used",
                "api_access": "api_calls_made",
                "case_limit": "cases_created",
            }

            usage_field = usage_field_map.get(limit_field)
            if not usage_field:
                # Unknown limit field, allow access
                print(f"⚠️ Unknown limit field: {limit_field}")
                return f(*args, **kwargs)

            current_usage = getattr(usage, usage_field, 0)

            # -1 means unlimited
            if limit == -1:
                # Increment if needed and proceed
                if increment > 0:
                    usage.increment(usage_field, increment)
                return f(*args, **kwargs)

            # Check if limit would be exceeded
            if limit_field == "bwc_video_hours_per_month" and hours is not None:
                # Check video hours
                if current_usage + hours > limit:
                    return (
                        jsonify(
                            {
                                "error": "Monthly video hours limit exceeded",
                                "limit": limit,
                                "used": current_usage,
                                "remaining": max(0, limit - current_usage),
                                "upgrade_required": True,
                                "upgrade_url": "/pricing",
                            }
                        ),
                        403,
                    )
            else:
                # Check count-based limits
                if current_usage + increment > limit:
                    limit_name = limit_field.replace("_per_month", "").replace("_", " ").title()
                    return (
                        jsonify(
                            {
                                "error": f"Monthly {limit_name} limit exceeded",
                                "limit": limit,
                                "used": current_usage,
                                "remaining": max(0, limit - current_usage),
                                "upgrade_required": True,
                                "current_tier": user.tier.name,
                                "upgrade_url": "/pricing",
                            }
                        ),
                        403,
                    )

            # Increment usage counter
            if increment > 0:
                usage.increment(usage_field, increment)

            # For video hours, increment separately
            if hours is not None and limit_field == "bwc_video_hours_per_month":
                usage.increment("bwc_video_hours_used", hours)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_feature(feature_name):
    """
    Decorator to check if user's tier has access to a specific feature

    Usage:
        @app.route('/api/timeline')
        @require_feature('timeline_builder')
        def timeline():
            return "Timeline feature"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401

            user = User.query.get(session["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 404

            limits = user.get_tier_limits()

            # Check if feature exists and is enabled
            if feature_name not in limits:
                # Feature doesn't exist in tier config, allow access
                return f(*args, **kwargs)

            feature_value = limits.get(feature_name)

            # Check boolean features
            if isinstance(feature_value, bool) and not feature_value:
                return (
                    jsonify(
                        {
                            "error": f"Feature '{feature_name}' not available in your tier",
                            "upgrade_required": True,
                            "current_tier": user.tier.name,
                            "upgrade_url": "/pricing",
                        }
                    ),
                    403,
                )

            # Check string features (e.g., ai_assistant_access)
            if isinstance(feature_value, str):
                if feature_value == "basic":
                    # Feature available but limited
                    request.feature_level = "basic"
                elif feature_value == "full":
                    request.feature_level = "full"
                # Pass through to route handler

            return f(*args, **kwargs)

        return decorated_function

    return decorator


class TierGate:
    """Helper class for tier gating in templates and views"""

    @staticmethod
    def can_access_feature(user, feature_name):
        """Check if user can access a feature"""
        if not user:
            return False

        limits = user.get_tier_limits()
        feature_value = limits.get(feature_name)

        if feature_value is None:
            return False

        if isinstance(feature_value, bool):
            return feature_value

        if isinstance(feature_value, int):
            return feature_value != 0

        if isinstance(feature_value, str):
            return feature_value != "none"

        return True

    @staticmethod
    def get_remaining_usage(user, limit_field):
        """Get remaining usage for a limit"""
        if not user:
            return 0

        limits = user.get_tier_limits()
        limit = limits.get(limit_field, 0)

        if limit == -1:
            return -1  # Unlimited

        usage = UsageTracking.get_or_create_current(user.id)

        usage_field_map = {
            "pdf_documents_per_month": "pdf_documents_processed",
            "bwc_videos_per_month": "bwc_videos_processed",
            "bwc_video_hours_per_month": "bwc_video_hours_used",
            "transcription_minutes_per_month": "transcription_minutes_used",
            "case_limit": "cases_created",
        }

        usage_field = usage_field_map.get(limit_field)
        if not usage_field:
            return 0

        current_usage = getattr(usage, usage_field, 0)
        remaining = max(0, limit - current_usage)

        return remaining

    @staticmethod
    def get_usage_stats(user):
        """Get comprehensive usage statistics for dashboard"""
        if not user:
            return {}

        limits = user.get_tier_limits()
        usage = UsageTracking.get_or_create_current(user.id)

        stats = {
            "tier": user.tier.name,
            "tier_display": user.tier.name.replace("_", " ").title(),
            "is_on_trial": user.is_on_trial if hasattr(user, "is_on_trial") else False,
            "trial_end": (
                user.trial_end.isoformat()
                if hasattr(user, "trial_end") and user.trial_end
                else None
            ),
            "limits": {
                "pdfs": {
                    "limit": limits.get("pdf_documents_per_month", 0),
                    "used": usage.pdf_documents_processed,
                    "remaining": TierGate.get_remaining_usage(user, "pdf_documents_per_month"),
                },
                "videos": {
                    "limit": limits.get("bwc_videos_per_month", 0),
                    "used": usage.bwc_videos_processed,
                    "remaining": TierGate.get_remaining_usage(user, "bwc_videos_per_month"),
                },
                "video_hours": {
                    "limit": limits.get("bwc_video_hours_per_month", 0),
                    "used": round(usage.bwc_video_hours_used, 2),
                    "remaining": TierGate.get_remaining_usage(user, "bwc_video_hours_per_month"),
                },
                "cases": {
                    "limit": limits.get("case_limit", 0),
                    "used": usage.cases_created,
                    "remaining": TierGate.get_remaining_usage(user, "case_limit"),
                },
            },
            "features": {
                "api_access": limits.get("api_access", False),
                "timeline_builder": limits.get("timeline_builder", False),
                "forensic_analysis": limits.get("forensic_analysis", False),
                "priority_support": limits.get("priority_support", False),
                "white_label": limits.get("white_label", False),
                "ai_assistant": limits.get("ai_assistant_access", "none"),
            },
        }

        return stats


def register_tier_gate_helpers(app):
    """Register TierGate helper functions for use in templates"""

    @app.context_processor
    def inject_tier_helpers():
        return {
            "can_access_feature": TierGate.can_access_feature,
            "get_remaining_usage": TierGate.get_remaining_usage,
            "get_usage_stats": TierGate.get_usage_stats,
        }


# ============================================
# Helper functions for API modules
# ============================================


def check_tier_access(feature_name):
    """
    Decorator to check if user has access to a feature

    Args:
        feature_name: Name of the feature to check (e.g., 'ai_analysis')

    Usage:
        @check_tier_access("ai_analysis")
        def my_route():
            pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user

            # Check if user is logged in
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401

            # Get user's tier limits
            limits = current_user.get_tier_limits()

            # Check if feature exists and is enabled
            feature_value = limits.get(feature_name)

            if feature_value is None:
                # Feature not defined, allow access
                return f(*args, **kwargs)

            # Check boolean features
            if isinstance(feature_value, bool) and not feature_value:
                return (
                    jsonify(
                        {
                            "error": f"Feature '{feature_name}' not available in your tier",
                            "upgrade_required": True,
                            "current_tier": current_user.tier.name,
                            "upgrade_url": "/pricing",
                        }
                    ),
                    403,
                )

            # Check numeric features (0 = disabled)
            if isinstance(feature_value, (int, float)) and feature_value == 0:
                return (
                    jsonify(
                        {
                            "error": f"Feature '{feature_name}' not available in your tier",
                            "upgrade_required": True,
                            "current_tier": current_user.tier.name,
                            "upgrade_url": "/pricing",
                        }
                    ),
                    403,
                )

            # Check string features ("none" = disabled)
            if isinstance(feature_value, str) and feature_value.lower() == "none":
                return (
                    jsonify(
                        {
                            "error": f"Feature '{feature_name}' not available in your tier",
                            "upgrade_required": True,
                            "current_tier": current_user.tier.name,
                            "upgrade_url": "/pricing",
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_tier_limits(user=None):
    """
    Get tier limits for a user

    Args:
        user: User object (optional, uses current_user if not provided)

    Returns:
        dict: Tier limits dictionary
    """
    if user is None:
        from flask_login import current_user

        if current_user.is_authenticated:
            user = current_user

    if not user or not hasattr(user, "get_tier_limits"):
        # Return basic free tier limits
        return {
            "bwc_videos_per_month": 1,
            "bwc_video_hours_per_month": 1,
            "document_pages_per_month": 5,
            "transcription_minutes_per_month": 10,
            "storage_gb": 1,
            "search_queries_per_month": 50,
            "ai_requests_per_month": 10,
            "case_limit": 2,
        }

    return user.get_tier_limits()


def get_user_tier(user=None):
    """
    Get user's tier level

    Args:
        user: User object (optional, uses current_user if not provided)

    Returns:
        TierLevel enum value
    """
    if user is None:
        from flask_login import current_user

        if current_user.is_authenticated:
            user = current_user

    if not user or not hasattr(user, "tier"):
        return TierLevel.FREE

    return user.tier
