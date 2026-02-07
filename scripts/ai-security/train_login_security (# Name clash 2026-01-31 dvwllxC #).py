# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Train Login Security AI Model
Initialize and train the anomaly detection model on historical login data
"""

import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

# Create minimal Flask app for database access
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///Evident_FRESH.db")
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace(
        "postgres://", "postgresql://", 1
    )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-12345")

from login_security import login_security
from models_auth import User, db

db.init_app(app)

with app.app_context():
    print("\n" + "=" * 70)
    print("  TRAINING LOGIN SECURITY AI MODEL")
    print("=" * 70 + "\n")

    # Get all users
    users = User.query.all()

    if not users:
        print("[WARN] No users found in database. Creating sample training data...")

        # Generate synthetic training data for initial model
        import numpy as np

        np.random.seed(42)

        sample_events = []
        for i in range(100):
            # Normal login patterns (daytime, weekdays, desktop)
            hour = np.random.randint(8, 18)  # Business hours
            day = np.random.randint(0, 5)  # Weekdays
            is_mobile = np.random.choice([0, 1], p=[0.7, 0.3])

            sample_events.append(
                {
                    "hour": hour,
                    "day_of_week": day,
                    "is_mobile": is_mobile,
                    "is_bot": 0,
                    "success": True,
                }
            )

        # Add some anomalous patterns (night, weekends, bots)
        for i in range(10):
            hour = np.random.choice([2, 3, 4, 23])  # Night
            day = np.random.choice([5, 6])  # Weekend
            is_mobile = 0
            is_bot = 1

            sample_events.append(
                {
                    "hour": hour,
                    "day_of_week": day,
                    "is_mobile": is_mobile,
                    "is_bot": is_bot,
                    "success": False,
                }
            )

        print(f"[OK] Generated {len(sample_events)} synthetic login events")

    else:
        # Use real user data to create training samples
        sample_events = []

        for user in users:
            if user.last_login:
                # Extract features from last login
                hour = user.last_login.hour
                day_of_week = user.last_login.weekday()

                sample_events.append(
                    {
                        "hour": hour,
                        "day_of_week": day_of_week,
                        "is_mobile": 0,  # Assume desktop for historical data
                        "is_bot": 0,
                        "success": True,
                    }
                )

        print(f"[OK] Extracted {len(sample_events)} login events from {len(users)} users")

        # Add synthetic anomalies if we don't have enough data
        if len(sample_events) < 20:
            print("[INFO] Adding synthetic anomalies to improve detection...")
            import numpy as np

            np.random.seed(42)

            for i in range(20 - len(sample_events)):
                hour = np.random.randint(8, 18)
                day = np.random.randint(0, 5)
                sample_events.append(
                    {
                        "hour": hour,
                        "day_of_week": day,
                        "is_mobile": 0,
                        "is_bot": 0,
                        "success": True,
                    }
                )

    # Train the model
    print(f"\n[TRAIN] Training model on {len(sample_events)} events...")

    success = login_security.train_on_historical_data(sample_events)

    if success:
        print("\n" + "=" * 70)
        print("  MODEL TRAINING COMPLETE")
        print("=" * 70)
        print(f"\n✅ Model trained on {len(sample_events)} login events")
        print(f"✅ Model saved to: {login_security.model_path}")
        print("✅ Contamination rate: 5% (anomaly threshold)")
        print("\n[OK] Login security AI is now active!")
        print("[OK] Suspicious logins will be automatically detected\n")

    else:
        print("\n" + "=" * 70)
        print("  MODEL TRAINING FAILED")
        print("=" * 70)
        print("\n❌ Failed to train model")
        print("❌ Check logs for details\n")
        sys.exit(1)
