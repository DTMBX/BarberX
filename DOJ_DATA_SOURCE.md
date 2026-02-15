# Official DOJ Epstein Library Data Source

## Overview

This platform is designed to process official document releases from the U.S. Department of Justice Epstein Library at **https://www.justice.gov/epstein**.

## Current Implementation Status

### Browser-Only Mode (Current)
The application currently operates in **Browser-Only Mode**, which displays the user interface and data structures designed for processing official DOJ releases. This mode demonstrates:

- Source configuration for DOJ Epstein Library endpoints
- Document metadata structure and provenance tracking
- Entity extraction and relationship visualization interfaces
- Search and analysis capabilities

**Important**: Browser-Only Mode does not perform actual document downloading, OCR processing, or entity extraction. It shows the UI framework that would display real results when connected to a Local Engine or Team Server.

### Data Displayed

The sample data shown in Browser-Only Mode reflects the structure and types of documents available in the DOJ Epstein Library:

- **Sources**: Configured to point to `justice.gov/epstein` and `justice.gov/epstein/doj-disclosures`
- **Documents**: Structured as official court filings, deposition transcripts, and legal records
- **Entities**: Represented with neutral identifiers (Individual A, Organization Alpha, etc.) to demonstrate provenance-backed entity extraction
- **Relationships**: Evidence-backed connections citing specific document chunks and confidence scores

All data structures follow the architecture designed for:
1. Lawful ingestion of public DOJ releases
2. Chain-of-custody preservation (SHA-256 hashes, timestamps, source URLs)
3. Evidence-backed analysis without accusatory conclusions
4. Audit-grade provenance for every derived artifact

## Full Processing Capabilities (Local Engine Required)

To process actual DOJ documents, you must install and connect to a **Local Worker Service** or **Team Server**. This companion service handles:

### 1. **Polite Crawling & Discovery**
- Discovers downloadable PDFs from justice.gov/epstein
- Respects Queue-it traffic management
- Honors age verification gates
- Records `discovered_from` provenance for every link
- Maintains rate limits (default: 5 req/min)

### 2. **Download with Provenance**
- Downloads files with retry logic and exponential backoff
- Computes SHA-256 hashes for tamper detection
- Stores immutable raw files
- Records HTTP status, timestamps, and source URLs
- Skips re-download of existing files (dedupe by hash)

### 3. **Text Extraction Pipeline**
- **Stage 1**: Native PDF text extraction (fast, preserves selectable text)
- **Stage 2**: OCR fallback for scanned pages (Tesseract or similar)
- Stores per-page extraction status and OCR confidence
- Provides re-OCR controls for low-quality pages
- Preserves page numbering and stable indices

### 4. **Audio Transcription (Optional)**
- Transcribes released audio files using Whisper-compatible engines
- Preserves redaction tones as `[REDACTED TONE]`
- Links transcripts to source file hash and URL
- Records model version and confidence

### 5. **Indexing & Search**
- **Keyword Index**: Exact search, phrases, filters, highlights
- **Semantic Index**: Embedding-based similarity search with explainability
- Faceted filtering by source, date, OCR usage, entity types
- Export result sets with citations and hashes

### 6. **Entity Extraction**
- Extracts people, organizations, locations, dates, identifiers
- Provides confidence scores and manual disambiguation workflows
- Requires reviewer approval for entity merges
- Maintains full edit history with audit logs

### 7. **Relationship Graph**
- Evidence-backed edges citing specific text chunks
- Neutral relationship types (CO_OCCURS_WITH, REFERENCED_IN, ASSOCIATED_WITH)
- Confidence thresholds and reviewer approval gates
- Exportable graph slices with full citations

### 8. **Audit & Compliance**
- Tamper-evident audit logs for all processing steps
- Provenance panels showing processing versions
- Retention controls and redaction modes for exports
- Compliance reports for crawl rate, errors, and throttling

## Site Access Controls & Compliance

The DOJ Epstein Library page may include:

1. **Age Verification Gate**: Client-side dialog requiring explicit acknowledgment
2. **Queue-it Traffic Management**: Server-side queue to manage high traffic
3. **Rate Limiting**: Standard web server rate limits

### Compliance Requirements

The Local Engine **must**:
- Detect and respect Queue-it controls (pause if queue is active)
- Record age gate encounters in audit logs
- Maintain polite rate limits (configurable, default 5 req/min)
- Never attempt to bypass or defeat access controls
- Store compliance reports showing request volume and backoff events

## API Keys & BYOK (Bring Your Own Keys)

Processing relies on LLM providers for:
- Entity extraction (named entity recognition)
- Semantic embeddings (vector search)
- Document summarization (navigation aids)
- Relationship classification

### Security Model

**Browser**: Never sees raw API keys
**Local Engine**: Stores keys in OS keychain or encrypted-at-rest
**User Control**: Add/remove providers, set spending caps, disable features

Supported providers:
- OpenAI (GPT-4, embeddings)
- Google Gemini
- Anthropic Claude
- Local models (Ollama, etc.)

## Installation & Setup

### Prerequisites
- Docker and Docker Compose, OR
- Native installation package for Windows/macOS/Linux
- API keys for chosen LLM provider(s)
- Storage space (estimated: ~10GB per 1,000 documents with OCR)

### Quick Start

1. **Download Local Engine**
   - GitHub releases: [Link to releases page]
   - Docker Compose: `docker-compose.yml` included in repo

2. **Start the Engine**
   ```bash
   docker-compose up -d
   ```
   Default: http://localhost:8080

3. **Connect from Browser**
   - Open the web app
   - Click "Change Connection"
   - Select "Local Engine"
   - Enter pairing code from engine UI

4. **Configure Providers**
   - Navigate to Local Engine settings (separate UI or CLI)
   - Add LLM provider profiles
   - Enter API keys (stored securely)
   - Set spending caps and rate limits

5. **Create Project & Add Source**
   - Create new project: "DOJ Epstein Library Analysis"
   - Add source: `https://www.justice.gov/epstein`
   - Configure crawl rules (rate limits, depth)

6. **Run Ingestion**
   - Start crawl → discover links
   - Download files → compute hashes
   - Extract text → OCR as needed
   - Index → enable search
   - Extract entities → run analysis scripts

7. **Search & Analyze**
   - Keyword search with filters
   - Semantic search for concepts
   - Browse entities and relationships
   - Export evidence bundles with citations

## Data Scope & Ethical Use

### What This Platform Does
- Processes **lawfully published public documents**
- Presents **evidence with citations** and confidence scores
- Maintains **chain-of-custody** for provenance
- Enables **audit-grade analysis** for journalism and research

### What This Platform Does NOT Do
- Generate accusation lists or "suspect databases"
- Make conclusions of guilt from automated analysis
- Bypass access controls or site protections
- Process private materials without authorization
- Facilitate doxxing or vigilante targeting

### User Responsibilities

Users must:
1. Only ingest content they are authorized to access
2. Respect site terms, robots directives, and access controls
3. Verify all findings against original source documents
4. Use redaction controls when sharing sensitive exports
5. Never publish unverified claims based on probabilistic analysis

### Disclaimer Requirements

Every export and report includes:
- Warning that analysis is probabilistic and requires verification
- Citation of source documents with URLs and hashes
- Confidence scores for entities and relationships
- Processing version and model information
- Audit trail for how conclusions were derived

## Roadmap

### Implemented (Browser UI)
- ✅ Multi-source configuration (DOJ, DOJ Disclosures)
- ✅ Ingestion run tracking with provenance
- ✅ Document viewer with status and confidence
- ✅ Entity explorer with disambiguation controls
- ✅ Relationship graph with evidence panels
- ✅ Search interface (keyword + semantic patterns)
- ✅ Audit log and system architecture views
- ✅ Analysis scripts framework
- ✅ Review queues and annotation system

### Requires Local Engine (Not Yet Implemented)
- ⏳ Actual web crawler for justice.gov/epstein
- ⏳ Polite downloader with Queue-it detection
- ⏳ PDF text extraction and OCR pipeline
- ⏳ Whisper transcription for audio files
- ⏳ Vector database integration (Qdrant/pgvector)
- ⏳ Entity extraction (via LLM providers)
- ⏳ Graph computation and storage (Neo4j or embedded)
- ⏳ Export generation with citations

### Future Enhancements
- 📋 Multi-language support with translation workflows
- 📋 Table and form extraction (structured data)
- 📋 Page-coordinate anchoring for precise highlights
- 📋 Advanced search operators (proximity, boolean)
- 📋 Incremental update scheduler (detect new releases)
- 📋 Quality scoring and dedupe detection
- 📋 Team collaboration features (RBAC, shared annotations)

## Support & Documentation

- **Full PRD**: See `PRD.md` in repo root
- **Setup Guide**: See `LOCAL_ENGINE_SETUP.md` (when available)
- **Security Policy**: See `SECURITY.md`
- **Issues & Questions**: GitHub Issues

## Legal & Compliance Notice

This platform is designed for lawful analysis of public records. Users are responsible for:
- Compliance with applicable laws and regulations
- Respecting intellectual property and privacy rights
- Verifying the accuracy of automated analysis outputs
- Obtaining appropriate authorizations before processing sensitive materials

The platform includes built-in safeguards (provenance tracking, audit logs, redaction tools) but **ultimate responsibility for ethical and lawful use rests with the user**.

---

**Last Updated**: 2024 (Browser-Only Mode Release)
**Status**: UI framework complete; Local Engine in development
**Source**: https://www.justice.gov/epstein
