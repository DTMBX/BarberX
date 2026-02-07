# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""Initialize legal retrieval database"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "instance" / "Evident_legal.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_legal_db():
    """Create tables in Evident_legal.db"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        schema_sql = SCHEMA_PATH.read_text()
        conn.executescript(schema_sql)

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"✓ Initialized {DB_PATH}")
        print(f"✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")

        return tables


if __name__ == "__main__":
    init_legal_db()
