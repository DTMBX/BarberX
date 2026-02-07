from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Pipeline Orchestrator - Single entry point for unified AI pipeline

This is the facade that existing code should call. It coordinates:
1. Ingest → Extract → Index → Retrieve → Analyze

Adapters are plugged in here, not exposed to callers.
"""

import logging

from .contracts import (
    AnalysisResult,
    ExtractResult,
    IndexResult,
    IngestResult,
    Passage,
    RetrieveResult,
    SourceSystem,
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Unified pipeline orchestrator

    Usage:
        orchestrator = PipelineOrchestrator()

        # Ingest
        result = orchestrator.ingest_document(
            file_path="/path/to/doc.pdf",
            source_system=SourceSystem.APP,
            metadata={"case_number": "CR-2024-001"}
        )

        # Extract
        extract_result = orchestrator.extract_document(result.doc_id)

        # Index
        index_result = orchestrator.index_document(result.doc_id)

        # Retrieve
        passages = orchestrator.retrieve(
            query="probable cause",
            filters={"source_system": "legal_library"}
        )

        # Analyze
        analysis = orchestrator.analyze(
            query="Was there probable cause?",
            context=passages
        )
    """

Optional[def __init__(self, config: dict] = None):
        """
        Initialize orchestrator with services and adapters

        Args:
            config: Configuration dict with keys:
                - db_path: Path to main database
                - storage_root: Root path for file storage
                - enable_vector_index: Whether to use ChromaDB
                - ocr_threshold: Min chars/page before OCR trigger
        """
        self.config = config or {}

        # Will be initialized lazily
        self._manifest_service = None
        self._extraction_service = None
        self._indexing_service = None
        self._retrieval_service = None
        self._authority_cache = None

        # Adapters (wrap existing systems)
        self._legal_library_adapter = None
        self._bwc_adapter = None
        self._pdf_discovery_adapter = None

        logger.info("PipelineOrchestrator initialized")

    # =================================================================
    # PUBLIC API (stable contract)
    # =================================================================

    def ingest_document(
Optional[self, file_path: str, source_system: SourceSystem, metadata: dict] = None
    ) -> IngestResult:
        """
        Ingest a document into the pipeline

        Steps:
        1. Compute SHA-256 hash
        2. Check for duplicates
        3. Save to canonical location: uploads/pdfs/originals/{sha256}.pdf
        4. Create manifest file: manifest/{sha256}.json
        5. Insert into documents table

        Args:
            file_path: Absolute path to file
            source_system: Origin system (app, bwc, legal_library)
            metadata: Optional user metadata (case_number, tags, etc.)

        Returns:
            IngestResult with doc_id and storage paths

        Raises:
            FileNotFoundError: If file_path doesn't exist
            ValueError: If file is empty or corrupt
        """
        manifest_service = self._get_manifest_service()

        logger.info(f"Ingesting document: {file_path} from {source_system.value}")

        # Delegate to manifest service
        result = manifest_service.ingest(
            file_path=file_path, source_system=source_system, metadata=metadata or {}
        )

        logger.info(
            f"Ingested doc_id={result.doc_id}, sha256={result.sha256[:16]}..., "
            f"duplicate={result.is_duplicate}"
        )

        return result

    def extract_document(self, doc_id: int) -> ExtractResult:
        """
        Extract text from document with auto-OCR

        Steps:
        1. Load document from database
        2. Detect text layer (sample pages)
        3. If thin/missing text → trigger OCR
        4. Extract page-by-page with offsets
        5. Save page text to disk cache
        6. Update manifest with extraction metadata
        7. Return page-aware extraction result

        Args:
            doc_id: Database document ID

        Returns:
            ExtractResult with page-level text and metadata

        Raises:
            ValueError: If doc_id not found
            RuntimeError: If extraction fails
        """
        extraction_service = self._get_extraction_service()

        logger.info(f"Extracting text from doc_id={doc_id}")

        result = extraction_service.extract(doc_id)

        logger.info(
            f"Extracted doc_id={doc_id}: {result.total_pages} pages, "
            f"method={result.extraction_method.value}, ocr={result.ocr_triggered}"
        )

        return result

    def index_document(self, doc_id: int, enable_vector: bool = False) -> IndexResult:
        """
        Index document for search

        Steps:
        1. Load extracted pages from database
        2. Insert into document_pages table
        3. Update FTS5 keyword index
        4. Optionally: generate embeddings and insert into ChromaDB
        5. Update manifest with indexing timestamp

        Args:
            doc_id: Database document ID
            enable_vector: Whether to generate vector embeddings

        Returns:
            IndexResult with indexing metadata

        Raises:
            ValueError: If doc_id not found or not extracted yet
        """
        indexing_service = self._get_indexing_service()

        logger.info(f"Indexing doc_id={doc_id}, vector={enable_vector}")

        result = indexing_service.index(doc_id, enable_vector=enable_vector)

        logger.info(
            f"Indexed doc_id={doc_id}: {result.pages_indexed} pages, "
            f"keyword={result.keyword_index_updated}, vector={result.vector_index_updated}"
        )

        return result

    def retrieve(
Optional[self, query: str, filters: dict] = None, top_k: int = 10, method: str = "keyword"
    ) -> RetrieveResult:
        """
        Retrieve relevant passages (NOT whole documents)

        Steps:
        1. Parse query and filters
        2. Search FTS5 index (keyword) or ChromaDB (semantic)
        3. Rank results by relevance
        4. For each match, extract passage with offsets
        5. Return citation-ready passages

        Args:
            query: Search query
            filters: Optional filters (source_system, date_range, etc.)
            top_k: Max results to return
            method: Retrieval method (keyword, semantic, hybrid)

        Returns:
            RetrieveResult with ranked passages
        """
        retrieval_service = self._get_retrieval_service()

        logger.info(f"Retrieving passages for query: '{query}' (method={method})")

        result = retrieval_service.retrieve(
            query=query, filters=filters or {}, top_k=top_k, method=method
        )

        logger.info(
            f"Retrieved {len(result.passages)} passages from {result.total_matches} matches"
        )

        return result

    def analyze(
Optional[self, query: str, context: list[Passage]] = None, mode: str = "legal_research"
    ) -> AnalysisResult:
        """
        Perform LLM analysis with grounded citations

        Steps:
        1. If context not provided, retrieve relevant passages
        2. Format passages into LLM prompt with citation markers
        3. Call LLM (GPT-4, Claude, etc.)
        4. Parse response and extract citations
        5. Validate citations against source passages
        6. Persist analysis + citations to database
        7. Return analysis with citation records

        Args:
            query: Analysis question
            context: Optional pre-retrieved passages (if None, auto-retrieve)
            mode: Analysis mode (legal_research, violation_scan, etc.)

        Returns:
            AnalysisResult with grounded response and citations

        Raises:
            ValueError: If no context and retrieval fails
            RuntimeError: If LLM call fails
        """
        # Lazy import to avoid circular dependency
        from .services.analysis_service import AnalysisService

        analysis_service = AnalysisService(
            retrieval_service=self._get_retrieval_service(),
            authority_cache=self._get_authority_cache(),
        )

        logger.info(f"Analyzing query: '{query}' (mode={mode})")

        # Auto-retrieve if context not provided
        if context is None:
            retrieve_result = self.retrieve(query=query, top_k=5)
            context = retrieve_result.passages

        result = analysis_service.analyze(query=query, context=context, mode=mode)

        logger.info(
            f"Analysis complete: {len(result.citations)} citations, "
            f"{len(result.authorities_cited)} authorities"
        )

        return result

    # =================================================================
    # ADAPTER INTEGRATION (wrap existing systems)
    # =================================================================

    def sync_legal_library(self, doc_id: int):
        """
        Sync a document from legal_library system into unified pipeline

        Args:
            doc_id: ID from legal_documents table
        """
        adapter = self._get_legal_library_adapter()
        adapter.sync_document(doc_id)
        logger.info(f"Synced legal_library doc_id={doc_id}")

    def sync_bwc_evidence(self, bwc_evidence_id: int):
        """
        Sync a document from BWC evidence system into unified pipeline

        Args:
            bwc_evidence_id: ID from .bwc/index.db evidence_items table
        """
        adapter = self._get_bwc_adapter()
        adapter.sync_evidence(bwc_evidence_id)
        logger.info(f"Synced BWC evidence_id={bwc_evidence_id}")

    # =================================================================
    # INTERNAL: Lazy service initialization
    # =================================================================

    def _get_manifest_service(self):
        """Lazy initialize manifest service"""
        if self._manifest_service is None:
            from .services.manifest_service import ManifestService

            self._manifest_service = ManifestService(config=self.config)
        return self._manifest_service

    def _get_extraction_service(self):
        """Lazy initialize extraction service"""
        if self._extraction_service is None:
            from .services.extraction_service import ExtractionService

            self._extraction_service = ExtractionService(
                config=self.config, manifest_service=self._get_manifest_service()
            )
        return self._extraction_service

    def _get_indexing_service(self):
        """Lazy initialize indexing service"""
        if self._indexing_service is None:
            from .services.indexing_service import IndexingService

            self._indexing_service = IndexingService(
                config=self.config, manifest_service=self._get_manifest_service()
            )
        return self._indexing_service

    def _get_retrieval_service(self):
        """Lazy initialize retrieval service"""
        if self._retrieval_service is None:
            from .services.retrieval_service import RetrievalService

            self._retrieval_service = RetrievalService(config=self.config)
        return self._retrieval_service

    def _get_authority_cache(self):
        """Lazy initialize authority cache"""
        if self._authority_cache is None:
            from .services.authority_cache_service import AuthorityCacheService

            self._authority_cache = AuthorityCacheService(config=self.config)
        return self._authority_cache

    def _get_legal_library_adapter(self):
        """Lazy initialize legal library adapter"""
        if self._legal_library_adapter is None:
            from .adapters.legal_library_adapter import LegalLibraryAdapter

            self._legal_library_adapter = LegalLibraryAdapter(orchestrator=self)
        return self._legal_library_adapter

    def _get_bwc_adapter(self):
        """Lazy initialize BWC adapter"""
        if self._bwc_adapter is None:
            from .adapters.bwc_indexer_adapter import BWCIndexerAdapter

            self._bwc_adapter = BWCIndexerAdapter(orchestrator=self)
        return self._bwc_adapter


# Singleton instance for global access
Optional[_orchestrator_instance: PipelineOrchestrator] = None


Optional[def get_orchestrator(config: dict] = None) -> PipelineOrchestrator:
    """
    Get global orchestrator instance (singleton)

    Args:
        config: Configuration dict (only used on first call)

    Returns:
        PipelineOrchestrator instance
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = PipelineOrchestrator(config=config)

    return _orchestrator_instance