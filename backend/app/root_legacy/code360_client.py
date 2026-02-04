"""
Code360 API Client
Universal municipal code integration via eCode360, GeneralCode, and other providers

Enables Evident users to integrate ANY municipality's code into their legal research.
"""

import hashlib
import logging
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CodeProvider(Enum):
    """Municipal code providers"""

    ECODE360 = "ecode360"  # General Code / eCode360
    MUNICODE = "municode"  # Municode (American Legal Publishing)
    AMERICAN_LEGAL = "american_legal"  # American Legal Publishing
    STERLING = "sterling"  # Sterling Codifiers
    QUALITY_CODE = "quality_code"  # Quality Code Publishing
    CUSTOM = "custom"  # Custom/direct URL


@dataclass
class Municipality:
    """Represents a municipality with code integration"""

    id: Optional[int] = None
    state: str = ""
    county: str = ""
    name: str = ""  # City/Township/Borough name
    provider: CodeProvider = CodeProvider.ECODE360
    base_url: str = ""
    api_key: Optional[str] = None
    enabled: bool = True
    last_sync: Optional[datetime] = None
    code_version: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.name}, {self.county} County, {self.state}"

    @property
    def slug(self) -> str:
        """URL-safe identifier"""
        return f"{self.state.lower()}-{self.county.lower()}-{self.name.lower()}".replace(" ", "-")


@dataclass
class CodeSection:
    """A section of municipal code"""

    id: Optional[int] = None
    municipality_id: int = 0
    chapter: str = ""
    section_number: str = ""
    title: str = ""
    text: str = ""
    effective_date: Optional[datetime] = None
    source_url: str = ""
    parent_section: Optional[str] = None
    children: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    sha256: str = ""

    def __post_init__(self):
        if self.text and not self.sha256:
            self.sha256 = hashlib.sha256(self.text.encode()).hexdigest()


class Code360Client:
    """
    Client for Code360/eCode360 municipal code API

    Code360 (by General Code) hosts municipal codes for thousands of municipalities.
    Base URL pattern: https://ecode360.com/[municipality-id]

    Also supports:
    - Municode: https://library.municode.com/[state]/[municipality]
    - American Legal: https://codelibrary.amlegal.com/codes/[municipality]
    """

    PROVIDER_PATTERNS = {
        CodeProvider.ECODE360: {
            "search_url": "https://ecode360.com/search",
            "base_pattern": "https://ecode360.com/{municipality_id}",
            "toc_pattern": "https://ecode360.com/{municipality_id}#toc",
        },
        CodeProvider.MUNICODE: {
            "search_url": "https://library.municode.com/",
            "base_pattern": "https://library.municode.com/{state}/{municipality}",
        },
        CodeProvider.AMERICAN_LEGAL: {
            "search_url": "https://codelibrary.amlegal.com/",
            "base_pattern": "https://codelibrary.amlegal.com/codes/{municipality}",
        },
    }

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).parent / "instance" / "Evident_legal.db"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Evident Legal Research/1.0 (legal research tool)",
                "Accept": "application/json, text/html",
            }
        )
        self._rate_limit_delay = 1.0  # seconds between requests
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ═══════════════════════════════════════════════════════════════════════════
    # MUNICIPALITY DISCOVERY
    # ═══════════════════════════════════════════════════════════════════════════

    def discover_municipality(
        self, state: str, municipality_name: str, county: Optional[str] = None
    ) -> Optional[Municipality]:
        """
        Discover a municipality's code source automatically

        Tries multiple providers to find the municipality's online code.

        Args:
            state: Two-letter state code (e.g., "NJ", "CA")
            municipality_name: Name of city/township/borough
            county: Optional county name for disambiguation

        Returns:
            Municipality object if found, None otherwise
        """
        state = state.upper()
        municipality_name = municipality_name.strip()

        # Try eCode360 first (most common for NJ/PA/NY)
        result = self._discover_ecode360(state, municipality_name)
        if result:
            result.county = county or ""
            return result

        # Try Municode
        result = self._discover_municode(state, municipality_name)
        if result:
            result.county = county or ""
            return result

        # Try American Legal
        result = self._discover_american_legal(state, municipality_name)
        if result:
            result.county = county or ""
            return result

        logger.warning(f"Could not discover code source for {municipality_name}, {state}")
        return None

    def _discover_ecode360(self, state: str, name: str) -> Optional[Municipality]:
        """Search eCode360 for municipality"""
        self._rate_limit()

        try:
            # eCode360 search endpoint
            response = self.session.get(
                "https://ecode360.com/search",
                params={"q": f"{name} {state}", "type": "codes"},
                timeout=15,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for municipality links
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                # eCode360 URLs look like: https://ecode360.com/12345678
                if re.match(r"https?://ecode360\.com/\d+", href):
                    # Verify it's the right municipality
                    link_text = link.get_text().lower()
                    if name.lower() in link_text and state.lower() in link_text:
                        return Municipality(
                            state=state,
                            name=name,
                            provider=CodeProvider.ECODE360,
                            base_url=href,
                            enabled=True,
                        )

        except Exception as e:
            logger.error(f"eCode360 discovery error: {e}")

        return None

    def _discover_municode(self, state: str, name: str) -> Optional[Municipality]:
        """Search Municode for municipality"""
        self._rate_limit()

        try:
            # Municode URL pattern
            state_slug = state.lower()
            name_slug = name.lower().replace(" ", "_")

            url = f"https://library.municode.com/{state_slug}/{name_slug}"
            response = self.session.head(url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                return Municipality(
                    state=state,
                    name=name,
                    provider=CodeProvider.MUNICODE,
                    base_url=url,
                    enabled=True,
                )

        except Exception as e:
            logger.debug(f"Municode discovery: {e}")

        return None

    def _discover_american_legal(self, state: str, name: str) -> Optional[Municipality]:
        """Search American Legal for municipality"""
        # Similar pattern to Municode
        return None  # TODO: Implement

    # ═══════════════════════════════════════════════════════════════════════════
    # CODE RETRIEVAL
    # ═══════════════════════════════════════════════════════════════════════════

    def fetch_table_of_contents(self, municipality: Municipality) -> List[Dict]:
        """
        Fetch the table of contents (chapter list) for a municipality's code

        Returns list of chapters with their sections
        """
        self._rate_limit()

        if municipality.provider == CodeProvider.ECODE360:
            return self._fetch_ecode360_toc(municipality)
        elif municipality.provider == CodeProvider.MUNICODE:
            return self._fetch_municode_toc(municipality)
        else:
            return self._fetch_generic_toc(municipality)

    def _fetch_ecode360_toc(self, municipality: Municipality) -> List[Dict]:
        """Fetch TOC from eCode360"""
        toc = []

        try:
            # eCode360 TOC is usually on the main page
            response = self.session.get(municipality.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for chapter links
            for item in soup.find_all(
                ["li", "div"], class_=re.compile(r"(chapter|article|part)", re.I)
            ):
                link = item.find("a", href=True)
                if link:
                    chapter_title = link.get_text().strip()
                    chapter_url = urljoin(municipality.base_url, link["href"])

                    # Extract chapter number
                    match = re.search(
                        r"(?:Chapter|Ch\.?|Art\.?)\s*(\d+[A-Za-z]?)", chapter_title, re.I
                    )
                    chapter_num = match.group(1) if match else ""

                    toc.append(
                        {
                            "chapter_number": chapter_num,
                            "title": chapter_title,
                            "url": chapter_url,
                            "sections": [],
                        }
                    )

        except Exception as e:
            logger.error(f"Error fetching eCode360 TOC: {e}")

        return toc

    def _fetch_municode_toc(self, municipality: Municipality) -> List[Dict]:
        """Fetch TOC from Municode"""
        # Municode has an API endpoint
        return []  # TODO: Implement

    def _fetch_generic_toc(self, municipality: Municipality) -> List[Dict]:
        """Generic TOC fetch via HTML scraping"""
        return []

    def fetch_section(
        self, municipality: Municipality, section_number: str
    ) -> Optional[CodeSection]:
        """
        Fetch a specific section of municipal code

        Args:
            municipality: The municipality object
            section_number: Section citation (e.g., "15-3.2", "170-15A")

        Returns:
            CodeSection if found
        """
        self._rate_limit()

        if municipality.provider == CodeProvider.ECODE360:
            return self._fetch_ecode360_section(municipality, section_number)
        else:
            return self._fetch_generic_section(municipality, section_number)

    def _fetch_ecode360_section(
        self, municipality: Municipality, section_number: str
    ) -> Optional[CodeSection]:
        """Fetch section from eCode360"""

        try:
            # eCode360 search by section
            search_url = f"{municipality.base_url}"
            response = self.session.get(search_url, params={"s": section_number}, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find section content
            section_div = soup.find("div", class_=re.compile(r"section", re.I))
            if section_div:
                title_elem = section_div.find(["h1", "h2", "h3", "h4"])
                text_elem = section_div.find("div", class_=re.compile(r"(content|text|body)", re.I))

                return CodeSection(
                    municipality_id=municipality.id or 0,
                    section_number=section_number,
                    title=title_elem.get_text().strip() if title_elem else "",
                    text=text_elem.get_text().strip() if text_elem else "",
                    source_url=response.url,
                    last_updated=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error fetching eCode360 section: {e}")

        return None

    def _fetch_generic_section(
        self, municipality: Municipality, section_number: str
    ) -> Optional[CodeSection]:
        """Generic section fetch"""
        return None

    def sync_municipality(
        self, municipality: Municipality, chapters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Sync all or selected chapters from a municipality's code

        Args:
            municipality: Municipality to sync
            chapters: Optional list of chapter numbers to sync (None = all)

        Returns:
            Sync statistics
        """
        stats = {
            "municipality": municipality.full_name,
            "sections_added": 0,
            "sections_updated": 0,
            "sections_unchanged": 0,
            "errors": [],
            "started_at": datetime.utcnow().isoformat(),
        }

        # Get TOC
        toc = self.fetch_table_of_contents(municipality)

        if chapters:
            toc = [c for c in toc if c["chapter_number"] in chapters]

        for chapter in toc:
            try:
                # Fetch chapter content
                self._rate_limit()

                response = self.session.get(chapter["url"], timeout=15)
                response.raise_for_status()

                # Parse sections
                soup = BeautifulSoup(response.content, "html.parser")

                for section_elem in soup.find_all("div", class_=re.compile(r"section", re.I)):
                    try:
                        section = self._parse_section_element(section_elem, municipality, chapter)
                        if section:
                            result = self._save_section(section)
                            stats[f"sections_{result}"] += 1
                    except Exception as e:
                        stats["errors"].append(f"Section parse error: {e}")

            except Exception as e:
                stats["errors"].append(f"Chapter {chapter['chapter_number']} error: {e}")

        stats["completed_at"] = datetime.utcnow().isoformat()

        # Update municipality last_sync
        municipality.last_sync = datetime.utcnow()
        self._save_municipality(municipality)

        return stats

    def _parse_section_element(
        self, elem, municipality: Municipality, chapter: Dict
    ) -> Optional[CodeSection]:
        """Parse a section HTML element into CodeSection"""

        title_elem = elem.find(["h1", "h2", "h3", "h4", "h5"])
        text_parts = []

        for p in elem.find_all(["p", "div"], class_=re.compile(r"(text|content|body)", re.I)):
            text_parts.append(p.get_text().strip())

        if not text_parts:
            text_parts = [elem.get_text().strip()]

        section_text = "\n\n".join(text_parts)

        # Extract section number from title
        title_text = title_elem.get_text().strip() if title_elem else ""
        section_match = re.search(r"§?\s*([\d\-\.A-Za-z]+)", title_text)
        section_num = section_match.group(1) if section_match else ""

        if not section_num or not section_text:
            return None

        return CodeSection(
            municipality_id=municipality.id or 0,
            chapter=chapter["chapter_number"],
            section_number=section_num,
            title=title_text,
            text=section_text,
            source_url=chapter.get("url", ""),
            last_updated=datetime.utcnow(),
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def _save_municipality(self, municipality: Municipality) -> int:
        """Save municipality to database"""
        with self._get_conn() as conn:
            if municipality.id:
                conn.execute(
                    """
                    UPDATE code360_municipalities SET
                        state=?, county=?, name=?, provider=?, base_url=?,
                        enabled=?, last_sync=?, code_version=?
                    WHERE id=?
                """,
                    (
                        municipality.state,
                        municipality.county,
                        municipality.name,
                        municipality.provider.value,
                        municipality.base_url,
                        municipality.enabled,
                        municipality.last_sync.isoformat() if municipality.last_sync else None,
                        municipality.code_version,
                        municipality.id,
                    ),
                )
                return municipality.id
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO code360_municipalities 
                        (state, county, name, provider, base_url, enabled, last_sync, code_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        municipality.state,
                        municipality.county,
                        municipality.name,
                        municipality.provider.value,
                        municipality.base_url,
                        municipality.enabled,
                        municipality.last_sync.isoformat() if municipality.last_sync else None,
                        municipality.code_version,
                    ),
                )
                return cursor.lastrowid

    def _save_section(self, section: CodeSection) -> str:
        """Save code section to database, returns 'added', 'updated', or 'unchanged'"""
        with self._get_conn() as conn:
            existing = conn.execute(
                """
                SELECT id, sha256 FROM code360_sections 
                WHERE municipality_id=? AND section_number=?
            """,
                (section.municipality_id, section.section_number),
            ).fetchone()

            if existing:
                if existing["sha256"] == section.sha256:
                    return "unchanged"
                else:
                    conn.execute(
                        """
                        UPDATE code360_sections SET
                            chapter=?, title=?, text=?, effective_date=?,
                            source_url=?, parent_section=?, sha256=?, last_updated=?
                        WHERE id=?
                    """,
                        (
                            section.chapter,
                            section.title,
                            section.text,
                            section.effective_date.isoformat() if section.effective_date else None,
                            section.source_url,
                            section.parent_section,
                            section.sha256,
                            datetime.utcnow().isoformat(),
                            existing["id"],
                        ),
                    )
                    return "updated"
            else:
                conn.execute(
                    """
                    INSERT INTO code360_sections 
                        (municipality_id, chapter, section_number, title, text,
                         effective_date, source_url, parent_section, sha256, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        section.municipality_id,
                        section.chapter,
                        section.section_number,
                        section.title,
                        section.text,
                        section.effective_date.isoformat() if section.effective_date else None,
                        section.source_url,
                        section.parent_section,
                        section.sha256,
                        datetime.utcnow().isoformat(),
                    ),
                )
                return "added"

    def get_municipality(self, municipality_id: int) -> Optional[Municipality]:
        """Get municipality by ID"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM code360_municipalities WHERE id=?", (municipality_id,)
            ).fetchone()

            if row:
                return Municipality(
                    id=row["id"],
                    state=row["state"],
                    county=row["county"],
                    name=row["name"],
                    provider=CodeProvider(row["provider"]),
                    base_url=row["base_url"],
                    enabled=bool(row["enabled"]),
                    last_sync=(
                        datetime.fromisoformat(row["last_sync"]) if row["last_sync"] else None
                    ),
                    code_version=row["code_version"],
                )
        return None

    def list_municipalities(
        self, state: Optional[str] = None, enabled_only: bool = True
    ) -> List[Municipality]:
        """List all integrated municipalities"""
        with self._get_conn() as conn:
            sql = "SELECT * FROM code360_municipalities WHERE 1=1"
            args = []

            if state:
                sql += " AND state=?"
                args.append(state.upper())

            if enabled_only:
                sql += " AND enabled=1"

            sql += " ORDER BY state, county, name"

            rows = conn.execute(sql, args).fetchall()

            return [
                Municipality(
                    id=row["id"],
                    state=row["state"],
                    county=row["county"],
                    name=row["name"],
                    provider=CodeProvider(row["provider"]),
                    base_url=row["base_url"],
                    enabled=bool(row["enabled"]),
                    last_sync=(
                        datetime.fromisoformat(row["last_sync"]) if row["last_sync"] else None
                    ),
                    code_version=row["code_version"],
                )
                for row in rows
            ]

    # ═══════════════════════════════════════════════════════════════════════════
    # SEARCH
    # ═══════════════════════════════════════════════════════════════════════════

    def search(
        self,
        query: str,
        state: Optional[str] = None,
        municipality_id: Optional[int] = None,
        chapter: Optional[str] = None,
        limit: int = 25,
    ) -> List[Dict]:
        """
        Search across all municipal codes

        Args:
            query: Search text
            state: Filter by state
            municipality_id: Filter by specific municipality
            chapter: Filter by chapter number
            limit: Maximum results

        Returns:
            List of matching sections with metadata
        """
        with self._get_conn() as conn:
            # Try FTS first
            try:
                sql = """
                    SELECT 
                        s.id, s.section_number, s.chapter, s.title,
                        snippet(code360_fts, 4, '[', ']', '…', 24) as snippet,
                        s.source_url, m.name as municipality, m.county, m.state
                    FROM code360_fts f
                    JOIN code360_sections s ON f.rowid = s.id
                    JOIN code360_municipalities m ON s.municipality_id = m.id
                    WHERE code360_fts MATCH ?
                """
                args = [query]

                if state:
                    sql += " AND m.state=?"
                    args.append(state.upper())

                if municipality_id:
                    sql += " AND m.id=?"
                    args.append(municipality_id)

                if chapter:
                    sql += " AND s.chapter=?"
                    args.append(chapter)

                sql += " LIMIT ?"
                args.append(limit)

                rows = conn.execute(sql, args).fetchall()
                return [dict(row) for row in rows]

            except sqlite3.OperationalError:
                # Fallback to LIKE search
                sql = """
                    SELECT 
                        s.id, s.section_number, s.chapter, s.title,
                        substr(s.text, 1, 300) as snippet,
                        s.source_url, m.name as municipality, m.county, m.state
                    FROM code360_sections s
                    JOIN code360_municipalities m ON s.municipality_id = m.id
                    WHERE (s.text LIKE ? OR s.title LIKE ? OR s.section_number LIKE ?)
                """
                query_like = f"%{query}%"
                args = [query_like, query_like, query_like]

                if state:
                    sql += " AND m.state=?"
                    args.append(state.upper())

                if municipality_id:
                    sql += " AND m.id=?"
                    args.append(municipality_id)

                if chapter:
                    sql += " AND s.chapter=?"
                    args.append(chapter)

                sql += " ORDER BY s.last_updated DESC LIMIT ?"
                args.append(limit)

                rows = conn.execute(sql, args).fetchall()
                return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def add_municipality(
    state: str, name: str, county: str = "", auto_discover: bool = True
) -> Optional[Municipality]:
    """
    Add a new municipality to Evident

    Example:
        add_municipality("NJ", "Atlantic City", "Atlantic")
        add_municipality("CA", "Los Angeles", "Los Angeles")
    """
    client = Code360Client()

    if auto_discover:
        municipality = client.discover_municipality(state, name, county)
        if municipality:
            municipality.id = client._save_municipality(municipality)
            return municipality

    # Manual creation if discovery fails
    municipality = Municipality(
        state=state.upper(),
        county=county,
        name=name,
        provider=CodeProvider.CUSTOM,
        enabled=False,  # Requires manual URL configuration
    )
    municipality.id = client._save_municipality(municipality)
    return municipality


def search_municipal_codes(
    query: str, state: Optional[str] = None, municipality: Optional[str] = None
) -> List[Dict]:
    """
    Search all integrated municipal codes

    Example:
        search_municipal_codes("parking violation", state="NJ")
        search_municipal_codes("noise ordinance", municipality="Atlantic City")
    """
    client = Code360Client()

    # If municipality name given, find the ID
    municipality_id = None
    if municipality:
        with client._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM code360_municipalities WHERE name LIKE ?", (f"%{municipality}%",)
            ).fetchone()
            if row:
                municipality_id = row["id"]

    return client.search(query, state=state, municipality_id=municipality_id)


