"""
User Analytics & Retention System
PostHog integration, churn prediction, and engagement tracking
"""

import os
from datetime import datetime, timedelta

import posthog

# Initialize PostHog (optional - only if API key is set)
POSTHOG_ENABLED = False
if os.getenv("POSTHOG_API_KEY"):
    posthog.api_key = os.getenv("POSTHOG_API_KEY")
    posthog.host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    POSTHOG_ENABLED = True
    print("[OK] PostHog analytics enabled")
else:
    print("[INFO] PostHog not configured (set POSTHOG_API_KEY to enable)")


class UserAnalytics:
    """Track user behavior and predict churn"""

    @staticmethod
    def track_event(user_id, event_name, properties=None):
        """
        Track user event

        Args:
            user_id: User ID
            event_name: Event name (e.g., "Login Success", "Feature Used")
            properties: Dict of event properties
        """
        if not POSTHOG_ENABLED:
            return

        try:
            posthog.capture(
                distinct_id=str(user_id),
                event=event_name,
                properties=properties or {},
            )
        except Exception as e:
            print(f"[ERROR] PostHog tracking failed: {e}")

    @staticmethod
    def identify_user(user_id, traits=None):
        """
        Identify user with traits

        Args:
            user_id: User ID
            traits: Dict of user traits (email, tier, signup_date, etc.)
        """
        if not POSTHOG_ENABLED:
            return

        try:
            posthog.identify(distinct_id=str(user_id), properties=traits or {})
        except Exception as e:
            print(f"[ERROR] PostHog identify failed: {e}")

    @staticmethod
    def track_login(user, success=True, method="password", risk_score=0):
        """Track login event with security context"""
        event_name = "Login Success" if success else "Login Failed"

        UserAnalytics.track_event(
            user.id if user else None,
            event_name,
            {
                "method": method,
                "tier": user.tier.name if user else "unknown",
                "risk_score": risk_score,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @staticmethod
    def track_signup(user, tier="FREE"):
        """Track new user signup"""
        UserAnalytics.identify_user(
            user.id,
            {
                "email": user.email,
                "tier": tier,
                "signup_date": datetime.utcnow().isoformat(),
                "full_name": user.full_name,
            },
        )

        UserAnalytics.track_event(
            user.id,
            "User Signed Up",
            {
                "tier": tier,
                "email_verified": user.email_verified,
            },
        )

    @staticmethod
    def track_feature_usage(user, feature_name, metadata=None):
        """Track feature usage for engagement analysis"""
        UserAnalytics.track_event(
            user.id,
            f"Feature Used: {feature_name}",
            {
                "feature": feature_name,
                "tier": user.tier.name,
                **(metadata or {}),
            },
        )

    @staticmethod
    def predict_churn_risk(user):
        """
        Predict churn risk based on activity patterns

        Returns:
            dict: {
                'risk_level': 'low' | 'medium' | 'high',
                'risk_score': 0-100,
                'factors': [list of risk factors],
                'recommendation': str
            }
        """
        from models_auth import UsageQuota

        # Get user's activity
        quota = UsageQuota.query.filter_by(user_id=user.id).first()

        risk_factors = []
        risk_score = 0

        # Check last login
        if user.last_login:
            days_since_login = (datetime.utcnow() - user.last_login).days

            if days_since_login > 30:
                risk_score += 40
                risk_factors.append(f"No login for {days_since_login} days")
            elif days_since_login > 14:
                risk_score += 20
                risk_factors.append(f"Last login {days_since_login} days ago")

        else:
            risk_score += 30
            risk_factors.append("Never logged in after signup")

        # Check usage levels
        if quota:
            # Check AI usage
            if quota.ai_requests_count == 0:
                risk_score += 15
                risk_factors.append("No AI features used")

            # Check file uploads
            if quota.files_uploaded_count == 0:
                risk_score += 10
                risk_factors.append("No files uploaded")

            # Check storage usage (low engagement indicator)
            if quota.storage_bytes_used == 0:
                risk_score += 5
                risk_factors.append("No data stored")

        # Determine risk level
        if risk_score < 30:
            risk_level = "low"
            recommendation = "User is engaged, maintain current experience"
        elif risk_score < 60:
            risk_level = "medium"
            recommendation = "Send engagement email with feature highlights"
        else:
            risk_level = "high"
            recommendation = "Trigger retention campaign, offer assistance"

        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 100),
            "factors": risk_factors,
            "recommendation": recommendation,
            "days_since_login": (
                (datetime.utcnow() - user.last_login).days if user.last_login else None
            ),
        }


# Convenience functions
def track_login(user, success=True, method="password", risk_score=0):
    """Track login event"""
    UserAnalytics.track_login(user, success, method, risk_score)


def track_signup(user, tier="FREE"):
    """Track signup event"""
    UserAnalytics.track_signup(user, tier)


def track_feature(user, feature_name, metadata=None):
    """Track feature usage"""
    UserAnalytics.track_feature_usage(user, feature_name, metadata)


def check_churn_risk(user):
    """Check if user is at risk of churning"""
    return UserAnalytics.predict_churn_risk(user)
