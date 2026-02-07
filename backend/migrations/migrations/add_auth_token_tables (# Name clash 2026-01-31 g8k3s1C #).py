# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database Migration: Add Auth Token Tables

This migration adds:
- password_reset_tokens: Persistent password reset tokens (replaces in-memory storage)
- email_verification_tokens: Email verification tokens for new signups

Run: python migrations/add_auth_token_tables.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migration():
    """Run the migration to add auth token tables"""
    from app import app, db

    with app.app_context():
        # Import the models to register them

        print("=" * 60)
        print("Auth Token Tables - Database Migration")
        print("=" * 60)

        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        tables_to_create = []

        if "password_reset_tokens" not in existing_tables:
            tables_to_create.append("password_reset_tokens")
        if "email_verification_tokens" not in existing_tables:
            tables_to_create.append("email_verification_tokens")

        if not tables_to_create:
            print("\n✓ All auth token tables already exist!")
            print("  - password_reset_tokens")
            print("  - email_verification_tokens")
            return True

        print(f"\nCreating tables: {', '.join(tables_to_create)}")

        # Create tables
        try:
            from sqlalchemy import text

            if "password_reset_tokens" in tables_to_create:
                db.session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        token VARCHAR(64) NOT NULL UNIQUE,
                        expires_at DATETIME NOT NULL,
                        used BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """
                    )
                )
                db.session.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token)"
                    )
                )
                db.session.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id)"
                    )
                )
                db.session.commit()
                print("  ✓ Created password_reset_tokens table with indexes")

            if "email_verification_tokens" in tables_to_create:
                db.session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS email_verification_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        token VARCHAR(64) NOT NULL UNIQUE,
                        expires_at DATETIME NOT NULL,
                        used BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """
                    )
                )
                db.session.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_email_verify_token ON email_verification_tokens(token)"
                    )
                )
                db.session.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS idx_email_verify_user ON email_verification_tokens(user_id)"
                    )
                )
                db.session.commit()
                print("  ✓ Created email_verification_tokens table with indexes")

            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)

            print("\nNew auth features available:")
            print("  - Password reset tokens now persist across server restarts")
            print("  - Email verification tokens for new user signups")
            print("\nAuth routes:")
            print("  POST  /auth/forgot-password       - Request password reset")
            print("  GET   /auth/reset-password/<token>- Reset password form")
            print("  POST  /auth/reset-password/<token>- Submit new password")
            print("  GET   /auth/verify-email/<token>  - Verify email address")
            print("  POST  /auth/resend-verification   - Resend verification email")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def verify_tables():
    """Verify tables were created correctly"""
    from app import app, db

    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print("\nVerifying tables...")
        required = ["password_reset_tokens", "email_verification_tokens"]

        all_present = True
        for table in required:
            if table in tables:
                columns = [c["name"] for c in inspector.get_columns(table)]
                print(f"  ✓ {table} ({len(columns)} columns)")
            else:
                print(f"  ✗ {table} - MISSING")
                all_present = False

        return all_present


if __name__ == "__main__":
    success = run_migration()
    if success:
        verify_tables()
    sys.exit(0 if success else 1)
