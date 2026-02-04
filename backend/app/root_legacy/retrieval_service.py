"""
Unified Retrieval Service
Provides FTS5 BM25-ranked retrieval across all document sources
"""

import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

DB_PATH = Path(__file__).parent / "instance" / "Evident_legal.db"


@dataclass
class Passage:
    """Retrieved passage with full provenance"""

    document_id: str
    sha256: str
    filename: str
    storage_path_original: str
    page_number: int
    text_start: int
    text_end: int
    snippet: str
    score: float
    source_system: str  # 'legal_library', 'muni_code', 'bwc'
    document_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return asdict(self)


class RetrievalService:
    """Unified retrieval service using FTS5"""

    def __init__(self, db_path: Union[str, Path] = DB_PATH):
        self.db_path = Path(db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def retrieve(
        self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 5
    ) -> List[Passage]:
        """
        Retrieve passages using FTS5 BM25 ranking

        Args:
            query: Search query
            filters: Optional filters (source_system, document_type, etc.)
            top_k: Number of results to return

        Returns:
            List of Passage objects ranked by relevance
        """
        filters = filters or {}

        with self._conn() as conn:
            # Build FTS5 query
            # FTS5 MATCH query with proper escaping
            fts_query = self._prepare_fts_query(query)

            # Base query using FTS5 with BM25 ranking
            sql = """
                SELECT 
                    fts.document_id,
                    fts.page_number,
                    p.text_content,
                    d.sha256,
                    d.filename,
                    d.storage_path_original,
                    d.source_system,
                    d.document_type,
                    d.metadata,
                    bm25(document_fts) AS score
                FROM document_fts fts
                JOIN document_pages p ON p.id = fts.rowid
                JOIN documents d ON d.document_id = fts.document_id
                WHERE document_fts MATCH ?
            """

            params = [fts_query]

            # Apply filters
            if filters.get("source_system"):
                sql += " AND d.source_system = ?"
                params.append(filters["source_system"])

            if filters.get("document_type"):
                sql += " AND d.document_type = ?"
                params.append(filters["document_type"])

            if filters.get("document_id"):
                sql += " AND d.document_id = ?"
                params.append(filters["document_id"])

            # Order by BM25 score (lower is better in FTS5)
            sql += " ORDER BY score LIMIT ?"
            params.append(top_k)

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            passages = []
            for row in rows:
                # Extract snippet with offsets
                snippet, text_start, text_end = self._extract_snippet(row["text_content"], query)

                # Parse metadata if present
                metadata = None
                if row["metadata"]:
                    try:
                        metadata = json.loads(row["metadata"])
                    except json.JSONDecodeError:
                        pass

                passage = Passage(
                    document_id=row["document_id"],
                    sha256=row["sha256"],
                    filename=row["filename"],
                    storage_path_original=row["storage_path_original"],
                    page_number=row["page_number"],
                    text_start=text_start,
                    text_end=text_end,
                    snippet=snippet,
                    score=abs(row["score"]),  # Convert BM25 score to positive
                    source_system=row["source_system"],
                    document_type=row["document_type"],
                    metadata=metadata,
                )
                passages.append(passage)

            return passages

    def _prepare_fts_query(self, query: str) -> str:
        """Prepare query for FTS5 MATCH"""
        # Remove special characters that might break FTS5
        # Keep phrases in quotes
        cleaned = re.sub(r"[^\w\s\"]", " ", query)
        # Collapse whitespace
        cleaned = " ".join(cleaned.split())
        return cleaned

    def _extract_snippet(
        self, text: str, query: str, context_chars: int = 150
    ) -> tuple[str, int, int]:
        """
        Extract snippet around query match with character offsets

        Returns:
            (snippet, text_start, text_end)
        """
        # Find first occurrence of any query term
        terms = query.lower().split()
        text_lower = text.lower()

        best_pos = -1
        for term in terms:
            pos = text_lower.find(term)
            if pos != -1 and (best_pos == -1 or pos < best_pos):
                best_pos = pos

        if best_pos == -1:
            # No match found, return beginning
            snippet = text[: context_chars * 2].strip()
            return snippet + "...", 0, len(snippet)

        # Extract context around match
        start = max(0, best_pos - context_chars)
        end = min(len(text), best_pos + context_chars)

        snippet = text[start:end].strip()

        # Add ellipsis
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet, start, end

    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get full document metadata"""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()

            if not row:
                return None

            metadata = None
            if row["metadata"]:
                try:
                    metadata = json.loads(row["metadata"])
                except json.JSONDecodeError:
                    pass

            return {
                "document_id": row["document_id"],
                "sha256": row["sha256"],
                "filename": row["filename"],
                "storage_path_original": row["storage_path_original"],
                "source_system": row["source_system"],
                "document_type": row["document_type"],
                "metadata": metadata,
                "indexed_at": row["indexed_at"],
                "created_at": row["created_at"],
            }

    def get_page_content(self, document_id: str, page_number: int) -> Optional[str]:
        """Get full text of a specific page"""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT text_content FROM document_pages WHERE document_id = ? AND page_number = ?",
                (document_id, page_number),
            ).fetchone()

            return row["text_content"] if row else None


