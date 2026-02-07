# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Migration: Add storage_used_mb column to users table
Run this once after deploying security fixes
"""

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize minimal Flask app
app = Flask(__name__)

# Database configuration
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    is_postgres = True
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{os.path.join(basedir, 'instance', 'Evident.db')}"
    )
    is_postgres = False

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def migrate():
    """Add storage_used_mb column to users table"""
    with app.app_context():
        try:
            # Check if column exists (different for SQLite vs PostgreSQL)
            if is_postgres:
                result = db.session.execute(
                    db.text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name='users' AND column_name='storage_used_mb'"
                    )
                )
                exists = result.fetchone() is not None
            else:
                # SQLite - check pragma
                result = db.session.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                exists = "storage_used_mb" in columns

            if exists:
                print("✅ storage_used_mb column already exists")
                return

            print(
                f"Adding storage_used_mb column to users table ({'PostgreSQL' if is_postgres else 'SQLite'})..."
            )

            # Add the column
            db.session.execute(
                db.text("ALTER TABLE users ADD COLUMN storage_used_mb FLOAT DEFAULT 0.0")
            )
            db.session.commit()

            print("✅ Migration successful! storage_used_mb column added")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    migrate()
