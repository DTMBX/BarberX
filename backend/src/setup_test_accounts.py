# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Test Account Setup
Creates test accounts for development and testing:
- test-enterprise@Evident (Enterprise tier)
- test-free@Evident (Free tier)
- admin@Evident (Admin/Enterprise tier)
"""

import os
import sys

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models_auth import TierLevel, User, db


def setup_test_accounts():
    """Create all test accounts"""

    print("\n" + "=" * 70)
    print("Evident Test Account Setup")
    print("=" * 70 + "\n")

    # Test accounts to create
    test_accounts = [
        {
            "email": "admin@Evident",
            "password": os.environ.get("Evident_ADMIN_PASSWORD", "AdminTest2026!"),
            "full_name": "Evident Administrator",
            "tier": TierLevel.ENTERPRISE,
            "is_admin": True,
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "test-enterprise@Evident",
            "password": "EnterpriseTest2026!",
            "full_name": "Enterprise Test User",
            "tier": TierLevel.ENTERPRISE,
            "is_admin": False,
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "test-free@Evident",
            "password": "FreeTest2026!",
            "full_name": "Free Tier Test User",
            "tier": TierLevel.FREE,
            "is_admin": False,
            "is_verified": True,
            "is_active": True,
        },
    ]

    with app.app_context():
        created = 0
        updated = 0

        for account in test_accounts:
            user = User.query.filter_by(email=account["email"]).first()

            if user:
                print(f"⚠️  Updating existing account: {account['email']}")
                user.set_password(account["password"])
                user.tier = account["tier"]
                user.is_admin = account["is_admin"]
                user.is_verified = account["is_verified"]
                user.is_active = account["is_active"]
                user.full_name = account["full_name"]
                updated += 1
            else:
                print(f"✅ Creating new account: {account['email']}")
                user = User(
                    email=account["email"],
                    full_name=account["full_name"],
                    tier=account["tier"],
                    is_admin=account["is_admin"],
                    is_verified=account["is_verified"],
                    is_active=account["is_active"],
                )
                user.set_password(account["password"])
                db.session.add(user)
                created += 1

        db.session.commit()

        print("\n" + "=" * 70)
        print("TEST ACCOUNT CREDENTIALS")
        print("=" * 70)

        for account in test_accounts:
            user = User.query.filter_by(email=account["email"]).first()
            tier_emoji = (
                "👑" if user.is_admin else ("🏢" if user.tier == TierLevel.ENTERPRISE else "🆓")
            )

            print(f"\n{tier_emoji} {account['email']}")
            print("   Password: [HIDDEN]")
            print(f"   Tier:     {user.tier.name} ({user.tier_name})")
            print(f"   Admin:    {user.is_admin}")
            print(f"   Active:   {user.is_active}")
            print(f"   Verified: {user.is_verified}")

            # Verify password works
            if user.check_password(account["password"]):
                print("   Login:    ✅ Password verified")
            else:
                print("   Login:    ❌ PASSWORD VERIFICATION FAILED!")

        print("\n" + "=" * 70)
        print(f"SUMMARY: Created {created}, Updated {updated}")
        print("=" * 70)

        # Show all users in database
        print("\n📋 All Users in Database:")
        all_users = User.query.order_by(User.created_at.desc()).all()
        for user in all_users:
            admin_badge = " [ADMIN]" if user.is_admin else ""
            active_badge = "" if user.is_active else " [INACTIVE]"
            print(f"   • {user.email} - {user.tier.name}{admin_badge}{active_badge}")

        print("\n✅ Test accounts ready for login at /auth/login\n")


if __name__ == "__main__":
    setup_test_accounts()
