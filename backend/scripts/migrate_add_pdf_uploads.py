# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python
"""
Database migration script to add PDFUpload table
Run this script to update the database schema
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db


def migrate_database():
    """Add PDFUpload table to database"""

    with app.app_context():
        print("🔄 Starting database migration...")

        try:
            # Import the model to ensure it's registered

            # Create tables
            db.create_all()

            print("✅ PDFUpload table created successfully!")
            print("✅ Database migration complete!")

            return True

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
