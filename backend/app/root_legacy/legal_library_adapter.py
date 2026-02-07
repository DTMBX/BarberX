from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Legal Library Adapter
Ingests documents and extracts pages into unified retrieval DB
"""

import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[WARN] PyPDF2 not available - PDF extraction disabled")

DB_PATH = Path(__file__).parent / "instance" / "Evident_legal.db"


class LegalLibraryAdapter:
    """Adapter to ingest legal documents into retrieval system"""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _sha256_file(filepath: Path) -> str:
        """Compute SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def ingest_pdf(
        self,
        filepath: Path | str,
        source_system: str = "legal_library",
        document_type: str = "case_law",
Optional[metadata: dict[str, Any]] = None,
    ) -> str:
        """
        Ingest PDF document and extract pages

        Args:
            filepath: Path to PDF file
            source_system: 'legal_library', 'muni_code', 'bwc'
            document_type: Type classification
            metadata: Additional metadata (case name, citation, etc.)

        Returns:
            document_id
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not installed - cannot extract PDF")

        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"PDF not found: {filepath}")

        # Generate document ID and hash
        document_id = f"{source_system}_{uuid.uuid4().hex[:12]}"
        sha256 = self._sha256_file(filepath)

        # Extract text from PDF
        pages = self._extract_pdf_pages(filepath)

        if not pages:
            raise ValueError(f"No text extracted from PDF: {filepath}")

        # Store document and pages
        with self._conn() as conn:
            # Insert document
            conn.execute(
                """
                INSERT INTO documents (
                    document_id, sha256, filename, storage_path_original,
                    source_system, document_type, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    sha256,
                    filepath.name,
                    str(filepath.absolute()),
                    source_system,
                    document_type,
                    json.dumps(metadata) if metadata else None,
                ),
            )

            # Insert pages (triggers will populate FTS)
            for page_num, text in pages.items():
                conn.execute(
                    """
                    INSERT INTO document_pages (document_id, page_number, text_content)
                    VALUES (?, ?, ?)
                    """,
                    (document_id, page_num, text),
                )

            conn.commit()

        return document_id

    def _extract_pdf_pages(self, filepath: Path) -> dict[int, str]:
        """Extract text from each page of PDF"""
        pages = {}

        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                for page_num in range(len(reader.pages)):
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()

                        # Clean up text
                        text = text.strip()

                        if text:  # Only store non-empty pages
                            pages[page_num + 1] = text  # 1-indexed
                    except Exception as e:
                        print(f"[WARN] Error extracting page {page_num + 1}: {e}")
                        continue

        except Exception as e:
            print(f"[ERROR] Failed to read PDF {filepath}: {e}")

        return pages

    def ingest_text_document(
        self,
        text: str,
        filename: str,
        source_system: str = "legal_library",
        document_type: str = "statute",
Optional[metadata: dict[str, Any]] = None,
        page_size: int = 5000,  # Characters per "page"
    ) -> str:
        """
        Ingest plain text document (split into pages)

        Args:
            text: Document text content
            filename: Logical filename
            source_system: Source system identifier
            document_type: Document type
            metadata: Additional metadata
            page_size: Characters per virtual page

        Returns:
            document_id
        """
        document_id = f"{source_system}_{uuid.uuid4().hex[:12]}"

        # Hash the text
        sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

        # Split into pages
        pages = {}
        page_num = 1

        for i in range(0, len(text), page_size):
            page_text = text[i : i + page_size].strip()
            if page_text:
                pages[page_num] = page_text
                page_num += 1

        # Store document and pages
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    document_id, sha256, filename, storage_path_original,
                    source_system, document_type, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    sha256,
                    filename,
                    f"text://{filename}",  # Virtual path
                    source_system,
                    document_type,
                    json.dumps(metadata) if metadata else None,
                ),
            )

            for page_num, page_text in pages.items():
                conn.execute(
                    """
                    INSERT INTO document_pages (document_id, page_number, text_content)
                    VALUES (?, ?, ?)
                    """,
                    (document_id, page_num, page_text),
                )

            conn.commit()

        return document_id

    def delete_document(self, document_id: str) -> bool:
        """Delete document and all its pages"""
        with self._conn() as conn:
            # Delete pages first (triggers will update FTS)
            conn.execute("DELETE FROM document_pages WHERE document_id = ?", (document_id,))

            # Delete document
            result = conn.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))

            conn.commit()
            return result.rowcount > 0

    def list_documents(
Optional[self, source_system: str] = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List ingested documents"""
        with self._conn() as conn:
            if source_system:
                rows = conn.execute(
                    """
                    SELECT document_id, filename, source_system, document_type,
                           indexed_at, created_at
                    FROM documents
                    WHERE source_system = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (source_system, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT document_id, filename, source_system, document_type,
                           indexed_at, created_at
                    FROM documents
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

            return [dict(row) for row in rows]