"""
AI-Powered Security Module for Evident
Anomaly detection, fraud prevention, and intelligent session management
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from flask import request
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from redis import Redis

# Initialize Redis for session management
try:
    redis_client = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )
    redis_available = redis_client.ping()
except Exception as e:
    print(f"[WARN] Redis not available: {e}")
    redis_available = False
    redis_client = None


class LoginAnomalyDetector:
    """Detect anomalous login patterns using ML"""

    def __init__(self):
        self.model = IForest(contamination=0.05, random_state=42)
        self.model_path = Path("ai_models/login_anomaly_detector.pkl")
        self.is_trained = False

        # Load model if exists
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                print("[OK] Login anomaly detector loaded")
            except Exception as e:
                print(f"[WARN] Could not load anomaly detector: {e}")

    def extract_features(self, request_obj, user=None):
        """Extract features from login request"""
        # Time-based features
        now = datetime.now()
        hour_of_day = now.hour
        day_of_week = now.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        is_night = 1 if hour_of_day < 6 or hour_of_day > 22 else 0

        # User agent parsing
        user_agent = request_obj.user_agent.string
        is_mobile = 1 if request_obj.user_agent.platform in ["android", "iphone", "ipad"] else 0

        # IP-based features (simplified)
        ip_address = request_obj.remote_addr or "0.0.0.0"
        ip_parts = ip_address.split(".")
        ip_first_octet = int(ip_parts[0]) if len(ip_parts) >= 1 else 0

        # User history features
        if user and redis_available:
            login_count = int(redis_client.get(f"user:{user.id}:login_count") or 0)
            last_login_hour = int(redis_client.get(f"user:{user.id}:last_hour") or hour_of_day)
            hour_diff = abs(hour_of_day - last_login_hour)
        else:
            login_count = 0
            hour_diff = 0

        features = [
            hour_of_day,
            day_of_week,
            is_weekend,
            is_night,
            is_mobile,
            ip_first_octet,
            login_count,
            hour_diff,
        ]

        return np.array(features).reshape(1, -1)

    def train(self, login_data):
        """Train the anomaly detector on historical login data"""
        if len(login_data) < 10:
            print("[WARN] Not enough data to train anomaly detector (need >= 10 samples)")
            return False

        X = np.array(login_data)
        self.model.fit(X)
        self.is_trained = True

        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

        print(f"[OK] Login anomaly detector trained on {len(login_data)} samples")
        return True

    def detect_anomaly(self, features):
        """Detect if login attempt is anomalous"""
        if not self.is_trained:
            # Not trained yet, allow all logins
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "risk_level": "unknown",
                "message": "Detector not trained yet",
            }

        # Get anomaly score (higher = more anomalous)
        score = self.model.decision_function(features)[0]
        prediction = self.model.predict(features)[0]

        # Normalize score to 0-1 range
        normalized_score = min(max((score + 0.5) / 1.0, 0), 1)

        # Determine risk level
        if normalized_score < 0.3:
            risk_level = "low"
        elif normalized_score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "is_anomaly": bool(prediction == 1),
            "anomaly_score": float(normalized_score),
            "risk_level": risk_level,
            "message": f"Login risk: {risk_level} ({normalized_score:.2%})",
        }

    def update_user_history(self, user_id):
        """Update user login history in Redis"""
        if not redis_available:
            return

        now = datetime.now()

        # Increment login count
        redis_client.incr(f"user:{user_id}:login_count")

        # Store last login hour
        redis_client.set(f"user:{user_id}:last_hour", now.hour)

        # Store last login timestamp
        redis_client.set(f"user:{user_id}:last_login", now.isoformat())


class RateLimiter:
    """Intelligent rate limiting with Redis"""

    def __init__(self):
        self.enabled = redis_available

    def check_rate_limit(self, key, max_attempts=5, window_seconds=300):
        """Check if key has exceeded rate limit"""
        if not self.enabled:
            return True, 0  # Allow if Redis not available

        current = redis_client.incr(key)

        if current == 1:
            # First attempt, set expiry
            redis_client.expire(key, window_seconds)

        ttl = redis_client.ttl(key)

        if current > max_attempts:
            return False, ttl  # Rate limit exceeded

        return True, ttl

    def get_attempts(self, key):
        """Get current attempt count"""
        if not self.enabled:
            return 0
        return int(redis_client.get(key) or 0)


class DeviceFingerprint:
    """Track and fingerprint devices"""

    def __init__(self):
        self.enabled = redis_available

    def generate_fingerprint(self, request_obj):
        """Generate device fingerprint from request"""
        components = [
            request_obj.user_agent.string,
            request_obj.accept_languages.to_header() if request_obj.accept_languages else "",
            request_obj.accept_charsets.to_header() if request_obj.accept_charsets else "",
        ]

        fingerprint_str = "|".join(components)

        # Simple hash
        import hashlib

        fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

        return fingerprint

    def is_known_device(self, user_id, fingerprint):
        """Check if device is known for this user"""
        if not self.enabled:
            return True  # Assume known if Redis not available

        key = f"user:{user_id}:devices"
        known_devices = redis_client.smembers(key)

        return fingerprint in known_devices

    def register_device(self, user_id, fingerprint):
        """Register device for user"""
        if not self.enabled:
            return

        key = f"user:{user_id}:devices"
        redis_client.sadd(key, fingerprint)
        redis_client.expire(key, 86400 * 90)  # 90 days


# Global instances
anomaly_detector = LoginAnomalyDetector()
rate_limiter = RateLimiter()
device_tracker = DeviceFingerprint()


def check_login_security(request_obj, user=None, email=None):
    """
    Comprehensive security check for login attempt

    Returns:
        dict: {
            'allowed': bool,
            'risk_score': float,
            'alerts': list,
            'require_mfa': bool
        }
    """
    alerts = []
    risk_score = 0.0
    require_mfa = False

    # 1. Rate limiting check
    identifier = email or request_obj.remote_addr
    rate_key = f"login_attempts:{identifier}"
    allowed, ttl = rate_limiter.check_rate_limit(rate_key, max_attempts=5, window_seconds=300)

    if not allowed:
        return {
            "allowed": False,
            "risk_score": 1.0,
            "alerts": [f"Too many login attempts. Try again in {ttl} seconds."],
            "require_mfa": False,
        }

    # 2. Anomaly detection
    features = anomaly_detector.extract_features(request_obj, user)
    anomaly_result = anomaly_detector.detect_anomaly(features)

    risk_score = anomaly_result["anomaly_score"]

    if anomaly_result["risk_level"] == "high":
        alerts.append("Unusual login pattern detected")
        require_mfa = True
    elif anomaly_result["risk_level"] == "medium":
        alerts.append("Login from unusual location/time")

    # 3. Device fingerprinting
    if user:
        fingerprint = device_tracker.generate_fingerprint(request_obj)
        is_known = device_tracker.is_known_device(user.id, fingerprint)

        if not is_known:
            alerts.append("Login from new device")
            require_mfa = True
            risk_score = max(risk_score, 0.6)

    # 4. Time-based checks
    now = datetime.now()
    if now.hour < 5 or now.hour > 23:
        alerts.append("Login during unusual hours")
        risk_score += 0.2

    return {
        "allowed": True,
        "risk_score": min(risk_score, 1.0),
        "alerts": alerts,
        "require_mfa": require_mfa,
    }


def train_anomaly_detector_from_db():
    """Train anomaly detector using historical login data from database"""
    from models_auth import User, db
    from usage_meter import SmartMeterEvent

    print("\n[AI] Training login anomaly detector...")

    # Get historical login events
    login_events = (
        SmartMeterEvent.query.filter(
            SmartMeterEvent.event_type == "login", SmartMeterEvent.status == "success"
        )
        .limit(1000)
        .all()
    )

    if len(login_events) < 10:
        print(f"[WARN] Not enough login data ({len(login_events)} events). Need at least 10.")
        return False

    # Extract features from historical logins
    training_data = []

    for event in login_events:
        # Reconstruct features from event metadata
        metadata = event.metadata or {}

        # Parse timestamp
        timestamp = event.timestamp

        features = [
            timestamp.hour,  # hour_of_day
            timestamp.weekday(),  # day_of_week
            1 if timestamp.weekday() >= 5 else 0,  # is_weekend
            1 if timestamp.hour < 6 or timestamp.hour > 22 else 0,  # is_night
            int(metadata.get("is_mobile", 0)),  # is_mobile
            int(metadata.get("ip_first_octet", 192)),  # ip_first_octet
            0,  # login_count (historical)
            0,  # hour_diff (historical)
        ]

        training_data.append(features)

    # Train the detector
    success = anomaly_detector.train(training_data)

    if success:
        print(f"[OK] Trained on {len(training_data)} historical login events")

    return success


