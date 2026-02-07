# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident UX Enhancement Utilities
Helper functions and filters for improved user experience
"""

from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user


def format_number(value):
    """Format numbers with thousands separator"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


def format_file_size(bytes_size):
    """Format bytes to human-readable size"""
    try:
        bytes_size = float(bytes_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    except (ValueError, TypeError):
        return "0 B"


def format_duration(seconds):
    """Format seconds to human-readable duration"""
    try:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except (ValueError, TypeError):
        return "0s"


def tier_color(tier_name):
    """Get color class for tier badge"""
    colors = {
        "FREE": "#6b7280",
        "PROFESSIONAL": "#3b82f6",
        "PREMIUM": "#7c3aed",
        "ENTERPRISE": "#0a0a0f",
        "ADMIN": "#c41e3a",
    }
    return colors.get(tier_name.upper(), "#6b7280")


def usage_percentage(current, limit):
    """Calculate usage percentage"""
    try:
        if limit == -1:  # Unlimited
            return 0
        if limit == 0:
            return 100
        return min(int((current / limit) * 100), 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


def usage_status(current, limit):
    """Get usage status: healthy, warning, or critical"""
    percentage = usage_percentage(current, limit)

    if limit == -1:
        return "unlimited"
    elif percentage >= 90:
        return "critical"
    elif percentage >= 75:
        return "warning"
    else:
        return "healthy"


def tier_upgrade_suggestion(current_tier):
    """Get suggested upgrade tier"""
    tiers = {
        "FREE": "PROFESSIONAL",
        "PROFESSIONAL": "PREMIUM",
        "PREMIUM": "ENTERPRISE",
        "ENTERPRISE": None,
        "ADMIN": None,
    }
    return tiers.get(current_tier.upper())


def tier_pricing(tier_name):
    """Get tier monthly price"""
    prices = {"FREE": 0, "PROFESSIONAL": 49, "PREMIUM": 199, "ENTERPRISE": 499, "ADMIN": 0}
    return prices.get(tier_name.upper(), 0)


def tier_features(tier_name):
    """Get list of tier features"""
    features = {
        "FREE": [
            "2 BWC videos per month",
            "50 document pages",
            "30 minutes transcription",
            "100 search queries",
            "500 MB storage",
            "Basic support",
        ],
        "PROFESSIONAL": [
            "25 BWC videos per month",
            "1,000 document pages",
            "600 minutes transcription",
            "Unlimited searches",
            "25 GB storage",
            "No watermarks",
            "Multi-BWC sync",
            "Priority support",
        ],
        "PREMIUM": [
            "100 BWC videos per month",
            "10,000 document pages",
            "3,000 minutes transcription",
            "Unlimited searches",
            "250 GB storage",
            "API access",
            "Forensic analysis",
            "Advanced tools",
            "Premium support",
        ],
        "ENTERPRISE": [
            "Unlimited BWC videos",
            "Unlimited documents",
            "Unlimited transcription",
            "1 TB storage",
            "Full API access",
            "White-label options",
            "Custom integrations",
            "Dedicated support",
            "SLA guarantee",
        ],
    }
    return features.get(tier_name.upper(), [])


def contextual_help(page_name, tier_name):
    """Get contextual help text for page and tier"""
    help_texts = {
        "dashboard": {
            "FREE": "Track your usage and upgrade when you need more capacity.",
            "PROFESSIONAL": "You have access to professional-grade tools and analytics.",
            "PREMIUM": "Full forensic analysis suite at your fingertips.",
            "ENTERPRISE": "Unlimited access to all Evident features.",
        },
        "upload": {
            "FREE": "Upload BWC videos up to 100 MB. Upgrade for larger files.",
            "PROFESSIONAL": "Upload BWC videos up to 500 MB.",
            "PREMIUM": "Upload BWC videos up to 2 GB.",
            "ENTERPRISE": "Upload BWC videos up to 10 GB.",
        },
        "analysis": {
            "FREE": "Basic analysis with automated transcription.",
            "PROFESSIONAL": "Enhanced analysis with speaker diarization.",
            "PREMIUM": "Full forensic analysis with discrepancy detection.",
            "ENTERPRISE": "Custom analysis workflows and advanced tools.",
        },
    }

    page_help = help_texts.get(page_name, {})
    return page_help.get(tier_name.upper(), "Learn more about this feature.")


def flash_tier_limit(feature_name):
    """Flash message about tier limit reached"""
    flash(
        f"You've reached your tier limit for {feature_name}. "
        f'<a href="/pricing">Upgrade your account</a> to continue.',
        "warning",
    )


def flash_success_with_action(message, action_url, action_text):
    """Flash success message with action button"""
    flash(f'{message} <a href="{action_url}" class="flash-action-btn">{action_text}</a>', "success")


def requires_feature(feature_name):
    """Decorator to check if user has access to feature"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this feature.", "info")
                return redirect(url_for("auth.login", next=request.url))

            if not hasattr(current_user, "can_access_feature"):
                # Fallback if enhanced auth not available
                return f(*args, **kwargs)

            if not current_user.can_access_feature(feature_name):
                flash(
                    "This feature requires a higher tier. "
                    '<a href="/pricing">View upgrade options</a>',
                    "warning",
                )
                return redirect(url_for("dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_welcome_message(tier_name, is_new_user=False):
    """Get personalized welcome message"""
    if is_new_user:
        messages = {
            "FREE": "🎉 Welcome to Evident! Start with 2 free BWC analyses.",
            "PROFESSIONAL": "🚀 Welcome to Professional! You have 25 analyses ready.",
            "PREMIUM": "⭐ Welcome to Premium! Unlimited power at your fingertips.",
            "ENTERPRISE": "👑 Welcome to Enterprise! Your custom solution awaits.",
        }
    else:
        messages = {
            "FREE": "Welcome back! You have analyses remaining this month.",
            "PROFESSIONAL": "Welcome back, Professional!",
            "PREMIUM": "Welcome back, Premium user!",
            "ENTERPRISE": "Welcome back! Your Enterprise account is ready.",
        }

    return messages.get(tier_name.upper(), "Welcome to Evident!")


def register_ux_filters(app):
    """Register all UX helper filters with Flask app"""
    app.jinja_env.filters["format_number"] = format_number
    app.jinja_env.filters["format_file_size"] = format_file_size
    app.jinja_env.filters["format_duration"] = format_duration
    app.jinja_env.filters["tier_color"] = tier_color
    app.jinja_env.filters["usage_percentage"] = usage_percentage
    app.jinja_env.filters["usage_status"] = usage_status
    app.jinja_env.filters["tier_pricing"] = tier_pricing

    # Add context processors for global template variables
    @app.context_processor
    def inject_ux_helpers():
        return {
            "tier_features": tier_features,
            "tier_upgrade_suggestion": tier_upgrade_suggestion,
            "contextual_help": contextual_help,
            "get_welcome_message": get_welcome_message,
        }
