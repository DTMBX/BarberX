"""
Citation Persistence Service
Tracks which documents/pages were cited in each analysis
"""

import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .retrieval_service import Passage

DB_PATH = Path(__file__).parent / "instance" / "Evident_legal.db"


@dataclass
class Citation:
    """Stored citation record"""

    id: int
    analysis_id: str
    document_id: str
    page_number: int
    text_start: int
    text_end: int
    snippet: str
    citation_rank: int
    created_at: str


class CitationService:
    """Persist and retrieve citations for analyses"""

    def __init__(self, db_path: Union[str, Path] = DB_PATH):
        self.db_path = Path(db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def persist_citations(self, analysis_id: Optional[str], passages: List[Passage]) -> str:
        """
        Store citations for an analysis

        Args:
            analysis_id: Analysis/chat session ID (generates if None)
            passages: List of passages that were cited

        Returns:
            analysis_id
        """
        if not analysis_id:
            analysis_id = f"analysis_{uuid.uuid4().hex[:16]}"

        with self._conn() as conn:
            for rank, passage in enumerate(passages, 1):
                conn.execute(
                    """
                    INSERT INTO citations (
                        analysis_id, document_id, page_number,
                        text_start, text_end, snippet, citation_rank
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analysis_id,
                        passage.document_id,
                        passage.page_number,
                        passage.text_start,
                        passage.text_end,
                        passage.snippet,
                        rank,
                    ),
                )

            conn.commit()

        return analysis_id

    def get_citations(self, analysis_id: str) -> List[Citation]:
        """Get all citations for an analysis"""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM citations
                WHERE analysis_id = ?
                ORDER BY citation_rank
                """,
                (analysis_id,),
            ).fetchall()

            return [
                Citation(
                    id=row["id"],
                    analysis_id=row["analysis_id"],
                    document_id=row["document_id"],
                    page_number=row["page_number"],
                    text_start=row["text_start"],
                    text_end=row["text_end"],
                    snippet=row["snippet"],
                    citation_rank=row["citation_rank"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def get_citations_by_document(self, document_id: str) -> List[Citation]:
        """Get all citations referencing a specific document"""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM citations
                WHERE document_id = ?
                ORDER BY created_at DESC
                """,
                (document_id,),
            ).fetchall()

            return [
                Citation(
                    id=row["id"],
                    analysis_id=row["analysis_id"],
                    document_id=row["document_id"],
                    page_number=row["page_number"],
                    text_start=row["text_start"],
                    text_end=row["text_end"],
                    snippet=row["snippet"],
                    citation_rank=row["citation_rank"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def get_citation_stats(self, document_id: str) -> Dict[str, Any]:
        """Get citation statistics for a document"""
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_citations,
                    COUNT(DISTINCT analysis_id) as analyses_count,
                    MIN(created_at) as first_cited,
                    MAX(created_at) as last_cited
                FROM citations
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

            return dict(row) if row else {}


