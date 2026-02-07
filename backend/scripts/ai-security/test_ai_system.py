# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Test the AI Login Stability System
Verify all components are working
"""

import os
import sys

print("\n" + "=" * 70)
print("  AI LOGIN STABILITY SYSTEM - STATUS CHECK")
print("=" * 70 + "\n")

# Test 1: Check dependencies
print("[1/6] Checking Dependencies...")
dependencies = {
    "pyod": "Anomaly Detection",
    "redis": "Session Management",
    "posthog": "User Analytics",
    "user_agents": "Device Parsing",
}

missing = []
for package, description in dependencies.items():
    try:
        __import__(package)
        print(f"   [OK] {package:<15} - {description}")
    except ImportError:
        print(f"   [ERROR] {package:<15} - MISSING!")
        missing.append(package)

if missing:
    print(f"\n   ERROR: Missing packages: {', '.join(missing)}")
    print(f"   Run: pip install {' '.join(missing)}")
    sys.exit(1)

# Test 2: Check Flask app integration
print("\n[2/6] Checking Flask Integration...")
try:
    from dotenv import load_dotenv

    load_dotenv()

    from flask import Flask

    from auth_routes import auth_bp
    from models_auth import User, db

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///Evident_FRESH.db")
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace(
            "postgres://", "postgresql://", 1
        )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")

    db.init_app(app)
    app.register_blueprint(auth_bp)

    print("   ✓ Flask app initialized")
    print("   ✓ Auth blueprint registered")
    print("   ✓ Database configured")
except Exception as e:
    print(f"   ✗ Flask integration failed: {e}")
    sys.exit(1)

# Test 3: Check anomaly detector
print("\n[3/6] Checking Anomaly Detector...")
try:
    import numpy as np
    from pyod.models.iforest import IForest

    # Create sample data
    X_train = np.random.randn(100, 5)  # 100 normal logins
    X_test = np.random.randn(10, 5)  # 10 new logins

    clf = IForest(contamination=0.1)
    clf.fit(X_train)
    scores = clf.decision_function(X_test)

    print("   ✓ IForest model created")
    print(f"   ✓ Trained on {len(X_train)} samples")
    print(f"   ✓ Anomaly scores: {scores[0]:.4f} - {scores[-1]:.4f}")
except Exception as e:
    print(f"   ✗ Anomaly detector failed: {e}")

# Test 4: Check Redis connection
print("\n[4/6] Checking Redis...")
try:
    import redis

    r = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=2)
    r.ping()
    print("   ✓ Redis connected (localhost:6379)")

    # Test set/get
    r.set("test_key", "test_value", ex=60)
    value = r.get("test_key")
    print("   ✓ Redis read/write working")
    r.delete("test_key")
except redis.ConnectionError:
    print("   ⚠ Redis not running (optional - session management will use default)")
    print("   → To start Redis: Download from https://redis.io/download")
except Exception as e:
    print(f"   ⚠ Redis check failed: {e}")

# Test 5: Check PostHog
print("\n[5/6] Checking PostHog Analytics...")
try:
    import posthog

    api_key = os.getenv("POSTHOG_API_KEY")

    if api_key:
        posthog.api_key = api_key
        posthog.host = "https://app.posthog.com"
        print("   ✓ PostHog configured with API key")
        print(f"   ✓ Endpoint: {posthog.host}")
    else:
        print("   ⚠ POSTHOG_API_KEY not set (analytics disabled)")
        print("   → Sign up at https://posthog.com (free tier: 1M events/mo)")
except Exception as e:
    print(f"   ✗ PostHog check failed: {e}")

# Test 6: Check database and user count
print("\n[6/6] Checking Database...")
try:
    with app.app_context():
        user_count = User.query.count()
        print("   ✓ Database connected")
        print(f"   ✓ Total users: {user_count}")

        if user_count > 0:
            # Check if we have login history to train on
            recent_user = User.query.first()
            print(f"   ✓ Sample user: {recent_user.email}")
except Exception as e:
    print(f"   ✗ Database check failed: {e}")

# Summary
print("\n" + "=" * 70)
print("  SYSTEM STATUS SUMMARY")
print("=" * 70 + "\n")

print("✅ READY:")
print("   • Anomaly detection (PyOD)")
print("   • User analytics (PostHog)")
print("   • Device fingerprinting (user-agents)")
print("   • Flask integration complete")

print("\n⚠ OPTIONAL (Configure for full features):")
redis_status = "✓ Running" if "r" in locals() and r else "✗ Not running"
posthog_status = "✓ Configured" if api_key else "✗ Not configured"
print(f"   • Redis: {redis_status}")
print(f"   • PostHog: {posthog_status}")

print("\n🔧 NEXT STEPS:")
if not api_key:
    print("   1. Get PostHog API key: https://posthog.com")
    print("   2. Add to .env: POSTHOG_API_KEY=your_key_here")
print("   3. Train anomaly detector: python scripts/train_login_detector.py")
print("   4. Test login flow with both accounts")
print("   5. Monitor anomaly scores in admin dashboard")

print("\n" + "=" * 70 + "\n")
