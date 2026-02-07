# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database migration: Add role column to users table
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "Evident.db")


def migrate_add_role_column():
    """Add role column to users table"""
    print("\n" + "=" * 80)
    print("Database Migration: Adding role column")
    print("=" * 80 + "\n")

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Database will be created when you run the app.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if role column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]

    if "role" in columns:
        print("✅ Column 'role' already exists in user table")
        conn.close()
        return True

    print("Adding 'role' column to user table...")

    try:
        # Add role column
        cursor.execute(
            """
            ALTER TABLE user 
            ADD COLUMN role VARCHAR(20) DEFAULT 'user'
        """
        )

        conn.commit()
        print("✅ Column 'role' added successfully")

        # Update admin user if exists
        cursor.execute(
            """
            UPDATE user 
            SET role = 'admin' 
            WHERE email = 'admin@Evident.info'
        """
        )

        if cursor.rowcount > 0:
            print("✅ Updated admin user with role='admin'")

        conn.commit()

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()
        return False

    # Verify
    cursor.execute("PRAGMA table_info(user)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}

    if "role" in columns:
        print(f"✅ Verified: role column exists (type: {columns['role']})")

        # Show current users with roles
        cursor.execute("SELECT email, role, subscription_tier FROM user")
        users = cursor.fetchall()

        if users:
            print(f"\nCurrent users ({len(users)}):")
            for email, role, tier in users:
                role_display = role or "user"
                print(f"  • {email:30} | role={role_display:10} | tier={tier}")

    conn.close()

    print("\n" + "=" * 80)
    print("Migration Complete!")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    migrate_add_role_column()
