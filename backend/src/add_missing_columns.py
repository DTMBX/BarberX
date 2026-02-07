# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Add missing columns to users table
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "Evident.db")


def add_missing_columns():
    print("\n" + "=" * 80)
    print("Adding missing columns to users table")
    print("=" * 80 + "\n")

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(users)")
        current_columns = [col[1] for col in cursor.fetchall()]

        print(f"Current columns ({len(current_columns)}): {', '.join(current_columns)}")

        # Define missing columns to add
        missing_columns = {
            "last_login": "TIMESTAMP NULL",
            "is_verified": "BOOLEAN DEFAULT 0",
            "analyses_count": "INTEGER DEFAULT 0",
        }

        added = 0
        for col_name, col_def in missing_columns.items():
            if col_name not in current_columns:
                print(f"\nAdding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                conn.commit()
                print(f"✅ Added '{col_name}'")
                added += 1
            else:
                print(f"ℹ️  Column '{col_name}' already exists")

        if added > 0:
            # Verify
            cursor.execute("PRAGMA table_info(users)")
            new_columns = [col[1] for col in cursor.fetchall()]
            print(f"\nNew columns ({len(new_columns)}): {', '.join(new_columns)}")

        conn.close()

        print("\n" + "=" * 80)
        print(f"Migration Complete! Added {added} columns")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()
        return False


if __name__ == "__main__":
    add_missing_columns()
