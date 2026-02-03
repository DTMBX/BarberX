"""
AI-Powered Login Security System
Anomaly detection, device fingerprinting, and threat analysis
"""

import hashlib
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from flask import request
from pyod.models.iforest import IForest
from pyod.models.lof import LOF

from models_auth import db


class LoginSecurityManager:
    """AI-powered login security with anomaly detection"""

    def __init__(self, model_path="models/login_detector.pkl"):
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.detector = None
        self.load_or_create_model()

    def load_or_create_model(self):
        """Load existing model or create new one"""
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    self.detector = pickle.load(f)
                print("[OK] Login security model loaded")
            except Exception as e:
                print(f"[WARN] Could not load model: {e}, creating new one")
                self.detector = IForest(contamination=0.05, random_state=42)
        else:
            self.detector = IForest(contamination=0.05, random_state=42)
            print("[OK] New login security model created")

    def save_model(self):
        """Save trained model to disk"""
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.detector, f)
            print("[OK] Login security model saved")
        except Exception as e:
            print(f"[ERROR] Could not save model: {e}")

    def extract_login_features(self, user_id=None, email=None):
        """Extract features from current request for anomaly detection"""
        import user_agents
        from flask import request

        # Parse user agent
        ua_string = request.headers.get("User-Agent", "")
        ua = user_agents.parse(ua_string)

        # Time features
        now = datetime.utcnow()
        hour_of_day = now.hour
        day_of_week = now.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        is_night = 1 if hour_of_day < 6 or hour_of_day > 22 else 0

        # Device features
        is_mobile = 1 if ua.is_mobile else 0
        is_tablet = 1 if ua.is_tablet else 0
        is_pc = 1 if ua.is_pc else 0
        is_bot = 1 if ua.is_bot else 0

        # Browser features
        browser_hash = hashlib.md5(str(ua.browser.family).encode()).hexdigest()
        browser_numeric = int(browser_hash[:8], 16) % 1000 / 1000.0

        # OS features
        os_hash = hashlib.md5(str(ua.os.family).encode()).hexdigest()
        os_numeric = int(os_hash[:8], 16) % 1000 / 1000.0

        # IP-based features (simplified)
        ip = request.remote_addr or "0.0.0.0"
        ip_hash = hashlib.md5(ip.encode()).hexdigest()
        ip_numeric = int(ip_hash[:8], 16) % 1000 / 1000.0

        # Referrer features
        referrer = request.referrer or ""
        has_referrer = 1 if referrer else 0

        features = [
            hour_of_day / 24.0,  # Normalize to 0-1
            day_of_week / 7.0,
            is_weekend,
            is_night,
            is_mobile,
            is_tablet,
            is_pc,
            is_bot,
            browser_numeric,
            os_numeric,
            ip_numeric,
            has_referrer,
        ]

        return np.array(features)

    def get_device_fingerprint(self):
        """Generate device fingerprint from request"""
        import user_agents

        ua_string = request.headers.get("User-Agent", "")
        ua = user_agents.parse(ua_string)
        ip = request.remote_addr or "0.0.0.0"

        # Create fingerprint from multiple factors
        fingerprint_data = {
            "ip": ip,
            "browser": ua.browser.family,
            "browser_version": ua.browser.version_string,
            "os": ua.os.family,
            "os_version": ua.os.version_string,
            "device": ua.device.family,
        }

        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    def check_login_anomaly(self, user_id=None, email=None):
        """
        Check if current login attempt is anomalous

        Returns:
            tuple: (is_suspicious: bool, anomaly_score: float, reason: str)
        """
        features = self.extract_login_features(user_id, email)

        # If model not trained yet, allow login but flag for training
        if not hasattr(self.detector, "decision_scores_"):
            return False, 0.0, "Model not trained yet"

        try:
            # Get anomaly score (higher = more anomalous)
            anomaly_score = self.detector.decision_function([features])[0]

            # Normalize score to 0-1 range
            normalized_score = min(max(anomaly_score, 0), 1)

            # Determine if suspicious (threshold: 0.75)
            is_suspicious = normalized_score > 0.75

            reason = ""
            if is_suspicious:
                # Identify which features contributed most
                if features[3] == 1:  # is_night
                    reason += "Unusual time (night), "
                if features[7] == 1:  # is_bot
                    reason += "Bot detected, "
                if features[0] < 0.2 or features[0] > 0.9:  # hour extremes
                    reason += "Unusual hour, "

                reason = reason.rstrip(", ") or "Anomalous pattern detected"

            return is_suspicious, normalized_score, reason

        except Exception as e:
            print(f"[ERROR] Anomaly detection failed: {e}")
            return False, 0.0, "Detection error"

    def train_on_historical_data(self, login_events):
        """
        Train model on historical login data

        Args:
            login_events: List of dicts with keys: user_id, timestamp, ip, user_agent, success
        """
        if not login_events or len(login_events) < 10:
            print("[WARN] Not enough data to train (need at least 10 events)")
            return False

        # Extract features from historical events
        features_list = []

        for event in login_events:
            # Simulate request context for feature extraction
            hour = event.get("hour", 12)
            day_of_week = event.get("day_of_week", 0)
            is_mobile = event.get("is_mobile", 0)
            is_bot = event.get("is_bot", 0)

            features = [
                hour / 24.0,
                day_of_week / 7.0,
                1 if day_of_week >= 5 else 0,  # is_weekend
                1 if hour < 6 or hour > 22 else 0,  # is_night
                is_mobile,
                0,  # is_tablet
                1 - is_mobile,  # is_pc
                is_bot,
                0.5,  # browser_numeric (placeholder)
                0.5,  # os_numeric (placeholder)
                0.5,  # ip_numeric (placeholder)
                1,  # has_referrer
            ]
            features_list.append(features)

        X = np.array(features_list)

        try:
            self.detector.fit(X)
            self.save_model()
            print(f"[OK] Model trained on {len(login_events)} events")
            return True
        except Exception as e:
            print(f"[ERROR] Training failed: {e}")
            return False

    def get_risk_score(self, user_id=None, email=None):
        """Get comprehensive risk score (0-100, higher = riskier)"""
        is_suspicious, anomaly_score, reason = self.check_login_anomaly(user_id, email)

        risk_score = int(anomaly_score * 100)

        risk_factors = []
        if is_suspicious:
            risk_factors.append(reason)

        # Check device fingerprint
        fingerprint = self.get_device_fingerprint()

        return {
            "risk_score": risk_score,
            "is_suspicious": is_suspicious,
            "anomaly_score": round(anomaly_score, 3),
            "risk_factors": risk_factors,
            "device_fingerprint": fingerprint,
            "recommendation": self._get_recommendation(risk_score),
        }

    def _get_recommendation(self, risk_score):
        """Get security recommendation based on risk score"""
        if risk_score < 30:
            return "allow"
        elif risk_score < 60:
            return "monitor"
        elif risk_score < 80:
            return "challenge"  # Require email verification
        else:
            return "block"  # Temporary block, require admin review


# Global instance
login_security = LoginSecurityManager()


def check_login_security(user_id=None, email=None):
    """
    Convenience function to check login security

    Returns:
        dict: Risk assessment with recommendation
    """
    return login_security.get_risk_score(user_id, email)
