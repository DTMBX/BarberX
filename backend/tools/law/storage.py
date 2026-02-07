from __future__ import annotations
from typing import Optional

import sqlite3
from pathlib import Path


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    # Create tables idempotently
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS law_documents(
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            source_key TEXT UNIQUE,
            jurisdiction TEXT,
            doc_type TEXT,
            title TEXT,
            court TEXT,
            published_date TEXT,
            captured_at_utc TEXT,
            raw_sha256 TEXT,
            canonical_sha256 TEXT,
            raw_path TEXT,
            canonical_path TEXT,
            license TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_law_documents_source_key ON law_documents(source, source_key);

        -- FTS5 table for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS law_fts USING fts5(
            doc_id UNINDEXED, title, court, canonical_text
        );

        CREATE TABLE IF NOT EXISTS citations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_doc_id INTEGER,
            cite_text TEXT,
            normalized_cite TEXT,
            start_offset INTEGER,
            end_offset INTEGER,
            target_hint TEXT,
            pinpoint TEXT
        );

        CREATE TABLE IF NOT EXISTS provenance_events(
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            event_type TEXT,
            tool_versions_json TEXT,
            inputs_sha256 TEXT,
            outputs_sha256 TEXT,
            timestamp_utc TEXT
        );
        """
    )
    conn.commit()
    return conn


Optional[def get_conn(db_path: Path] = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = Path.cwd() / "backend" / "tools" / "law" / "law.db"
    return init_db(db_path)