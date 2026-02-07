# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Initialize usage quotas for all existing users based on their tier.
Run this once after deploying the smart meter system.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from app import app, db
from models_auth import User
from usage_meter import SmartMeter, UsageQuota


def initialize_all_quotas():
    """Initialize usage quotas for all users who don't have one yet."""
    with app.app_context():
        # Get all users
        users = User.query.all()

        initialized = 0
        skipped = 0
        errors = 0

        print(f"\n{'=' * 70}")
        print(f"  INITIALIZING USAGE QUOTAS FOR {len(users)} USERS")
        print(f"{'=' * 70}\n")

        for user in users:
            try:
                # Check if user already has a quota
                existing_quota = UsageQuota.query.filter_by(user_id=user.id).first()

                if existing_quota:
                    print(f"⏭️  Skipping {user.email} - quota already exists")
                    skipped += 1
                    continue

                # Initialize quota
                SmartMeter.initialize_user_quota(user.id)

                print(f"✅ Initialized {user.email} (Tier: {user.tier or 'FREE'})")
                initialized += 1

            except Exception as e:
                print(f"❌ Error initializing {user.email}: {str(e)}")
                errors += 1

        # Commit all changes
        db.session.commit()

        print(f"\n{'=' * 70}")
        print("  INITIALIZATION COMPLETE")
        print(f"{'=' * 70}")
        print(f"  ✅ Initialized: {initialized}")
        print(f"  ⏭️  Skipped:     {skipped}")
        print(f"  ❌ Errors:      {errors}")
        print(f"  📊 Total:       {len(users)}")
        print(f"{'=' * 70}\n")

        return initialized, skipped, errors


if __name__ == "__main__":
    initialize_all_quotas()
