"""
User Analytics and Retention Tracking
PostHog, Amplitude, and Prophet-based churn prediction
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

# PostHog integration
try:
    import posthog

    posthog.api_key = os.getenv("POSTHOG_API_KEY")
    posthog.host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    POSTHOG_AVAILABLE = bool(posthog.api_key)
    if POSTHOG_AVAILABLE:
        print("[OK] PostHog analytics enabled")
except ImportError:
    POSTHOG_AVAILABLE = False
    print("[WARN] PostHog not available - install with: pip install posthog")

# Amplitude integration
try:
    from amplitude import Amplitude, BaseEvent

    amplitude_key = os.getenv("AMPLITUDE_API_KEY")
    if amplitude_key:
        amplitude_client = Amplitude(amplitude_key)
        AMPLITUDE_AVAILABLE = True
        print("[OK] Amplitude analytics enabled")
    else:
        AMPLITUDE_AVAILABLE = False
except ImportError:
    AMPLITUDE_AVAILABLE = False
    print("[WARN] Amplitude not available - install with: pip install amplitude-analytics")


class UserAnalytics:
    """Track user behavior and engagement"""

    @staticmethod
    def track_event(user_id: int, event_name: str, properties: Dict[str, Any] = None):
        """Track event to all available analytics platforms"""
        properties = properties or {}
        properties["timestamp"] = datetime.utcnow().isoformat()

        # PostHog
        if POSTHOG_AVAILABLE:
            try:
                posthog.capture(distinct_id=str(user_id), event=event_name, properties=properties)
            except Exception as e:
                print(f"[ERROR] PostHog tracking failed: {e}")

        # Amplitude
        if AMPLITUDE_AVAILABLE:
            try:
                event = BaseEvent(
                    event_type=event_name, user_id=str(user_id), event_properties=properties
                )
                amplitude_client.track(event)
            except Exception as e:
                print(f"[ERROR] Amplitude tracking failed: {e}")

    @staticmethod
    def identify_user(user_id: int, traits: Dict[str, Any]):
        """Identify user with traits"""
        # PostHog
        if POSTHOG_AVAILABLE:
            try:
                posthog.identify(distinct_id=str(user_id), properties=traits)
            except Exception as e:
                print(f"[ERROR] PostHog identify failed: {e}")

        # Amplitude
        if AMPLITUDE_AVAILABLE:
            try:
                from amplitude import Identify

                identify_obj = Identify()
                for key, value in traits.items():
                    identify_obj.set(key, value)
                amplitude_client.identify(identify_obj, str(user_id))
            except Exception as e:
                print(f"[ERROR] Amplitude identify failed: {e}")

    @staticmethod
    def track_login(user_id: int, success: bool, tier: str, device: str = None):
        """Track login event"""
        event_name = "Login Success" if success else "Login Failed"

        UserAnalytics.track_event(
            user_id, event_name, {"tier": tier, "device": device, "success": success}
        )

    @staticmethod
    def track_signup(user_id: int, tier: str, source: str = None):
        """Track signup event"""
        UserAnalytics.track_event(
            user_id, "User Signed Up", {"tier": tier, "source": source or "direct"}
        )

        # Identify user
        UserAnalytics.identify_user(
            user_id,
            {
                "tier": tier,
                "signup_date": datetime.utcnow().isoformat(),
                "signup_source": source or "direct",
            },
        )

    @staticmethod
    def track_tier_upgrade(user_id: int, old_tier: str, new_tier: str, revenue: float = None):
        """Track subscription tier change"""
        UserAnalytics.track_event(
            user_id,
            "Subscription Upgraded",
            {"old_tier": old_tier, "new_tier": new_tier, "revenue": revenue},
        )

        # Update user traits
        UserAnalytics.identify_user(
            user_id, {"tier": new_tier, "last_upgrade": datetime.utcnow().isoformat()}
        )

    @staticmethod
    def track_feature_usage(user_id: int, feature: str, tier: str):
        """Track feature usage"""
        UserAnalytics.track_event(
            user_id, f"Feature Used: {feature}", {"feature": feature, "tier": tier}
        )

    @staticmethod
    def track_churn_risk(user_id: int, risk_score: float, reasons: list):
        """Track churn risk prediction"""
        UserAnalytics.track_event(
            user_id, "Churn Risk Detected", {"risk_score": risk_score, "reasons": reasons}
        )


class ChurnPredictor:
    """Predict user churn using activity patterns"""

    def __init__(self):
        self.churn_threshold = 0.7  # 70% probability

    def predict_churn(self, user_activity: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict churn probability based on user activity

        Args:
            user_activity: DataFrame with columns ['date', 'login_count', 'feature_usage']

        Returns:
            dict with churn_probability, risk_level, and recommendations
        """
        if len(user_activity) < 7:
            return {
                "churn_probability": 0.0,
                "risk_level": "unknown",
                "message": "Not enough data for prediction",
            }

        # Calculate engagement metrics
        recent_days = 7
        recent_activity = user_activity.tail(recent_days)

        # Metrics
        avg_daily_logins = recent_activity["login_count"].mean()
        login_trend = recent_activity["login_count"].diff().mean()
        days_inactive = (datetime.now() - pd.to_datetime(recent_activity["date"].iloc[-1])).days

        # Simple churn probability calculation
        churn_score = 0.0

        # Low login frequency
        if avg_daily_logins < 0.5:
            churn_score += 0.3

        # Declining trend
        if login_trend < 0:
            churn_score += 0.2

        # Days inactive
        if days_inactive > 3:
            churn_score += 0.3
        elif days_inactive > 7:
            churn_score += 0.5

        # Determine risk level
        if churn_score < 0.3:
            risk_level = "low"
        elif churn_score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Generate recommendations
        recommendations = []
        if days_inactive > 3:
            recommendations.append("Send re-engagement email")
        if avg_daily_logins < 0.5:
            recommendations.append("Highlight unused features")
        if login_trend < 0:
            recommendations.append("Offer support or tutorial")

        return {
            "churn_probability": min(churn_score, 1.0),
            "risk_level": risk_level,
            "days_inactive": days_inactive,
            "avg_daily_logins": avg_daily_logins,
            "recommendations": recommendations,
        }

    def get_user_activity_from_db(self, user_id: int, days: int = 30) -> pd.DataFrame:
        """Get user activity from database"""
        from sqlalchemy import func

        from models_auth import User
        from usage_meter import SmartMeterEvent

        since = datetime.utcnow() - timedelta(days=days)

        # Query login events grouped by date
        results = (
            SmartMeterEvent.query.filter(
                SmartMeterEvent.user_id == user_id,
                SmartMeterEvent.event_type == "login",
                SmartMeterEvent.timestamp >= since,
            )
            .with_entities(
                func.date(SmartMeterEvent.timestamp).label("date"),
                func.count().label("login_count"),
            )
            .group_by(func.date(SmartMeterEvent.timestamp))
            .all()
        )

        # Convert to DataFrame
        df = pd.DataFrame([{"date": r.date, "login_count": r.login_count} for r in results])

        if df.empty:
            # No activity data
            return pd.DataFrame({"date": [], "login_count": [], "feature_usage": []})

        # Fill missing dates with 0
        date_range = pd.date_range(start=since.date(), end=datetime.now().date(), freq="D")
        df_full = pd.DataFrame({"date": date_range})
        df_full = df_full.merge(df, on="date", how="left")
        df_full["login_count"] = df_full["login_count"].fillna(0)
        df_full["feature_usage"] = 0  # TODO: Calculate from actual feature events

        return df_full


class RetentionTracker:
    """Track and analyze user retention"""

    @staticmethod
    def calculate_retention_cohort(signup_date: datetime, user_id: int) -> Dict[str, Any]:
        """Calculate retention metrics for user cohort"""
        from usage_meter import SmartMeterEvent

        # Get login events
        logins = (
            SmartMeterEvent.query.filter(
                SmartMeterEvent.user_id == user_id,
                SmartMeterEvent.event_type == "login",
                SmartMeterEvent.status == "success",
            )
            .order_by(SmartMeterEvent.timestamp)
            .all()
        )

        if not logins:
            return {"day_1": False, "day_7": False, "day_30": False, "total_logins": 0}

        # Check retention milestones
        day_1_login = any((l.timestamp.date() - signup_date.date()).days == 1 for l in logins)
        day_7_login = any((l.timestamp.date() - signup_date.date()).days <= 7 for l in logins)
        day_30_login = any((l.timestamp.date() - signup_date.date()).days <= 30 for l in logins)

        return {
            "day_1": day_1_login,
            "day_7": day_7_login,
            "day_30": day_30_login,
            "total_logins": len(logins),
            "last_login": logins[-1].timestamp.isoformat() if logins else None,
        }


# Global instances
analytics = UserAnalytics()
churn_predictor = ChurnPredictor()
retention_tracker = RetentionTracker()
