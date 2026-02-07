from __future__ import annotations
from typing import Optional

from datetime import datetime
from pathlib import Path

from ..blobs import write_blob
from ..citations import extract_citations
from ..normalize import canonicalize_bytes
from ..sources.courtlistener.client import CourtListenerClient
from ..storage import get_conn


class Ingestor:
    def __init__(self, db_path: Optional[Path] = None):
        self.conn = get_conn(db_path)

    def ingest_opinion(
        self,
        source: str,
        source_key: str,
        opinion_json: dict,
        tool_versions_json: str = "{}",
        idempotency_key: Optional[str] = None,
    ):
        # fetch content bytes and content_type via minimal client shape
        client = CourtListenerClient()
        content_bytes, content_type = client.fetch_opinion_content(opinion_json)

        raw_blob = write_blob(content_bytes, kind="raw")
        canonical_bytes, canonical_text = canonicalize_bytes(content_bytes, content_type)
        canonical_blob = write_blob(canonical_bytes, kind="canonical")

        # upsert law_documents by (source, source_key)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT doc_id FROM law_documents WHERE source = ? AND source_key = ?",
            (source, source_key),
        )
        row = cur.fetchone()
        now = datetime.utcnow().isoformat() + "Z"
        if row:
            doc_id = row[0]
            cur.execute(
                "UPDATE law_documents SET title = ?, court = ?, captured_at_utc = ?, raw_sha256 = ?, canonical_sha256 = ?, raw_path = ?, canonical_path = ? WHERE doc_id = ?",
                (
                    opinion_json.get("title"),
                    opinion_json.get("court"),
                    now,
                    raw_blob["sha256"],
                    canonical_blob["sha256"],
                    raw_blob["path"],
                    canonical_blob["path"],
                    doc_id,
                ),
            )
        else:
            cur.execute(
                "INSERT INTO law_documents(source, source_key, title, court, captured_at_utc, raw_sha256, canonical_sha256, raw_path, canonical_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    source,
                    source_key,
                    opinion_json.get("title"),
                    opinion_json.get("court"),
                    now,
                    raw_blob["sha256"],
                    canonical_blob["sha256"],
                    raw_blob["path"],
                    canonical_blob["path"],
                ),
            )
            doc_id = cur.lastrowid

        # update FTS
        cur.execute("DELETE FROM law_fts WHERE doc_id = ?", (doc_id,))
        cur.execute(
            "INSERT INTO law_fts(doc_id, title, court, canonical_text) VALUES (?, ?, ?, ?)",
            (
                doc_id,
                opinion_json.get("title") or "",
                opinion_json.get("court") or "",
                canonical_text,
            ),
        )

        # extract citations and persist deterministically
        cites = extract_citations(canonical_text)
        # clear existing
        cur.execute("DELETE FROM citations WHERE from_doc_id = ?", (doc_id,))
        for c in cites:
            cur.execute(
                "INSERT INTO citations(from_doc_id, cite_text, normalized_cite, start_offset, end_offset, target_hint, pinpoint) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    doc_id,
                    c["cite_text"],
                    c["normalized_cite"],
                    c["start_offset"],
                    c["end_offset"],
                    c.get("target_hint"),
                    c.get("pinpoint"),
                ),
            )

        # append provenance event if not already recorded for same inputs
        inputs_sha = raw_blob["sha256"]
        outputs_sha = canonical_blob["sha256"]
        cur.execute(
            "SELECT event_id FROM provenance_events WHERE doc_id = ? AND event_type = ? AND inputs_sha256 = ?",
            (doc_id, "ingest", inputs_sha),
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO provenance_events(doc_id, event_type, tool_versions_json, inputs_sha256, outputs_sha256, timestamp_utc) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, "ingest", tool_versions_json, inputs_sha, outputs_sha, now),
            )

        self.conn.commit()
        return doc_id
