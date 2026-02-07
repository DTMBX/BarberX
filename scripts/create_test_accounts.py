# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Create Test Accounts for Evident UX Testing
===========================================
Creates one test account for each tier level:
- FREE
- PROFESSIONAL
- PREMIUM
- ENTERPRISE
- ADMIN

Each account includes sample usage data to test tier-specific UX features.
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from existing auth module
from flask import Flask
from models_auth import TierLevel, UsageTracking, User, bcrypt, db

# Create Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "test-secret-key"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'instance', 'Evident_auth.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)


def create_test_accounts():
    """Create test accounts for each tier with sample data."""

    with app.app_context():
        # Ensure tables exist
        db.create_all()

        print("🚀 Creating Evident Test Accounts...\n")

        # Test account configurations
        test_accounts = [
            {
                "email": "free@Evident.test",
                "password": "test123",
                "full_name": "Free Tier User",
                "tier": TierLevel.FREE,
                "usage": {
                    "analyses_this_month": 2,
                    "bwc_videos_processed": 1,
                    "document_pages_processed": 8,
                    "transcription_minutes_used": 15,
                    "storage_used_mb": 45,
                },
            },
            {
                "email": "pro@Evident.test",
                "password": "test123",
                "full_name": "Professional User",
                "tier": TierLevel.PROFESSIONAL,
                "usage": {
                    "analyses_this_month": 18,
                    "bwc_videos_processed": 8,
                    "document_pages_processed": 350,
                    "transcription_minutes_used": 240,
                    "storage_used_mb": 2400,
                },
            },
            {
                "email": "premium@Evident.test",
                "password": "test123",
                "full_name": "Premium User",
                "tier": TierLevel.PREMIUM,
                "usage": {
                    "analyses_this_month": 45,
                    "bwc_videos_processed": 22,
                    "document_pages_processed": 1800,
                    "transcription_minutes_used": 680,
                    "storage_used_mb": 8500,
                },
            },
            {
                "email": "enterprise@Evident.test",
                "password": "test123",
                "full_name": "Enterprise User",
                "tier": TierLevel.ENTERPRISE,
                "usage": {
                    "analyses_this_month": 120,
                    "bwc_videos_processed": 85,
                    "document_pages_processed": 12000,
                    "transcription_minutes_used": 2400,
                    "storage_used_mb": 45000,
                },
            },
            {
                "email": "admin@Evident.test",
                "password": "test123",
                "full_name": "System Administrator",
                "tier": TierLevel.ADMIN,
                "usage": {
                    "analyses_this_month": 0,
                    "bwc_videos_processed": 0,
                    "document_pages_processed": 0,
                    "transcription_minutes_used": 0,
                    "storage_used_mb": 0,
                },
            },
        ]

        created_count = 0
        updated_count = 0

        for account in test_accounts:
            # Check if user already exists
            existing_user = User.query.filter_by(email=account["email"]).first()

            if existing_user:
                print(f"⚠️  User {account['email']} already exists. Updating...")
                user = existing_user
                user.tier = account["tier"]
                user.full_name = account["full_name"]
                user.set_password(account["password"])
                updated_count += 1
            else:
                # Create new user
                user = User(
                    email=account["email"],
                    full_name=account["full_name"],
                    tier=account["tier"],
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                    - timedelta(days=30),  # Account created 30 days ago
                )
                user.set_password(account["password"])
                db.session.add(user)
                created_count += 1

            db.session.commit()  # Commit to get user.id

            # Get current year and month
            now = datetime.utcnow()
            current_year = now.year
            current_month = now.month

            # Create or update usage tracking
            usage = UsageTracking.query.filter_by(
                user_id=user.id, year=current_year, month=current_month
            ).first()
            if not usage:
                usage = UsageTracking(user_id=user.id, year=current_year, month=current_month)
                db.session.add(usage)

            # Set usage data
            usage.bwc_videos_processed = account["usage"]["bwc_videos_processed"]
            usage.document_pages_processed = account["usage"]["document_pages_processed"]
            usage.transcription_minutes_used = account["usage"]["transcription_minutes_used"]
            usage.storage_used_mb = account["usage"]["storage_used_mb"]
            usage.updated_at = now

            db.session.commit()

            tier_name = account["tier"].name
            print(f"✅ {tier_name:12} - {account['email']:25} (password: {account['password']})")

        print(f"\n{'=' * 80}")
        print("📊 Summary:")
        print(f"   • Created: {created_count} new accounts")
        print(f"   • Updated: {updated_count} existing accounts")
        print(f"   • Total:   {created_count + updated_count} test accounts ready")
        print(f"{'=' * 80}\n")

        print("🎉 Test Account Creation Complete!")
        print("\n📝 Login Instructions:")
        print("   1. Navigate to http://localhost:5000/auth/login")
        print("   2. Use any of the emails above with password: test123")
        print("   3. Each account has tier-specific features and sample usage data")
        print("\n🔍 UX Features to Test:")
        print("   • Onboarding tour (shows on first login)")
        print("   • Usage meters (color-coded progress bars)")
        print("   • Tier upgrade cards (context-aware suggestions)")
        print("   • Admin dashboard (admin@Evident.test only)")
        print("   • Accessibility features (keyboard navigation, screen reader support)")
        print(
            "\n💡 Tip: Open multiple private/incognito windows to test different accounts simultaneously!"
        )


if __name__ == "__main__":
    try:
        create_test_accounts()
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
