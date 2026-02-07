# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database migration: Add Stripe subscription fields
Adds Stripe tracking fields to User model and updates UsageTracking
"""

from app import app, db
from models_auth import UsageTracking, User
from sqlalchemy import inspect


def add_column_if_not_exists(table_name, column_name, column_type):
    """Add column to table if it doesn't exist"""
    inspector = inspect(db.engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]

    if column_name not in columns:
        with db.engine.connect() as conn:
            conn.execute(
                db.text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            )
            conn.commit()
        print(f"✅ Added column {table_name}.{column_name}")
    else:
        print(f"⏭️  Column {table_name}.{column_name} already exists")


def migrate():
    """Run migration"""
    print("=" * 60)
    print("MIGRATION: Add Stripe Subscription Fields")
    print("=" * 60)

    with app.app_context():
        # Add Stripe fields to users table
        print("\n📊 Adding Stripe fields to users table...")
        add_column_if_not_exists("users", "stripe_customer_id", "VARCHAR(100)")
        add_column_if_not_exists("users", "stripe_subscription_id", "VARCHAR(100)")
        add_column_if_not_exists("users", "stripe_subscription_status", "VARCHAR(50)")
        add_column_if_not_exists("users", "stripe_current_period_end", "DATETIME")
        add_column_if_not_exists("users", "trial_end", "DATETIME")
        add_column_if_not_exists("users", "is_on_trial", "BOOLEAN DEFAULT 0")

        # Add unique indexes for Stripe IDs
        try:
            with db.engine.connect() as conn:
                conn.execute(
                    db.text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS idx_stripe_customer ON users(stripe_customer_id)"
                    )
                )
                conn.execute(
                    db.text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS idx_stripe_subscription ON users(stripe_subscription_id)"
                    )
                )
                conn.commit()
            print("✅ Added indexes for Stripe fields")
        except Exception as e:
            print(f"⚠️  Indexes may already exist: {e}")

        # Add new usage tracking fields
        print("\n📊 Adding usage tracking fields...")
        add_column_if_not_exists("usage_tracking", "bwc_video_hours_used", "FLOAT DEFAULT 0.0")
        add_column_if_not_exists("usage_tracking", "pdf_documents_processed", "INTEGER DEFAULT 0")
        add_column_if_not_exists("usage_tracking", "cases_created", "INTEGER DEFAULT 0")

        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update .env with Stripe keys:")
        print("   - STRIPE_SECRET_KEY=sk_...")
        print("   - STRIPE_PUBLISHABLE_KEY=pk_...")
        print("   - STRIPE_WEBHOOK_SECRET=whsec_...")
        print("   - STRIPE_PRICE_PRO=price_...")
        print("   - STRIPE_PRICE_PREMIUM=price_...")
        print("\n2. Create Stripe products:")
        print("   - PRO: $49/month with 3-day trial")
        print("   - PREMIUM: $249/month")
        print("\n3. Configure webhook endpoint:")
        print("   - URL: https://Evident.info/api/stripe/webhook")
        print("   - Events: checkout.session.completed, customer.subscription.*")
        print("\n4. Test subscription flow")


if __name__ == "__main__":
    migrate()
