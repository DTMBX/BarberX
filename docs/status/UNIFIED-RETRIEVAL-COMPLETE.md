# Unified Legal Retrieval System - Implementation Complete

## Summary

Successfully implemented a unified retrieval system with citation provenance for
the Legal Library. All components are working and tested.

## Components Implemented

### 1. Database Schema ✓

**Location:** `scripts/db/schema.sql`

- `documents` - All ingested legal documents with sha256, source_system tracking
- `document_pages` - Page-level content for retrieval
- `document_fts` - FTS5 index with BM25 ranking
- `citations` - Citation provenance tracking
- `muni_sources` - Municipal code sources (NJ counties)
- `muni_code_sections` - Municipal ordinance sections
- Auto-syncing FTS triggers

**Initialization:**

```bash
python scripts/db/init_db.py
```

### 2. RetrievalService ✓

**Location:** `retrieval_service.py`

**Features:**

- Unified FTS5 BM25-ranked retrieval across all sources
- Returns `Passage` objects with full provenance:
  - document_id, sha256, filename, storage_path_original
  - page_number, text_start, text_end
  - snippet with query context
  - score, source_system
- Filters by source_system, document_type, document_id
- Configurable top_k results

**Usage:**

```python
from retrieval_service import RetrievalService

service = RetrievalService()
passages = service.retrieve(
    query="search and seizure",
    filters={'source_system': 'legal_library'},
    top_k=5
)
```

### 3. LegalLibraryAdapter ✓

**Location:** `legal_library_adapter.py`

**Features:**

- Ingest PDF documents with page extraction
- Ingest plain text with virtual paging
- SHA256 deduplication
- Metadata storage (JSON)
- Document listing and deletion

**Usage:**

```python
from legal_library_adapter import LegalLibraryAdapter

adapter = LegalLibraryAdapter()

# Ingest PDF
doc_id = adapter.ingest_pdf(
    filepath="case.pdf",
    source_system="legal_library",
    document_type="case_law",
    metadata={"citation": "Smith v. Jones", "year": 2020}
)

# Ingest text
doc_id = adapter.ingest_text_document(
    text="Legal text here...",
    filename="statute.txt",
    source_system="legal_library",
    document_type="statute"
)
```

### 4. ChatGPT Integration Update ✓

**Location:** `chatgpt_legal_library_integration.py`

**Changes:**

- `search_library_for_context()` now returns `(passages, citations_metadata)`
  tuple
- Uses `RetrievalService.retrieve()` instead of LIKE-based search
- `enhance_system_prompt()` builds strict SOURCES block with:
  - Numbered citations [Source 1], [Source 2]
  - Document ID, page number, offsets
  - Excerpt text
  - Requirement to cite sources

**Before/After:**

```python
# OLD (LIKE search, no provenance)
cases = integration.search_library_for_context(message)
# Returns: [{'citation': '...', 'title': '...', 'summary': '...'}]

# NEW (FTS5 + provenance)
passages, metadata = integration.search_library_for_context(message)
# Returns: ([Passage(doc_id, page, offsets, snippet, ...)], {...})

# OLD prompt (loose references)
prompt = enhance_system_prompt(base, cases)
# "Relevant cases: Smith v. Jones..."

# NEW prompt (strict citations)
prompt = enhance_system_prompt(base, passages)
# "=== SOURCES ===
# [Source 1]
# Document: smith_v_jones.pdf
# Page: 5
# Excerpt: ...
# (doc_id: legal_library_abc123, offsets: 150-450)
# === END SOURCES ===
# CRITICAL: Every factual claim must cite a source..."
```

### 5. CitationService ✓

**Location:** `citation_service.py`

**Features:**

- Persist citations for each analysis
- Track document_id, page, offsets, snippet, rank
- Retrieve citations by analysis_id or document_id
- Citation statistics (count, date range)

**Usage:**

```python
from citation_service import CitationService

service = CitationService()

# Persist after retrieval
analysis_id = service.persist_citations(
    analysis_id="chat_session_123",
    passages=passages
)

# Retrieve later
citations = service.get_citations("chat_session_123")

# Document usage stats
stats = service.get_citation_stats("legal_library_abc123")
# {'total_citations': 15, 'analyses_count': 3, ...}
```

### 6. MunicipalCodeService ✓

**Location:** `municipal_code_service.py`

**Features:**

- Manage eCode360 / GeneralCode / Municode ordinances
- Seed core NJ counties (Atlantic, Ocean, Cape May, etc.)
- Upsert sections with SHA256 deduplication
- FTS search with fallback to LIKE
- Retrieve by county/municipality

**Usage:**

```python
from municipal_code_service import MunicipalCodeService

service = MunicipalCodeService()

# Seed counties
service.seed_core_counties({
    "Atlantic": ["Atlantic City", "Galloway"],
    "Ocean": ["Toms River", "Lakewood"]
})

# Ensure source
source = service.ensure_source(
    county="Atlantic",
    municipality="Atlantic City",
    provider="eCode360"
)

# Upsert ordinance
section_id = service.upsert_section(
    source_id=source.id,
    section_citation="§ 222-36",
    title="Body-worn cameras required",
    text="All law enforcement officers...",
    source_url="https://ecode360.com/..."
)

# Search
results = service.search(
    query="body camera",
    county="Atlantic",
    limit=5
)
```

### 7. CLI Tool ✓

**Location:** `pipeline/cli.py`

**Commands:**

```bash
# Retrieve passages
python -m pipeline.cli retrieve "search seizure warrant" -top 5
python -m pipeline.cli retrieve "qualified immunity" -source legal_library -json

# List documents
python -m pipeline.cli list
python -m pipeline.cli list -source legal_library -limit 10

# Get citations
python -m pipeline.cli citations analysis_abc123
```

### 8. Tests ✓

**Location:** `tests/test_unified_retrieval.py`

**Coverage:**

- ✅ Ingestion produces pages
- ✅ Retrieval returns passages with page+offsets
- ✅ Citations persist for an analysis
- ✅ Municipal code storage works
- ✅ End-to-end flow (ingest → retrieve → cite → persist)

**Results:**

```
5 passed in 0.16s
```

## Integration with ChatGPT Service

To wire this into your chat endpoint:

```python
from chatgpt_legal_library_integration import ChatGPTLegalLibraryIntegration
from citation_service import CitationService

integration = ChatGPTLegalLibraryIntegration()
citation_svc = CitationService()

@chatgpt_bp.route('/api/v1/chat/message', methods=['POST'])
def send_message():
    user_message = request.get_json()['message']

    # 1. Retrieve relevant passages
    passages, metadata = integration.search_library_for_context(user_message)

    # 2. Build prompt with SOURCES
    system_prompt = integration.enhance_system_prompt(
        base_system_prompt,
        passages
    )

    # 3. Call ChatGPT
    response = chatgpt_service.chat(user_message, system_prompt)

    # 4. Persist citations
    analysis_id = citation_svc.persist_citations(
        analysis_id=session_id,
        passages=passages
    )

    return jsonify({
        'response': response,
        'analysis_id': analysis_id,
        'sources': metadata
    })
```

## BWC Bridge (Future)

To bridge BWC documents without removing BWC DB:

```python
# In BWC indexer, after creating pages:
from legal_library_adapter import LegalLibraryAdapter

adapter = LegalLibraryAdapter()

# Mirror BWC video metadata
doc_id = adapter.ingest_text_document(
    text=bwc_transcript,
    filename=f"bwc_{video_id}.txt",
    source_system="bwc",
    document_type="bwc_video",
    metadata={
        "video_id": video_id,
        "bwc_db_path": bwc_db_path,
        "timestamp": timestamp
    }
)
```

This allows unified retrieval across legal library + BWC without changing BWC
indexing.

## Architecture Benefits

1. **Single retrieval interface** - One `retrieve()` call for all sources
2. **Full provenance** - Every passage has doc_id/page/offsets
3. **FTS5 BM25 ranking** - Production-quality relevance
4. **Citation tracking** - Audit trail of which docs were used
5. **Municipal codes ready** - Infrastructure for ordinances
6. **No breaking changes** - BWC can be bridged without modification
7. **Testable** - Comprehensive test coverage

## Next Steps

1. **Ingest legal library documents:**

   ```bash
   python -m pipeline.cli ingest cases/*.pdf -source legal_library -doc-type case_law
   ```

2. **Seed municipal codes:**

   ```python
   from municipal_code_service import MunicipalCodeService
   service = MunicipalCodeService()
   service.seed_core_counties({
       "Atlantic": ["Atlantic City", "Egg Harbor Township"],
       "Ocean": ["Toms River", "Lakewood"]
   })
   ```

3. **Update ChatGPT endpoint** - Wire in retrieval + citations (see Integration
   section above)

4. **Monitor citation stats** - Track which documents are most cited:
   ```python
   stats = citation_svc.get_citation_stats(document_id)
   ```

## Files Created/Modified

**Created:**

- `scripts/db/schema.sql` - Database schema
- `scripts/db/init_db.py` - DB initialization
- `retrieval_service.py` - Unified retrieval service
- `legal_library_adapter.py` - Document ingestion
- `citation_service.py` - Citation persistence
- `municipal_code_service.py` - Municipal ordinances
- `pipeline/cli.py` - CLI tool
- `tests/test_unified_retrieval.py` - Test suite

**Modified:**

- `chatgpt_legal_library_integration.py` - Updated to use RetrievalService

**Database:**

- `instance/Evident_legal.db` - Unified legal retrieval database

All requirements met: ✅ ONE unified RetrievalService  
✅ Passage with full provenance fields ✅ LegalLibraryService adapter calls
RetrievalService ✅ ChatGPT integration accepts passages + citations ✅
Citations persist (analysis_id, doc_id, page, offsets) ✅ No breaking changes to
BWC
