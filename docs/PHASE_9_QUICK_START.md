# Phase 9 Quick Start Guide
## Begin Testing Suite Implementation Immediately

**Duration**: 2-3 weeks  
**Team**: QA Engineers (2), Document Processing Specialist (1)  
**Status**: Ready to start now

---

## 📋 What You're Building

A comprehensive test suite ensuring:
- ✅ 25 PDFs batch load in parallel (5-second concurrency)
- ✅ OCR achieves 95%+ accuracy on scanned documents
- ✅ Case facts extract correctly (parties, case #, violations)
- ✅ Knowledge graphs build successfully (entities + relationships)
- ✅ End-to-end workflow: PDFs → OCR → Extract → Graph (< 5 min for 25 PDFs)

---

## 🚀 Starting Now: Day 1 Checklist

### 1. Setup Test Directory
```bash
cd c:\web-dev\github-repos\Evident

# Create test structure
mkdir -p tests/phase9
mkdir -p tests/phase9/unit/batch_processing
mkdir -p tests/phase9/integration
mkdir -p tests/phase9/fixtures/sample_pdfs
mkdir -p tests/phase9/fixtures/dismissed_cases

cd tests/phase9
```

### 2. Create Test Fixtures (Sample Data)
```bash
# Create sample PDFs for testing
# Edit: tests/phase9/fixtures/generate_fixtures.py

# Sample legal PDFs:
# - complaint.pdf (10 pages)
# - discovery_response.pdf (15 pages)  
# - motion.pdf (5 pages)
# - dismissed_case_summary.pdf (8 pages)
```

### 3. Create Test Configuration
```python
# tests/phase9/conftest.py
import pytest
import os

@pytest.fixture
def sample_pdfs_dir():
    return os.path.join(os.path.dirname(__file__), 'fixtures/sample_pdfs')

@pytest.fixture
def dismissed_case_pdfs():
    return {
        'complaint': 'dismissed_complaint.pdf',
        'discovery': 'dismissed_discovery.pdf',
        'certification': 'dismissed_certification.pdf'
    }

@pytest.fixture
def ocr_engine():
    from models.batch_document_processing import OCREngine
    return OCREngine(model='tesseract-v5', fallback='easyocr')

@pytest.fixture
def pdf_loader():
    from models.batch_document_processing import PDFBatchLoader
    return PDFBatchLoader(max_concurrent=4, skip_errors=True)
```

---

## 📝 Phase 9 Test Files to Create

### File 1: Test Batch PDF Loading
```
Path: tests/phase9/unit/batch_processing/test_pdf_batch_loader.py
Lines: ~75 tests
Targets:
- Load 10 PDFs concurrently
- Load 25 PDFs concurrently
- Handle corrupted PDF (skip gracefully)
- Handle missing file (skip gracefully)
- Report correct page counts
- Report correct file sizes
- Measure concurrent performance
```

### File 2: Test OCR Extraction
```
Path: tests/phase9/unit/batch_processing/test_ocr_extraction.py
Lines: ~60 tests
Targets:
- Extract text from scanned PDF (95%+ confidence)
- Extract from mixed PDF (scanned + native)
- Measure per-page confidence
- Batch process 5 PDFs concurrently
- Verify Tesseract fallback works
- Verify EasyOCR fallback works
- Handle image preprocessing
- Measure inference time (target: 30s per page)
```

### File 3: Test Context Extraction
```
Path: tests/phase9/unit/batch_processing/test_document_context_extraction.py
Lines: ~50 tests
Targets:
- Extract case number (e.g., "2023-CV-12345")
- Extract plaintiff name
- Extract defendant name
- Extract court name
- Extract relief requested
- Extract violations (breach, fraud, negligence)
- Extract key dates (filing, hearing)
- Handle missing fields gracefully
- Validate extracted data format
```

### File 4: Test Knowledge Graph
```
Path: tests/phase9/unit/batch_processing/test_case_knowledge_graph.py
Lines: ~45 tests
Targets:
- Extract entities (parties, dates, statutes)
- Build relationships (entity1 → entity2)
- Count nodes >= 20 (for 3 documents)
- Count edges >= 40 (for 3 documents)
- Validate node types (PERSON, ORG, DATE, etc)
- Index in vector DB successfully
- Serialize/deserialize graphs
```

### File 5: Integration Tests
```
Path: tests/phase9/integration/test_batch_workflow.py
Lines: ~40 tests
Targets:
- Full pipeline: Load → OCR → Extract → Graph
- Process 10 PDFs end-to-end (< 120 seconds)
- Validate output format (dictionaries with keys)
- Handle errors gracefully (skip bad PDFs)
- Produce valid knowledge graph output
- Measure end-to-end timing
```

### File 6: Performance Benchmarks
```
Path: tests/phase9/performance/test_batch_performance.py
Lines: ~30 tests
Targets:
- Load 25 PDFs: < 10 seconds
- OCR 100 pages: < 300 seconds (5 min target)
- Extract context per document: < 5 seconds
- Build knowledge graph per document: < 10 seconds
- Full workflow 25 PDFs: < 360 seconds (6 min acceptable)
```

**Total**: ~300 tests across 6 files = foundation for 1,000+ test suite

---

## 🔧 Implementation Order (Week-by-Week)

### Week 1: Setup + Batch Loading
**Files**: `test_pdf_batch_loader.py`, `conftest.py`

**Day 1**:
- Create directory structure
- Create `conftest.py` with fixtures
- Create 10 sample PDFs (using `reportlab`)

**Day 2-3**:
- Implement `PDFBatchLoader` tests
- Verify concurrent loading (4-8 workers)
- Test error handling (corrupted PDFs)

**Day 4-5**:
- Create 25-PDF load scenario
- Measure performance (target: 2-5 sec per PDF)
- Debug and optimize

**Week 1 Goal**: ✅ 50+ passing tests, concurrent loading proven

### Week 2: OCR + Context
**Files**: `test_ocr_extraction.py`, `test_document_context_extraction.py`

**Day 1-2**:
- Implement `OCREngine` tests
- Setup Tesseract locally (Windows binary)
- Test on sample scanned PDFs

**Day 3-4**:
- Implement fallback (EasyOCR) tests
- Verify accuracy >= 95%
- Measure per-page confidence

**Day 5-6**:
- Implement context extraction tests
- Extract parties, case #, violations
- Validate accuracy on 10 sample documents

**Week 2 Goal**: ✅ 100+ tests, OCR at 95%+, context extraction working

### Week 3: Knowledge Graph + Integration
**Files**: `test_case_knowledge_graph.py`, `test_batch_workflow.py`

**Day 1-2**:
- Implement knowledge graph builder tests
- Verify entity extraction (spaCy NER)
- Verify relationship building

**Day 3-4**:
- Implement end-to-end workflow test
- Load → OCR → Extract → Graph all in one
- Measure total time (target: < 5 min for 25 PDFs)

**Day 5-6**:
- Performance benchmarking
- Optimization (parallel processing, caching)
- Final validation

**Week 3 Goal**: ✅ 300+ tests, end-to-end workflow proven, < 5 min for 25 PDFs

---

## 📊 How to Run Tests

### All Tests
```bash
pytest tests/phase9/ -v --tb=short --cov=models/batch_document_processing
```

### By Category
```bash
# Unit tests only
pytest tests/phase9/unit/ -v

# Integration tests only
pytest tests/phase9/integration/ -v

# Performance benchmarks
pytest tests/phase9/performance/ -v --benchmark-only

# Specific test file
pytest tests/phase9/unit/batch_processing/test_pdf_batch_loader.py -v
```

### With Coverage Report
```bash
pytest tests/phase9/ --cov=models/batch_document_processing --cov-report=html
# Opens coverage/index.html
```

---

## 🎯 Success Criteria (Phase 9)

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tests | 1,000+ | |
| Test Passing | 100% | |
| Code Coverage | 90%+ | |
| OCR Accuracy | 95%+ | |
| Batch Load Time | < 10s for 25 PDFs | |
| OCR Time | < 5 min for 100 pages | |
| Context Accuracy | 95%+ extraction | |
| End-to-End | < 6 min for 25 PDFs | |

---

## 🛠️ Dependencies to Install

```bash
# Core testing
pip install pytest pytest-cov pytest-asyncio

# PDF/OCR
pip install PyPDF2 pdfplumber pymupdf pytesseract python-docx
pip install easyocr paddleocr  # Fallbacks

# NLP/Extraction
pip install spacy transformers torch
python -m spacy download en_core_web_sm

# Async/Performance
pip install asyncio aiofiles

# Database (for phase 10)
pip install sqlalchemy psycopg2-binary

# Testing utilities
pip install faker  # Generate fake PDFs
pip install pdf2image  # For OCR
pip install reportlab  # Create test PDFs
```

### Setup Tesseract (OCR)
**Windows**:
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR
# Add to PATH in conftest.py:
import os
os.environ['PYTESSERACT_PATH'] = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 📚 Key Test Examples

### Test 1: Batch Load 25 PDFs
```python
@pytest.mark.asyncio
async def test_batch_load_25_pdfs(pdf_loader, sample_pdfs_dir):
    """Load 25 PDFs concurrently"""
    pdf_files = [
        os.path.join(sample_pdfs_dir, f'document_{i}.pdf')
        for i in range(25)
    ]
    
    results = await pdf_loader.load_batch(pdf_files)
    
    # Assertions
    assert len(results) == 25
    assert all(r['status'] == 'loaded' for r in results)
    assert all(r['page_count'] > 0 for r in results)
    assert sum(r['file_size_bytes'] for r in results) < 500_000_000
```

### Test 2: OCR Accuracy
```python
@pytest.mark.asyncio
async def test_ocr_accuracy_95_percent(ocr_engine, sample_pdfs_dir):
    """Scanned PDF extraction >= 95% confidence"""
    pdf_path = os.path.join(sample_pdfs_dir, 'scanned_legal_doc.pdf')
    
    result = await ocr_engine.extract_text(pdf_path)
    
    assert result['confidence'] >= 0.95
    assert len(result['text']) > 1000
    assert 'defendant' in result['text'].lower() or 'plaintiff' in result['text'].lower()
```

### Test 3: Extract Case Facts
```python
def test_extract_case_number(context_extractor):
    """Extract case number from text"""
    text = "CASE NO. 2023-CV-12345 Plaintiff v. Defendant"
    
    context = context_extractor.extract(text)
    
    assert context['case_number'] == '2023-CV-12345'
    assert context['parties']['plaintiff'] is not None
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Tesseract Not Found
```python
# Solution: Install and add to PATH
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue 2: CUDA/GPU Not Available
```python
# Solution: Use CPU-only
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU
```

### Issue 3: Async Timeout
```python
# Solution: Increase timeout in pytest.ini
[pytest]
asyncio_mode = auto
timeout = 600  # 10 minutes
```

---

## 📈 Progression to 1,000+ Tests

```
Phase 9 (Weeks 1-3):     300 tests (batch, OCR, extraction)
Phase 9 (Extended):      500 tests (edge cases, performance)
Phase 10 (Weeks 4-7):    300 tests (chat, memory, projects)
Phase 11 (Weeks 8-10):   300 tests (vector DB, knowledge graph)
Other (compliance, etc): 200 tests

TOTAL: 1,000+ tests
```

---

## ✅ Deliverables Checklist

**Week 1**:
- [ ] Test directory structure created
- [ ] conftest.py with fixtures
- [ ] 10 sample PDFs generated
- [ ] PDFBatchLoader tests (50 tests)
- [ ] 50+ tests passing

**Week 2**:
- [ ] 25 sample PDFs for load testing
- [ ] OCREngine tests (60 tests)
- [ ] DocumentContextExtractor tests (50 tests)
- [ ] 160+ total tests passing
- [ ] OCR accuracy verified >= 95%

**Week 3**:
- [ ] CaseKnowledgeGraphBuilder tests (45 tests)
- [ ] BatchDocumentWorkflow tests (40 tests)
- [ ] Performance benchmarks (30 tests)
- [ ] 300+ total tests passing
- [ ] End-to-end workflow validated
- [ ] Performance targets met (< 5 min for 25 PDFs)

**Documentation**:
- [ ] TEST_GUIDE.md (how to run tests)
- [ ] FIXTURES_GUIDE.md (how to create sample data)
- [ ] COVERAGE_REPORT.md (test coverage details)

---

## 🎓 Learning Resources

### Testing
- pytest docs: https://docs.pytest.org/
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio
- Factory Boy (fixtures): https://factoryboy.readthedocs.io/

### OCR
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- EasyOCR: https://github.com/JaidedAI/EasyOCR

### NLP
- spaCy: https://spacy.io/
- Transformers: https://huggingface.co/docs/transformers/

---

## 🚦 Next Phase Entry Point

**Phase 10 starts when**:
- ✅ 300+ Phase 9 tests passing
- ✅ 90%+ code coverage
- ✅ OCR accuracy >= 95%
- ✅ Batch performance < 5 min for 25 PDFs

**Phase 10 first task**: Create API endpoint tests + models

---

## 👥 Team Assignments

**QA Engineer 1** (Week 1-3):
- `test_pdf_batch_loader.py`
- `test_ocr_extraction.py`
- Performance benchmarking

**QA Engineer 2** (Week 1-3):
- `test_document_context_extraction.py`
- `test_case_knowledge_graph.py`
- `conftest.py` + fixtures

**Document Processing Specialist** (Week 1-3):
- Generate 25 sample legal PDFs
- Create test fixtures (dismissed cases, etc)
- Validate extraction accuracy

---

## 🎬 Start Now

**This moment**:
```bash
cd c:\web-dev\github-repos\Evident
mkdir -p tests/phase9/{unit/batch_processing,integration,fixtures/{sample_pdfs,dismissed_cases}}
touch tests/phase9/conftest.py
touch tests/phase9/unit/batch_processing/__init__.py

# Begin Phase 9 👇
```

**You have everything you need. Start this week.**

