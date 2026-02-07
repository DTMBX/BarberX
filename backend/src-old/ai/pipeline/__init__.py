# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Unified AI Pipeline

Stable contracts for:
  Ingest → Extract → Index → Retrieve → Analyze

Usage:
    from src.ai.pipeline import get_orchestrator, SourceSystem

    orchestrator = get_orchestrator()

    # Ingest
    result = orchestrator.ingest_document(
        file_path="/path/to/doc.pdf",
        source_system=SourceSystem.APP
    )

    # Extract + Index
    orchestrator.extract_document(result.doc_id)
    orchestrator.index_document(result.doc_id)

    # Retrieve passages
    passages = orchestrator.retrieve(query="probable cause")

    # Analyze with citations
    analysis = orchestrator.analyze(
        query="Was there probable cause?",
        context=passages.passages
    )
"""

from .contracts import (
    AnalysisResult,
    CitationRecord,
    ExtractionMethod,
    ExtractResult,
    IndexResult,
    IngestResult,
    ManifestRecord,
    PageExtraction,
    Passage,
    RetrieveResult,
    SourceSystem,
    validate_citation,
    validate_passage,
)
from .orchestrator import PipelineOrchestrator, get_orchestrator

__all__ = [
    # Main entry point
    "get_orchestrator",
    "PipelineOrchestrator",
    # Data contracts
    "IngestResult",
    "ExtractResult",
    "PageExtraction",
    "IndexResult",
    "Passage",
    "RetrieveResult",
    "AnalysisResult",
    "CitationRecord",
    "ManifestRecord",
    # Enums
    "SourceSystem",
    "ExtractionMethod",
    # Validators
    "validate_passage",
    "validate_citation",
]
