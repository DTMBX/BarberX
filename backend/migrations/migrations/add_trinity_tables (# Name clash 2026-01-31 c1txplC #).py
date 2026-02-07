# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Database Migration: Add Legal Trinity Tables

This migration adds tables for the Legal Trinity system:
- code360_municipalities: Integrated municipalities (Code360, Municode, etc.)
- code360_sections: Municipal code sections
- code360_fts: Full-text search index for municipal codes

Run: python migrations/add_trinity_tables.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migration():
    """Run the migration to add Legal Trinity tables"""
    from app import app, db

    with app.app_context():
        print("=" * 60)
        print("Legal Trinity - Database Migration")
        print("=" * 60)

        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        tables_to_create = []

        if "code360_municipalities" not in existing_tables:
            tables_to_create.append("code360_municipalities")
        if "code360_sections" not in existing_tables:
            tables_to_create.append("code360_sections")

        if not tables_to_create:
            print("\n✓ All Legal Trinity tables already exist!")
            print("  - code360_municipalities")
            print("  - code360_sections")
            return True

        print(f"\nCreating tables: {', '.join(tables_to_create)}")

        # Create tables
        try:
            from sqlalchemy import text

            if "code360_municipalities" in tables_to_create:
                db.session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS code360_municipalities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        state VARCHAR(2) NOT NULL,
                        county VARCHAR(100),
                        name VARCHAR(200) NOT NULL,
                        provider VARCHAR(50) DEFAULT 'ecode360',
                        base_url VARCHAR(500),
                        api_key VARCHAR(200),
                        enabled BOOLEAN DEFAULT 1,
                        last_sync DATETIME,
                        code_version VARCHAR(50),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(state, county, name)
                    )
                """
                    )
                )
                db.session.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_muni_state 
                    ON code360_municipalities(state)
                """
                    )
                )
                db.session.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_muni_name 
                    ON code360_municipalities(name)
                """
                    )
                )
                db.session.commit()
                print("  ✓ Created code360_municipalities table with indexes")

            if "code360_sections" in tables_to_create:
                db.session.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS code360_sections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        municipality_id INTEGER NOT NULL,
                        chapter VARCHAR(50),
                        section_number VARCHAR(100) NOT NULL,
                        title VARCHAR(500),
                        text TEXT NOT NULL,
                        effective_date DATE,
                        source_url VARCHAR(500),
                        parent_section VARCHAR(100),
                        sha256 VARCHAR(64),
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (municipality_id) REFERENCES code360_municipalities(id),
                        UNIQUE(municipality_id, section_number)
                    )
                """
                    )
                )
                db.session.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_section_muni 
                    ON code360_sections(municipality_id)
                """
                    )
                )
                db.session.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_section_chapter 
                    ON code360_sections(chapter)
                """
                    )
                )
                db.session.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_section_number 
                    ON code360_sections(section_number)
                """
                    )
                )
                db.session.commit()
                print("  ✓ Created code360_sections table with indexes")

            # Try to create FTS table (SQLite specific)
            try:
                db.session.execute(
                    text(
                        """
                    CREATE VIRTUAL TABLE IF NOT EXISTS code360_fts USING fts5(
                        state,
                        county,
                        municipality,
                        chapter,
                        section_number,
                        title,
                        text,
                        content='code360_sections',
                        content_rowid='id'
                    )
                """
                    )
                )
                db.session.commit()
                print("  ✓ Created code360_fts full-text search table")
            except Exception as e:
                print(f"  ⚠ FTS table not created (may not be SQLite): {e}")

            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)

            print("\nLegal Trinity API endpoints now available:")
            print("  POST   /api/v1/trinity/search           - Search all government levels")
            print("  POST   /api/v1/trinity/search/federal   - Search federal law only")
            print("  POST   /api/v1/trinity/search/state/<code> - Search state law")
            print("  POST   /api/v1/trinity/search/local     - Search municipal codes")
            print("  POST   /api/v1/trinity/municipality     - Add a municipality")
            print("  GET    /api/v1/trinity/municipalities   - List municipalities")
            print("  POST   /api/v1/trinity/sync/<id>        - Sync municipality codes")
            print("  POST   /api/v1/trinity/analyze          - Analyze evidence against law")
            print("  GET    /api/v1/trinity/jurisdictions    - Get jurisdiction info")
            print("  POST   /api/v1/trinity/discover         - Discover municipality code source")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


def seed_sample_municipalities():
    """Seed some sample NJ municipalities"""
    from sqlalchemy import text

    from app import app, db

    sample_municipalities = [
        ("NJ", "Atlantic", "Atlantic City", "ecode360", "https://ecode360.com/AT0927"),
        ("NJ", "Ocean", "Toms River", "ecode360", "https://ecode360.com/TO0948"),
        ("NJ", "Camden", "Camden", "ecode360", "https://ecode360.com/CA0604"),
        ("NJ", "Essex", "Newark", "municode", "https://library.municode.com/nj/newark"),
        ("NJ", "Hudson", "Jersey City", "municode", "https://library.municode.com/nj/jersey_city"),
        ("NJ", "Bergen", "Hackensack", "ecode360", "https://ecode360.com/HA0634"),
    ]

    with app.app_context():
        print("\nSeeding sample municipalities...")

        for state, county, name, provider, url in sample_municipalities:
            try:
                db.session.execute(
                    text(
                        """
                    INSERT OR IGNORE INTO code360_municipalities 
                        (state, county, name, provider, base_url, enabled)
                    VALUES (?, ?, ?, ?, ?, 1)
                """
                    ),
                    (state, county, name, provider, url),
                )
            except Exception as e:
                print(f"  ⚠ Could not add {name}: {e}")

        db.session.commit()
        print("  ✓ Sample municipalities seeded")


def verify_tables():
    """Verify tables were created correctly"""
    from app import app, db

    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print("\nVerifying tables...")
        required = ["code360_municipalities", "code360_sections"]

        all_present = True
        for table in required:
            if table in tables:
                columns = [c["name"] for c in inspector.get_columns(table)]
                print(f"  ✓ {table} ({len(columns)} columns)")
            else:
                print(f"  ✗ {table} - MISSING")
                all_present = False

        # Check for FTS
        if "code360_fts" in tables:
            print("  ✓ code360_fts (FTS5 enabled)")
        else:
            print("  ⚠ code360_fts not present (FTS disabled)")

        return all_present


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Legal Trinity Database Migration")
    parser.add_argument("--seed", action="store_true", help="Seed sample municipalities")
    args = parser.parse_args()

    success = run_migration()

    if success:
        verify_tables()

        if args.seed:
            seed_sample_municipalities()

    sys.exit(0 if success else 1)
