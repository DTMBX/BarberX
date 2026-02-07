# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Add AppSettings table to database
Run this to add the settings management feature to existing database
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "Evident.db")


def add_settings_table():
    """Add app_settings table to existing database"""
    print("\n" + "=" * 80)
    print("Adding AppSettings Table to Database")
    print("=" * 80 + "\n")

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Please create the database first by running the app.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if table already exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='app_settings'
    """
    )

    if cursor.fetchone():
        print("ℹ️  app_settings table already exists")
        conn.close()
        return True

    # Create app_settings table
    print("Creating app_settings table...")

    cursor.execute(
        """
        CREATE TABLE app_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) UNIQUE NOT NULL,
            value TEXT,
            value_type VARCHAR(20) DEFAULT 'string',
            category VARCHAR(50) DEFAULT 'general',
            description VARCHAR(500),
            is_editable BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            FOREIGN KEY (updated_by) REFERENCES user (id)
        )
    """
    )

    # Create index on key for fast lookups
    cursor.execute("CREATE INDEX ix_app_settings_key ON app_settings (key)")
    cursor.execute("CREATE INDEX ix_app_settings_category ON app_settings (category)")

    conn.commit()

    print("✅ app_settings table created successfully")

    # Verify table exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='app_settings'
    """
    )

    if cursor.fetchone():
        print("✅ Table verified in database")

        # Show current database tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"\nCurrent database tables ({len(tables)}):")
        for table in tables:
            print(f"  • {table[0]}")

    conn.close()

    print("\n" + "=" * 80)
    print("Migration Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Log in to admin panel: https://app.Evident/admin")
    print("2. Go to Settings tab")
    print("3. Click 'Initialize Defaults' to create all settings")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    add_settings_table()
