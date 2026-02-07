# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

import os
import sqlite3

db_path = "instance/Evident.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")

    conn.close()
else:
    print(f"Database {db_path} does not exist")
