# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Create test accounts for subscription testing
"""

from app import app, db
from models_auth import TierLevel, User


def create_test_accounts():
    """Create test accounts for each tier"""
    with app.app_context():
        test_accounts = [
            {
                "email": "free@Evident.test",
                "password": "test123",
                "full_name": "Free Tier User",
                "tier": TierLevel.FREE,
            },
            {
                "email": "pro@Evident.test",
                "password": "test123",
                "full_name": "Professional Tier User",
                "tier": TierLevel.PROFESSIONAL,
            },
            {
                "email": "premium@Evident.test",
                "password": "test123",
                "full_name": "Premium Tier User",
                "tier": TierLevel.PREMIUM,
            },
            {
                "email": "enterprise@Evident.test",
                "password": "test123",
                "full_name": "Enterprise Tier User",
                "tier": TierLevel.ENTERPRISE,
            },
            {
                "email": "admin@Evident.test",
                "password": "admin123",
                "full_name": "Admin User",
                "tier": TierLevel.ADMIN,
                "is_admin": True,
            },
        ]

        print("Creating test accounts...")
        for account in test_accounts:
            # Check if user exists
            existing = User.query.filter_by(email=account["email"]).first()
            if existing:
                print(f"  ⏭️  {account['email']} already exists")
                continue

            # Create user
            user = User(
                email=account["email"],
                full_name=account["full_name"],
                tier=account["tier"],
                is_verified=True,
                is_admin=account.get("is_admin", False),
            )
            user.set_password(account["password"])

            db.session.add(user)
            print(f"  ✅ Created {account['email']} ({account['tier'].name})")

        db.session.commit()
        print("\n✅ Test accounts created successfully!")
        print("\nLogin credentials:")
        print("  free@Evident.test / test123")
        print("  pro@Evident.test / test123")
        print("  premium@Evident.test / test123")
        print("  enterprise@Evident.test / test123")
        print("  admin@Evident.test / admin123")


if __name__ == "__main__":
    create_test_accounts()
