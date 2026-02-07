# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database migration: Add tier column to user table
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "Evident.db")


def migrate_add_tier_column():
    """Add tier column to user table"""
    print("\n" + "=" * 80)
    print("Database Migration: Adding tier column for UX improvements")
    print("=" * 80 + "\n")

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Database will be created when you run the app.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if tier column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]

    if "tier" in columns:
        print("✅ Column 'tier' already exists in user table")
        conn.close()
        return True

    print("Adding 'tier' column to user table...")

    try:
        # Add tier column (stores integer value from TierLevel enum)
        cursor.execute(
            """
            ALTER TABLE user 
            ADD COLUMN tier INTEGER DEFAULT 0
        """
        )

        conn.commit()
        print("✅ Column 'tier' added successfully (default: 0 = FREE)")

        # Set admin user to ADMIN tier if exists
        cursor.execute(
            """
            UPDATE user 
            SET tier = 9999
            WHERE email = 'admin@Evident' OR role = 'admin'
        """
        )

        rows_updated = cursor.rowcount
        if rows_updated > 0:
            conn.commit()
            print(f"✅ Updated {rows_updated} admin user(s) to ADMIN tier")

        # Show migration summary
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]

        print("\n📊 Migration Summary:")
        print(f"   • Total users in database: {total_users}")
        print("   • Default tier set to: FREE (0)")
        print("   • Admin users upgraded to: ADMIN (9999)")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False


if __name__ == "__main__":
    migrate_add_tier_column()
    print("\n" + "=" * 80)
    print("✅ Migration complete! You can now create test accounts.")
    print("=" * 80 + "\n")
