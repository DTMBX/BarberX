# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Admin Account Setup - FIXED VERSION
Creates admin account using correct SQLAlchemy models
"""

import os
import sys

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models_auth import TierLevel, User, db

# SECURE ADMIN CREDENTIALS
ADMIN_EMAIL = "admin@Evident"
ADMIN_PASSWORD = os.environ.get("Evident_ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    print("❌ ERROR: Evident_ADMIN_PASSWORD environment variable must be set")
    print("\nSet it with:")
    print("  $env:Evident_ADMIN_PASSWORD = 'pQWN6CUNH04Gx6Ud73dfybu6jiV_DM4s'")
    sys.exit(1)


def create_admin_fixed():
    """Create admin account using correct SQLAlchemy models"""

    print("\n" + "=" * 70)
    print("Evident Admin Account Setup (FIXED VERSION)")
    print("=" * 70 + "\n")

    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()

        if admin:
            print(f"⚠️  Admin account already exists: {admin.email}")
            print(f"   Current tier: {admin.tier.name}")
            print(f"   Is admin: {admin.is_admin}")
            print("\n   Updating password...")

            # Update password
            admin.set_password(ADMIN_PASSWORD)
            admin.tier = TierLevel.ADMIN
            admin.is_admin = True
            admin.is_active = True
            admin.is_verified = True

            db.session.commit()
            print("✅ Admin account updated")
        else:
            print("Creating new admin account...")

            # Create new admin
            admin = User(
                email=ADMIN_EMAIL,
                full_name="Evident System Administrator",
                tier=TierLevel.ADMIN,
                is_admin=True,
                is_active=True,
                is_verified=True,
            )

            admin.set_password(ADMIN_PASSWORD)

            db.session.add(admin)
            db.session.commit()

            print("✅ Admin account created")

        # Verify
        admin = User.query.filter_by(email=ADMIN_EMAIL).first()

        print("\n" + "=" * 70)
        print("ADMIN CREDENTIALS")
        print("=" * 70)
        print(f"Email:    {admin.email}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Tier:     {admin.tier.name} (${admin.tier.value}/mo)")
        print(f"Is Admin: {admin.is_admin}")
        print(f"Active:   {admin.is_active}")
        print(f"Verified: {admin.is_verified}")
        print("=" * 70 + "\n")

        # Test password
        if admin.check_password(ADMIN_PASSWORD):
            print("✅ Password verification: SUCCESS\n")
        else:
            print("❌ Password verification: FAILED\n")
            return False

        # Count all users
        total_users = User.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()

        print(f"Total users: {total_users}")
        print(f"Admin users: {admin_count}")

        if admin_count == 1:
            print("✅ Security check: Exactly ONE admin exists\n")
        else:
            print(f"⚠️  WARNING: {admin_count} admins found (should be 1)\n")

        return True


if __name__ == "__main__":
    try:
        success = create_admin_fixed()
        if success:
            print("✅ Setup complete!")
            print("\n🌐 Login at: http://localhost:5000/auth/login")
            print(f"📧 Email: {ADMIN_EMAIL}")
            sys.exit(0)
        else:
            print("❌ Setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
