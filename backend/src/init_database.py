# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Create all missing database tables for Evident Legal Tech Platform
Run this to initialize the database with all required tables
"""

import sys
from pathlib import Path

# Import the Flask app and db
from app import app, db


def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables for Evident Legal Tech Platform...")

    with app.app_context():
        # Create instance directory if it doesn't exist
        instance_dir = Path("./instance")
        instance_dir.mkdir(exist_ok=True)

        # Create all tables
        db.create_all()

        print("\n✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - users (authentication)")
        print("  - analyses (BWC video analysis)")
        print("  - pdf_uploads (court document tracking)")
        print("  - audit_logs (compliance logging)")
        print("  - api_keys (API access)")
        print("  - app_settings (application configuration)")

        # Check if tables were created
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        print(f"\n📊 Total tables in database: {len(tables)}")
        for table in sorted(tables):
            print(f"  ✓ {table}")

        return True


if __name__ == "__main__":
    try:
        create_tables()
        print("\n🎉 Database initialization complete!")
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
