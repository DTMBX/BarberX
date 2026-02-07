# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Smart Meter Database Migration
Creates tables for comprehensive usage tracking
"""

import os
import sys

sys.path.insert(0, ".")

# Load environment variables
from dotenv import load_dotenv

# Import Flask and SQLAlchemy directly to avoid OpenAI imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Create minimal db instance
db = SQLAlchemy()


def create_smart_meter_tables():
    """Create smart meter tables"""
    # Create Flask app with minimal config
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///Evident.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize db
    db.init_app(app)

    with app.app_context():
        # Import models INSIDE app context to avoid circular imports
        from usage_meter import SmartMeterEvent, UsageQuota

        print("Creating smart meter tables...")

        # Create tables
        SmartMeterEvent.__table__.create(db.engine, checkfirst=True)
        UsageQuota.__table__.create(db.engine, checkfirst=True)

        print("✅ Smart meter tables created successfully!")
        print("\nTables created:")
        print("  - smart_meter_events (tracks individual usage events)")
        print("  - usage_quotas (real-time quota tracking)")

        # Show table schemas
        # Import models again for schema display
        from usage_meter import SmartMeterEvent, UsageQuota

        print("\n" + "=" * 60)
        print("SMART METER EVENT SCHEMA")
        print("=" * 60)
        for column in SmartMeterEvent.__table__.columns:
            print(
                f"  {column.name:30s} {str(column.type):20s} {('NOT NULL' if not column.nullable else '')}"
            )

        print("\n" + "=" * 60)
        print("USAGE QUOTA SCHEMA")
        print("=" * 60)
        for column in UsageQuota.__table__.columns:
            print(
                f"  {column.name:30s} {str(column.type):20s} {('NOT NULL' if not column.nullable else '')}"
            )


if __name__ == "__main__":
    create_smart_meter_tables()
