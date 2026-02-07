from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Municipal Code Service
Manages municipal ordinances (Code 360 and similar systems)
"""

import hashlib
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).parent / "instance" / "Evident_legal.db"

CORE_NJ_COUNTIES = [
    "Atlantic",
    "Ocean",
    "Cape May",
    "Burlington",
    "Camden",
    "Gloucester",
    "Salem",
    "Cumberland",
    "Mercer",
]


@dataclass
class MuniSource:
    id: int
    state: str
    county: str
    municipality: str
Optional[provider: str]
Optional[base_url: str]


class MunicipalCodeService:
    """Adapter to ingest legal documents into retrieval system"""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _sha256_text(text: str) -> str:
        normalized = " ".join(text.split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def ensure_source(
        self,
        county: str,
        municipality: str,
Optional[provider: str] = "eCode360",
Optional[base_url: str] = None,
    ) -> MuniSource:
        """Ensure municipal source exists, create if not"""
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO muni_sources(state, county, municipality, provider, base_url)
                VALUES('NJ', ?, ?, ?, ?)
                ON CONFLICT(state, county, municipality) DO UPDATE SET
                  provider=excluded.provider,
                  base_url=COALESCE(excluded.base_url, muni_sources.base_url)
                """,
                (county, municipality, provider, base_url),
            )
            row = conn.execute(
                "SELECT * FROM muni_sources WHERE state='NJ' AND county=? AND municipality=?",
                (county, municipality),
            ).fetchone()
            return MuniSource(
                id=row["id"],
                state=row["state"],
                county=row["county"],
                municipality=row["municipality"],
                provider=row["provider"],
                base_url=row["base_url"],
            )

    def upsert_section(
        self,
        source_id: int,
        section_citation: str,
        text: str,
Optional[title: str] = None,
Optional[source_url: str] = None,
Optional[effective_date: str] = None,
Optional[last_updated: str] = None,
Optional[section_path: str] = None,
    ) -> int:
        """Insert or update a municipal code section"""
        sha = self._sha256_text(text)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO muni_code_sections(
                  source_id, section_citation, section_path, title, text,
                  effective_date, last_updated, source_url, sha256
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, section_citation) DO UPDATE SET
                  section_path=COALESCE(excluded.section_path, muni_code_sections.section_path),
                  title=COALESCE(excluded.title, muni_code_sections.title),
                  text=excluded.text,
                  effective_date=COALESCE(excluded.effective_date, muni_code_sections.effective_date),
                  last_updated=COALESCE(excluded.last_updated, muni_code_sections.last_updated),
                  source_url=COALESCE(excluded.source_url, muni_code_sections.source_url),
                  sha256=excluded.sha256,
                  retrieved_at=datetime('now')
                """,
                (
                    source_id,
                    section_citation,
                    section_path,
                    title,
                    text,
                    effective_date,
                    last_updated,
                    source_url,
                    sha,
                ),
            )

            sec_row = conn.execute(
                "SELECT id, section_citation, title, text FROM muni_code_sections WHERE source_id=? AND section_citation=?",
                (source_id, section_citation),
            ).fetchone()

            # Write to FTS table (contentless)
            try:
                conn.execute(
                    """
                    INSERT INTO muni_fts(county, municipality, section_citation, title, text)
                    SELECT s.county, s.municipality, ?, ?, ?
                    FROM muni_sources s WHERE s.id=?
                    """,
                    (section_citation, title or "", text, source_id),
                )
            except sqlite3.OperationalError:
                # muni_fts not created; ignore
                pass

            return int(sec_row["id"])

    def seed_core_counties(
Optional[self, municipalities_by_county: dict[str, Iterable[str]]] = None
    ) -> None:
        """
        Seeds muni_sources rows for core NJ counties.
        Pass municipalities_by_county to also seed known municipalities.
        """
        municipalities_by_county = municipalities_by_county or {}

        with self._conn() as conn:
            for county in CORE_NJ_COUNTIES:
                munis = list(municipalities_by_county.get(county, []))
                if not munis:
                    # Skip if no municipalities provided
                    continue

                for muni in munis:
                    conn.execute(
                        """
                        INSERT INTO muni_sources(state, county, municipality, provider, base_url)
                        VALUES('NJ', ?, ?, 'eCode360', NULL)
                        ON CONFLICT(state, county, municipality) DO NOTHING
                        """,
                        (county, muni),
                    )

    def search(
        self,
        query: str,
Optional[county: str] = None,
Optional[municipality: str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search municipal codes using FTS or fallback to LIKE"""
        with self._conn() as conn:
            # Prefer FTS
            try:
                sql = """
                    SELECT rowid AS id, county, municipality, section_citation, title, 
                           snippet(muni_fts, 4, '[', ']', '…', 12) AS snippet 
                    FROM muni_fts 
                    WHERE muni_fts MATCH ?
                """
                args = [query]
                if county:
                    sql += " AND county=?"
                    args.append(county)
                if municipality:
                    sql += " AND municipality=?"
                    args.append(municipality)
                sql += " LIMIT ?"
                args.append(limit)
                rows = conn.execute(sql, args).fetchall()
                return [dict(r) for r in rows]
            except sqlite3.OperationalError:
                # Fallback LIKE
                sql = """
                SELECT c.id, s.county, s.municipality, c.section_citation, c.title,
                       substr(c.text, 1, 280) AS snippet, c.source_url
                FROM muni_code_sections c
                JOIN muni_sources s ON s.id=c.source_id
                WHERE (c.text LIKE ? OR c.title LIKE ? OR c.section_citation LIKE ?)
                """
                args = [f"%{query}%", f"%{query}%", f"%{query}%"]
                if county:
                    sql += " AND s.county=?"
                    args.append(county)
                if municipality:
                    sql += " AND s.municipality=?"
                    args.append(municipality)
                sql += " ORDER BY c.retrieved_at DESC LIMIT ?"
                args.append(limit)
                rows = conn.execute(sql, args).fetchall()
                return [dict(r) for r in rows]