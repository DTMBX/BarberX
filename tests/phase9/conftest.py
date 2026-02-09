"""
Phase 9 Test Configuration & Fixtures
Test fixtures for batch document processing
"""
import pytest
import os
import asyncio
import tempfile
from pathlib import Path
from typing import Generator

# Add models to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from models.batch_document_processing import (
    OCREngine,
    PDFBatchLoader,
    DocumentContextExtractor,
    CaseKnowledgeGraphBuilder,
    BatchDocumentWorkflow
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return path to fixtures directory"""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture(scope="session")
def sample_pdfs_dir(fixtures_dir):
    """Return path to sample PDFs directory"""
    path = os.path.join(fixtures_dir, 'sample_pdfs')
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def dismissed_cases_dir(fixtures_dir):
    """Return path to dismissed cases directory"""
    path = os.path.join(fixtures_dir, 'dismissed_cases')
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture
def temp_pdf_dir():
    """Create temporary directory for test PDFs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="session")
def ocr_engine():
    """Create OCREngine instance for testing"""
    return OCREngine(
        model='tesseract-v5',
        fallback='easyocr',
        preprocessing=True
    )


@pytest.fixture(scope="session")
def pdf_loader():
    """Create PDFBatchLoader instance for testing"""
    return PDFBatchLoader(
        max_concurrent=4,
        skip_errors=True,
        timeout_per_pdf=60
    )


@pytest.fixture(scope="session")
def context_extractor():
    """Create DocumentContextExtractor instance for testing"""
    return DocumentContextExtractor()


@pytest.fixture(scope="session")
def knowledge_graph_builder():
    """Create CaseKnowledgeGraphBuilder instance for testing"""
    return CaseKnowledgeGraphBuilder()


@pytest.fixture(scope="session")
def batch_workflow():
    """Create BatchDocumentWorkflow instance for testing"""
    return BatchDocumentWorkflow(
        ocr_engine=OCREngine(model='tesseract-v5', fallback='easyocr'),
        context_extractor=DocumentContextExtractor(),
        graph_builder=CaseKnowledgeGraphBuilder()
    )


@pytest.fixture
def sample_case_text():
    """Return sample legal case text for testing"""
    return """
    CASE NO. 2023-CV-12345
    
    PLAINTIFF v. DEFENDANT
    
    Plaintiff ABC Corp filed a complaint against Defendant XYZ Inc.
    
    COURT: United States District Court for the Northern District of California
    
    JUDGE: Hon. John Smith
    
    VIOLATION: Breach of Contract
    
    The defendant failed to perform obligations under the service agreement 
    signed on January 15, 2023. The breach resulted in damages of $250,000.
    
    RELIEF REQUESTED: $250,000 in damages plus attorneys fees and costs.
    
    KEY DATES:
    - Contract signed: January 15, 2023
    - Breach occurred: March 1, 2023
    - Complaint filed: April 15, 2023
    - Motion hearing: June 20, 2023
    """


@pytest.fixture
def sample_dismissed_case_text():
    """Return sample dismissed case text (to be reused in new case)"""
    return """
    CASE NO. 2022-CV-98765
    
    PLAINTIFF v. DEFENDANT
    
    Plaintiff Big Law Firm filed action against Defendant Original Corp.
    
    COURT: United States District Court for the Central District of California
    
    JUDGE: Hon. Sarah Johnson
    
    VIOLATION: Negligence, Fraud
    
    The defendant made false representations regarding product quality.
    Caused financial loss of $500,000.
    
    RELIEF REQUESTED: $500,000 in compensatory damages, $1,000,000 in punitive damages
    
    STATUS: DISMISSED WITHOUT PREJUDICE (February 14, 2024)
    
    KEY FACTS:
    - Parties had prior business relationship (2020-2022)
    - Multiple communications showing defendant's knowledge of falsity
    - Financial damages well-documented
    - Certifications obtained from independent experts
    
    REUSABLE ELEMENTS:
    - Expert testimony (90% reusable if similar damages claimed)
    - Party relationship documentation (70% reusable)
    - Certification protocols (80% reusable)
    - Discovery responses (60% reusable)
    """


@pytest.fixture
def sample_pdf_files(sample_pdfs_dir):
    """
    Return dict of available sample PDF files
    Will be generated on demand if not present
    """
    return {
        'complaint': os.path.join(sample_pdfs_dir, 'complaint.pdf'),
        'discovery': os.path.join(sample_pdfs_dir, 'discovery.pdf'),
        'motion': os.path.join(sample_pdfs_dir, 'motion.pdf'),
        'certification': os.path.join(sample_pdfs_dir, 'certification.pdf'),
    }


@pytest.fixture
def dismissed_case_pdfs(dismissed_cases_dir):
    """
    Return dict of dismissed case PDF files
    Will be generated on demand if not present
    """
    return {
        'complaint': os.path.join(dismissed_cases_dir, 'dismissed_complaint.pdf'),
        'discovery': os.path.join(dismissed_cases_dir, 'dismissed_discovery.pdf'),
        'certification': os.path.join(dismissed_cases_dir, 'dismissed_certification.pdf'),
    }


def pytest_configure(config):
    """Configure pytest before running tests"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


# Performance benchmarking fixture
@pytest.fixture
def benchmark_timer():
    """Simple timer for performance benchmarking"""
    import time
    
    class Timer:
        def __init__(self):
            self.start = None
            self.end = None
        
        def __enter__(self):
            self.start = time.time()
            return self
        
        def __exit__(self, *args):
            self.end = time.time()
        
        @property
        def elapsed(self):
            if self.start and self.end:
                return self.end - self.start
            return None
        
        @property
        def elapsed_ms(self):
            if self.elapsed:
                return self.elapsed * 1000
            return None
    
    return Timer


# Teardown for test files
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add cleanup logic here if needed
