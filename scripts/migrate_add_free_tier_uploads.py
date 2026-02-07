# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database Migration: Add FREE Tier One-Time Upload Tracking
Adds fields to track one-time upload usage for FREE tier users
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_migration():
    """Run the migration"""
    try:
        # Import after path is set
        from app import app, db
        from models_auth import User
        from sqlalchemy import inspect

        with app.app_context():
            try:
                # Check if columns already exist
                inspector = inspect(db.engine)
                columns = [col["name"] for col in inspector.get_columns("users")]

                if "one_time_upload_used" in columns:
                    print("✅ Columns already exist, skipping...")
                    return True

                print("Adding one-time upload tracking columns...")

                # Add columns using raw SQL (safer for existing databases)
                db.session.execute(
                    db.text(
                        """
                    ALTER TABLE users 
                    ADD COLUMN one_time_upload_used BOOLEAN DEFAULT FALSE
                """
                    )
                )

                db.session.execute(
                    db.text(
                        """
                    ALTER TABLE users 
                    ADD COLUMN one_time_upload_date TIMESTAMP NULL
                """
                    )
                )

                db.session.commit()

                print("✅ Successfully added one-time upload tracking columns")

                # Update existing users
                print("Updating existing users...")
                users = User.query.all()
                print(f"✅ Found {len(users)} users (defaults will be applied)")

                return True

            except Exception as e:
                db.session.rollback()
                error_msg = str(e).lower()
                # If columns already exist, that's okay
                if "already exists" in error_msg or "duplicate" in error_msg:
                    print("✅ Columns already exist (expected)")
                    return True
                print(f"❌ Error: {e}")
                return False

    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("FREE Tier One-Time Upload Migration")
    print("=" * 70)

    if run_migration():
        print("\n" + "=" * 70)
        print("✅ Migration completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Restart your Flask app")
        print("2. Test FREE tier upload functionality")
        print("3. Verify watermarks are applied")
        print("4. Set up cron job for data retention cleanup")
        sys.exit(0)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
