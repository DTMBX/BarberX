# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import os
import sqlite3

db_path = "instance/Evident.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table schema
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()

    print("\n" + "=" * 80)
    print("USERS TABLE SCHEMA")
    print("=" * 80)

    column_names = [col[1] for col in columns]
    print(f"\nColumn count: {len(columns)}")
    print(f"Column names: {', '.join(column_names)}")
    print(f"\nHas 'role' column: {'role' in column_names}")

    print("\nDetailed schema:")
    for col in columns:
        cid, name, ctype, notnull, default, pk = col
        print(
            f"  [{cid}] {name:20} {ctype:15} {'NOT NULL' if notnull else '':<10} default={default}"
        )

    print("\n" + "=" * 80)

    conn.close()
else:
    print(f"Database {db_path} does not exist")
