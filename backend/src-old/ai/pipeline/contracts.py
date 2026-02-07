from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Pipeline Contracts - Stable interfaces for unified AI pipeline

These data contracts define the canonical format for all pipeline stages.
All adapters and services must produce/consume these types.

NON-NEGOTIABLE FIELDS FOR PROVENANCE:
- doc_id: Database primary key
- sha256: Content hash for deduplication
- storage_path_original: Path to immutable original file
- storage_path_processed: Path to OCR/repaired version (if exists)
- page_number: Page within document
- text_start, text_end: Character offsets for citation
- snippet: Actual text content
- source_system: Origin (app, bwc, legal_library)
- created_at: Timestamp
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SourceSystem(Enum):
    """Origin system that ingested the document"""

    APP = "app"
    BWC = "bwc"
    LEGAL_LIBRARY = "legal_library"
    BATCH_IMPORT = "batch_import"


class ExtractionMethod(Enum):
    """How text was extracted from document"""

    TEXT = "text"  # Native text layer
    OCR = "ocr"  # Full OCR
    HYBRID = "hybrid"  # Some pages text, some OCR
    FAILED = "failed"


@dataclass
class IngestResult:
    """
    Result of document ingestion (STEP 1 of pipeline)

    Guarantees:
    - Original file preserved at storage_path_original
    - SHA-256 computed for deduplication
    - Manifest file created
    """

    doc_id: int  # Database primary key
    sha256: str  # Content hash (64 hex chars)
    filename_original: str  # Original upload filename
    storage_path_original: str  # Absolute path to saved original
    file_size_bytes: int
    source_system: SourceSystem
    metadata: dict[str, any] = field(default_factory=dict)  # User-provided metadata
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Deduplication info
    is_duplicate: bool = False
Optional[duplicate_of_doc_id: int] = None


@dataclass
class PageExtraction:
    """Extracted text from a single page"""

    page_number: int  # 1-indexed
    text: str
    char_count: int
Optional[storage_path: str] = None  # Path to cached page text file
    extraction_method: ExtractionMethod = ExtractionMethod.TEXT
Optional[confidence_score: float] = None  # OCR confidence if applicable


@dataclass
class ExtractResult:
    """
    Result of text extraction (STEP 2 of pipeline)

    Guarantees:
    - Page-level text captured with offsets
    - OCR applied if text layer was missing/thin
    - Manifest updated with extraction metadata
    """

    doc_id: int
    sha256: str
    total_pages: int
    pages: list[PageExtraction]  # Page-level text with offsets

    # Extraction metadata
    text_layer_detected: bool  # Was native text present?
    extraction_method: ExtractionMethod  # How we got the text
    ocr_triggered: bool = False
Optional[storage_path_processed: str] = None  # Path to OCR'd PDF if created

    # Quality metrics
    total_chars: int = 0
    avg_chars_per_page: float = 0.0
    thin_pages: int = 0  # Pages with < threshold chars

    extracted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IndexResult:
    """
    Result of document indexing (STEP 3 of pipeline)

    Guarantees:
    - Pages inserted into document_pages table
    - FTS5 index updated for keyword search
    - Optional vector embeddings created
    """

    doc_id: int
    sha256: str
    pages_indexed: int

    # Index details
    keyword_index_updated: bool = False  # FTS5
    vector_index_updated: bool = False  # ChromaDB/FAISS

    # Quality metrics
    total_terms: int = 0  # Unique terms in keyword index
Optional[embedding_dimensions: int] = None

    indexed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Passage:
    """
    Citation-ready text passage from retrieval

    This is THE core data structure for grounded LLM analysis.
    Every passage must be traceable to source document + page + offsets.
    """

    # Document provenance (NON-NEGOTIABLE)
    document_id: int
    sha256: str
    filename: str
    storage_path_original: str
    source_system: SourceSystem

    # Page provenance (NON-NEGOTIABLE)
    page_number: int  # 1-indexed
    text_start: int  # Character offset within page
    text_end: int  # Character offset within page
    snippet: str  # Actual text content (with context)

    # Retrieval metadata
    score: float  # Relevance score (BM25, cosine similarity, etc.)
    match_type: str = "keyword"  # keyword, semantic, hybrid

    # Optional structured extraction
    entities: list[dict] = field(default_factory=list)  # NER results
    metadata: dict[str, any] = field(default_factory=dict)


@dataclass
class RetrieveResult:
    """
    Result of passage retrieval (STEP 4 of pipeline)

    Guarantees:
    - Returns passages, NOT whole documents
    - Every passage has citation metadata
    - Results ranked by relevance
    """

    query: str
    passages: list[Passage]
    total_matches: int

    # Retrieval strategy
    retrieval_method: str = "keyword"  # keyword, semantic, hybrid
    index_used: str = "fts5"  # fts5, chromadb, hybrid

    # Authority records (if legal research query)
    authority_citations: list[dict] = field(default_factory=list)

    retrieved_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CitationRecord:
    """
    Citation linking analysis output to source passage

    Persisted to database for audit trail.
    """

    analysis_id: int  # FK to analysis table
    document_id: int
    page_number: int
    text_start: int
    text_end: int
    snippet: str  # Cited text

    # Authority info (if legal citation)
Optional[authority_name: str] = None  # e.g., "Miranda v. Arizona"
Optional[authority_citation: str] = None  # e.g., "384 U.S. 436 (1966)"

    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnalysisResult:
    """
    Result of LLM analysis (STEP 5 of pipeline)

    Guarantees:
    - Analysis grounded in retrieved passages
    - Citations persisted to database
    - No hallucinated facts/cases
    """

    analysis_id: int  # Database primary key
    query: str
    response: str  # LLM output

    # Grounding data
    passages_used: list[Passage]  # Input passages sent to LLM
    citations: list[CitationRecord]  # Citations extracted from response

    # Authority records referenced
    authorities_cited: list[dict] = field(default_factory=list)

    # Metadata
    model: str = "gpt-4"
    tokens_used: int = 0
Optional[confidence_score: float] = None

    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ManifestRecord:
    """
    Manifest file structure for a document

    Stored as manifest/{sha256}.json on disk.
    Provides complete audit trail of processing.
    """

    sha256: str

    # Original file
    original: dict[str, any]  # {path, bytes, filename, uploaded_at}

    # Processed artifacts
    processed: dict[str, any] = field(
        default_factory=dict
    )  # {repaired_pdf, ocr_pdf, page_text: [...]}

    # Extraction metadata
    extraction: dict[str, any] = field(
        default_factory=dict
    )  # {method, text_layer_detected, ocr_triggered}

    # Timestamps
    timestamps: dict[str, str] = field(
        default_factory=dict
    )  # {ingested_at, extracted_at, indexed_at}

    # Provenance
    source_system: str = "app"
Optional[doc_id: int] = None  # DB primary key once inserted


# Validation helpers


def validate_passage(passage: Passage) -> bool:
    """Validate that a passage has all required citation fields"""
    required_fields = [
        passage.document_id,
        passage.sha256,
        passage.filename,
        passage.storage_path_original,
        passage.page_number,
        passage.snippet,
    ]
    return all(field is not None for field in required_fields)


def validate_citation(citation: CitationRecord) -> bool:
    """Validate that a citation has all required fields"""
    required_fields = [
        citation.analysis_id,
        citation.document_id,
        citation.page_number,
        citation.snippet,
    ]
    return all(field is not None for field in required_fields)