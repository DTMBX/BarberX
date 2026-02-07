# Unified Retrieval System - Quick Start Guide

## 1. Database Setup

```bash
# Initialize the database
python scripts/db/init_db.py
```

This creates `instance/Evident_legal.db` with tables for documents, pages, FTS
index, citations, and municipal codes.

## 2. Ingest Documents

### Python API

```python
from legal_library_adapter import LegalLibraryAdapter

adapter = LegalLibraryAdapter()

# Ingest PDF
doc_id = adapter.ingest_pdf(
    filepath="path/to/case.pdf",
    source_system="legal_library",
    document_type="case_law",
    metadata={"citation": "Smith v. Jones", "year": 2024}
)

# Ingest text
doc_id = adapter.ingest_text_document(
    text="Your legal text here...",
    filename="statute.txt",
    source_system="legal_library",
    document_type="statute"
)
```

## 3. Retrieve Passages

### Python API

```python
from retrieval_service import RetrievalService

service = RetrievalService()

# Simple retrieval
passages = service.retrieve(
    query="search and seizure",
    top_k=5
)

# With filters
passages = service.retrieve(
    query="qualified immunity",
    filters={'source_system': 'legal_library', 'document_type': 'case_law'},
    top_k=10
)

# Each passage has:
for passage in passages:
    print(f"Document: {passage.filename}")
    print(f"Page: {passage.page_number}")
    print(f"Offsets: {passage.text_start}-{passage.text_end}")
    print(f"Snippet: {passage.snippet}")
    print(f"Score: {passage.score}")
```

## 4. ChatGPT Integration

```python
from chatgpt_legal_library_integration import ChatGPTLegalLibraryIntegration
from citation_service import CitationService

integration = ChatGPTLegalLibraryIntegration()
citation_svc = CitationService()

# In your chat endpoint
user_message = "What are the requirements for a search warrant?"

# 1. Retrieve relevant passages
passages, metadata = integration.search_library_for_context(user_message)

# 2. Build prompt with SOURCES
system_prompt = integration.enhance_system_prompt(
    "You are a legal assistant...",
    passages
)

# The prompt now contains:
# === SOURCES (Retrieved Legal Documents) ===
# [Source 1]
# Document: fourth_amendment.txt
# Page: 1
# Excerpt: ...warrants be supported by probable cause...
# (doc_id: legal_library_abc123, offsets: 150-350)
# === END SOURCES ===
# CRITICAL: Every factual claim must cite a source...

# 3. Call ChatGPT
response = chatgpt_service.chat(user_message, system_prompt)

# 4. Persist citations
analysis_id = citation_svc.persist_citations(
    analysis_id=f"chat_{session_id}",
    passages=passages
)
```

## 5. Municipal Codes

```python
from municipal_code_service import MunicipalCodeService

service = MunicipalCodeService()

# Seed core counties
service.seed_core_counties({
    "Atlantic": ["Atlantic City", "Galloway", "Egg Harbor Township"],
    "Ocean": ["Toms River", "Lakewood"],
    "Cape May": ["Cape May", "Lower Township"]
})

# Add ordinance
source = service.ensure_source(
    county="Atlantic",
    municipality="Atlantic City"
)

section_id = service.upsert_section(
    source_id=source.id,
    section_citation="§ 222-36",
    title="Body-worn cameras required",
    text="All law enforcement officers shall wear body-worn cameras...",
    source_url="https://ecode360.com/AT1234"
)

# Search
results = service.search(
    query="body camera",
    county="Atlantic",
    limit=5
)
```

## 6. Citation Tracking

```python
from citation_service import CitationService

service = CitationService()

# After analysis, persist citations
analysis_id = service.persist_citations(
    analysis_id="analysis_123",
    passages=passages
)

# Later, retrieve citations
citations = service.get_citations("analysis_123")
for cite in citations:
    print(f"[{cite.citation_rank}] {cite.document_id} p.{cite.page_number}")
    print(f"   Offsets: {cite.text_start}-{cite.text_end}")
    print(f"   Snippet: {cite.snippet}")

# Document usage stats
stats = service.get_citation_stats("legal_library_abc123")
# {'total_citations': 15, 'analyses_count': 3,
#  'first_cited': '2024-01-30...', 'last_cited': '2024-01-30...'}
```

## Testing

```bash
# Run tests
python -m pytest tests/test_unified_retrieval.py -v

# All 5 tests should pass:
# ✓ test_01_ingest_text_document
# ✓ test_02_retrieve_passages
# ✓ test_03_persist_citations
# ✓ test_04_municipal_code_storage
# ✓ test_05_end_to_end_citation_flow
```

## CLI Usage

```bash
# Retrieve passages
python -m pipeline.cli retrieve "search seizure" -top 5
python -m pipeline.cli retrieve "qualified immunity" -json

# List documents
python -m pipeline.cli list
python -m pipeline.cli list -source legal_library

# Get citations
python -m pipeline.cli citations analysis_abc123
```

## Architecture

```
User Query
    ↓
RetrievalService.retrieve(query, filters)
    ↓
FTS5 BM25 Search on document_fts
    ↓
Returns Passage[] with:
  - document_id, sha256, filename
  - page_number, text_start, text_end
  - snippet, score, source_system
    ↓
ChatGPT Integration
  - enhance_system_prompt(passages)
  - Builds SOURCES block
    ↓
CitationService.persist_citations(analysis_id, passages)
    ↓
Citations Table
  - Audit trail of sources used
```

## Key Benefits

1. **Single Retrieval Interface** - One `retrieve()` method for all document
   types
2. **Full Provenance** - Every passage tracked with doc_id/page/offsets
3. **BM25 Ranking** - Production-quality relevance scoring
4. **Citation Audit Trail** - Know which documents were used in each analysis
5. **Municipal Codes Ready** - Infrastructure for ordinances
6. **No Breaking Changes** - Existing systems can be bridged
7. **Testable** - Comprehensive test coverage

## Database Schema

**Documents:**

- document_id (unique), sha256, filename, storage_path_original
- source_system ('legal_library', 'muni_code', 'bwc')
- document_type, metadata (JSON)

**Document Pages:**

- document_id, page_number, text_content
- Auto-syncs to FTS5 via triggers

**Citations:**

- analysis_id, document_id, page_number
- text_start, text_end, snippet, citation_rank

**Municipal Sources/Sections:**

- state, county, municipality, provider
- section_citation, title, text, source_url

All ready for production use!
