# Planning Guide

**Deployment Architecture: PWA + Local Worker Service**

This platform deploys as two coordinated components:
1. **Browser PWA (Static Frontend)**: Hostable on any web server or GitHub Pages; provides account-less local-first UI, document viewer, search, entity explorer, graph explorer, script controls, and export builder
2. **Local Worker Service (Companion App)**: Installed application or Docker container running on user's machine; handles all heavy processing (OCR, Whisper, vector indexing, graph computation) and stores API keys securely

**Security Model**: API keys (OpenAI, Gemini, Claude) are stored and used exclusively within the Local Worker Service using OS keychain or encrypted-at-rest storage—never exposed to browser JavaScript. The PWA connects via localhost with a short-lived session token obtained through a pairing code.

**Deployment Model**: Users "load it like a website" but connect to their own local processing engine, keeping data and credentials under their control. The PWA detects the local service and offers "Connect to Local Engine" with automatic health-check polling.

**Technical Scope**: The PWA provides the complete user interface and data rendering. The Local Worker Service handles:
- Web crawlers and polite downloaders with rate limiting
- PDF text extraction and OCR processing (Tesseract or similar)
- Audio/video transcription (Whisper or similar)
- Vector database for semantic search (e.g., PostgreSQL with pgvector or embedded alternatives)
- Entity extraction and relationship graph computation
- Distributed job queues for processing millions of documents
- Object storage for immutable raw file storage with SHA-256 verification (local folders or MinIO)

**Experience Qualities**:
1. **Methodical** - Every piece of information traced to its source with evidence-backed citations and clear confidence scoring
2. **Transparent** - Complete provenance chains, audit trails, and processing status visible at every layer
3. **Secure** - API keys and sensitive data remain under user control; browser never sees raw credentials

**Complexity Level**: Complex Application (advanced functionality, likely with multiple views)
This platform implements a distributed architecture with browser PWA frontend and local processing backend, including connection management, BYOK provider architecture, ingestion orchestration, OCR processing, entity disambiguation, graph visualization, role-based access control, and comprehensive audit logging—requiring multiple coordinated views, state management, and secure API communication.

**Operating Modes**:
- **Browser-Only (Limited)**: No engine connected; demonstrates interface capabilities using real DOJ Epstein Library document metadata and structure
- **Local Engine (Full)**: Connected to localhost worker service; all processing happens locally with user's API keys and data
- **Team Server (Full)**: Connected to private self-hosted server; multi-user collaboration with server-side API keys
- **Limited Browser Mode**: Small-sample processing using WebAssembly (PDF text extraction, lightweight embeddings) with clear speed/memory warnings

## Essential Features

**Local Engine Connection & Pairing**
- Functionality: Detect Local Worker Service on localhost, initiate pairing with code, establish session token, monitor health
- Purpose: Enable secure connection between PWA and local processing engine without exposing credentials
- Trigger: User opens PWA and clicks "Connect to Local Engine" or PWA auto-detects localhost service
- Progression: Detect service → show pairing code from local engine → user enters code in PWA → receive session token → store with expiration → enable full features
- Success criteria: PWA shows connection status (Not Connected / Connected Local / Connected Team); health checks poll every 30s; tokens auto-refresh before expiration; pairing can be revoked from engine UI

**BYOK Provider Management (Local Engine Only)**
- Functionality: Configure LLM provider profiles (OpenAI, Gemini, Claude, Local Models) with credentials, capabilities, and spending caps inside Local Worker Service
- Purpose: Allow users to bring their own API keys while keeping them secure and never exposing them to browser code
- Trigger: User navigates to provider settings in Local Engine management interface
- Progression: Add provider → select type → enter credentials (stored in OS keychain) → set spending caps → test connection → enable for tasks
- Success criteria: Keys stored encrypted or in OS keychain; PWA UI shows available providers and task assignments but never sees raw keys; all LLM calls logged with provider, model, tokens, purpose; users can disable/delete providers instantly

**Project-Based Workspace Management**
- Functionality: Create local Projects containing sources, artifacts, indexes, annotations, script outputs with import/export manifests
- Purpose: Enable users to organize work by investigation/case/topic with isolated data and retention policies
- Trigger: User creates new project from dashboard or imports project manifest
- Progression: Create project → set retention policy → add sources → configure processing → run ingestion → annotate and analyze → export project bundle
- Success criteria: Projects stored independently in Local Engine; manifests include tamper-evident audit ledger (URLs, timestamps, SHA-256s, processing versions); projects exportable as bundles without raw bulk documents

**Source Management & Discovery**
- Functionality: Configure document sources with crawl rules, rate limits, and provenance policies
- Purpose: Establish chain-of-custody from discovery through processing
- Trigger: Admin navigates to Sources dashboard and configures a new source
- Progression: Add source → set crawl parameters → validate connectivity → save → view in sources list
- Success criteria: Source configuration stored with validation rules, ready for ingestion runs

**Ingestion Run Orchestration**
- Functionality: Execute discovery, download, hash, and queue documents with throttling and error handling
- Purpose: Demonstrate audit-grade ingestion with deterministic provenance
- Trigger: Analyst initiates a new ingestion run from a configured source
- Progression: Start run → discover documents → download with rate limiting → compute SHA-256 → store immutably → update run status
- Success criteria: All discovered documents logged with timestamps, hashes, and download status; errors captured with retry state

**Document Processing Pipeline**
- Functionality: Extract text (native or OCR), chunk for indexing, store page-level metadata
- Purpose: Transform raw documents into searchable, analyzable artifacts
- Trigger: Downloaded document enters processing queue
- Progression: Extract metadata → extract text → detect if OCR needed → chunk text → mark processing complete
- Success criteria: Each document shows extraction status, page count, OCR flags, and text availability

**Full-Text Search with Provenance**
- Functionality: Keyword and semantic search across indexed documents with highlighting and filters
- Purpose: Enable fast discovery of relevant passages with source citations
- Trigger: User enters search query in global search bar or Search hub
- Progression: Enter query → apply filters (source, date, OCR used) → view results with snippets → click to view document context
- Success criteria: Results show highlighted matches, link to exact pages, display confidence and source hash

**Entity Extraction & Disambiguation**
- Functionality: Extract people, organizations, locations, dates with confidence scoring and manual merge workflow
- Purpose: Build structured knowledge from unstructured text with reviewer oversight
- Trigger: Document completes text extraction and enters entity extraction queue
- Progression: Extract entities → assign confidence → surface in Entity explorer → reviewer disambiguates → approve merge
- Success criteria: Entities displayed with aliases, confidence, mention counts, and disambiguation status

**Evidence-Backed Relationship Graph**
- Functionality: Visualize entity relationships with explainable edges citing evidence snippets
- Purpose: Surface patterns across documents without making accusations
- Trigger: User navigates to Graph view and selects entities or filters
- Progression: Load graph → apply filters → select entity → view edges → click edge to see evidence → export subgraph with citations
- Success criteria: Every edge shows relationship type, confidence, and clickable evidence snippets from source chunks

**Audit Trail & Access Control**
- Functionality: RBAC with Admin/Analyst/Reviewer/ReadOnly roles; log all entity/relationship edits
- Purpose: Ensure changes are traceable and access is appropriately restricted
- Trigger: User performs any mutation (entity merge, relationship edit, source configuration)
- Progression: Action initiated → RBAC check → execute → log audit event → surface in audit log
- Success criteria: Audit log shows actor, timestamp, action, object ID, and change details; unauthorized actions blocked

**Document Viewer with Provenance Panel**
- Functionality: View document text/pages with side panel showing SHA-256, source URL, download timestamp, processing version
- Purpose: Enable verification of document authenticity and chain-of-custody
- Trigger: User clicks document from search results or document list
- Progression: Load document → render text/pages → display provenance panel → enable in-document search → allow page navigation
- Success criteria: Document displays with full metadata, hash verification, and clear processing history

**Analysis Script Runner (Modular Automation)**
- Functionality: Execute versioned analysis scripts (pattern scanning, entity enrichment, timeline building, similarity linking, relationship engine, summarization, export generation) with full audit trails and reproducible outputs
- Purpose: Automate investigator-friendly artifact generation while preserving provenance and avoiding accusatory outputs
- Trigger: Scripts execute automatically after ingestion stages (post-download, post-extraction, post-chunking, post-index, post-entity) or manually by Analysts
- Progression: Script triggered → validate inputs → execute with sandboxing → generate findings/timeline/proposals → log run with hashes → surface outputs in UI → queue reviewer approvals when needed
- Success criteria: Every script run recorded with version hash, config hash, input hashes, and output hashes; all outputs explainable with evidence; proposals require Reviewer approval; scripts are idempotent and replayable

**Reviewer Proposal Workflow**
- Functionality: Review and approve/reject proposals for entity merges, alias additions, and relationship upgrades generated by analysis scripts
- Purpose: Maintain human oversight for high-impact changes while preserving reversibility and audit trails
- Trigger: Analysis script generates a proposal requiring reviewer approval
- Progression: Script creates proposal → surfaces in Proposals view → Reviewer examines evidence → approves or rejects with notes → change applied or discarded → logged in audit trail
- Success criteria: All proposals show confidence, evidence snippets, reversibility status; approved changes are logged and reversible; rejected proposals retain justification

**OCR/Text Quality Scoring**
- Functionality: Compute per-page and per-document quality metrics (text density, OCR confidence proxies, character error heuristics, layout quality, language consistency, readability) and flag low-quality pages for re-OCR or manual review
- Purpose: Identify documents requiring reprocessing to ensure corpus reliability
- Trigger: Quality scoring script runs post-extraction or manually
- Progression: Extract document text → compute quality metrics → generate quality badge → flag for review if below threshold → surface in review queue with reprocess recommendation
- Success criteria: Quality badge displays overall score with breakdown; low-quality documents automatically queued for review; reprocess workflow available per document/page

**Near-Duplicate Detection & Canonicalization**
- Functionality: Detect identical or near-identical PDFs/pages/chunks using hashes and similarity fingerprints; collapse duplicates into canonical records while preserving all source URLs and download events
- Purpose: Reduce corpus noise, speed search, and maintain provenance for all duplicate copies
- Trigger: Deduplication script runs post-index or manually
- Progression: Compute document hashes → detect exact matches → compute similarity fingerprints → identify near-duplicates → create canonical mapping → preserve all provenance metadata
- Success criteria: Duplicate groups show canonical document with list of duplicate sources; all original URLs and download timestamps preserved; search returns canonical documents only

**Review Queues & Tasking**
- Functionality: Create queues for low OCR quality, ambiguous entities, relationship proposals, sensitive content flags, export requests, translation review, and structured extraction review; add assignments, due dates, and reviewer sign-off
- Purpose: Enable team-scale operations with accountability and workflow management
- Trigger: Scripts or analysts flag items requiring human review
- Progression: Item added to queue with priority → analyst views queue dashboard → assigns to team member → reviewer examines evidence → completes with notes → item marked complete with timestamp
- Success criteria: Queue dashboard shows counts by type and priority; items display status, assignee, due date; completed items retain review notes and sign-off

**Claims vs Evidence Annotations**
- Functionality: Create annotations labeled as Evidence Quote (mandatory citations), Interpretation, Hypothesis, or To-Verify; enforce citation requirements for Evidence Quotes
- Purpose: Keep teams honest and prevent narrative drift by requiring explicit evidence backing
- Trigger: Analyst creates annotation while reviewing documents
- Progression: Select annotation type → enter content → add citations (required for Evidence Quotes) → tag with categories → save → link to other annotations
- Success criteria: Evidence Quotes cannot be saved without at least one required citation; all annotations display type badge, citations with snippets, tags, and creation metadata; annotations searchable and linkable

**Multilingual Detection & Translation Workflow**
- Functionality: Auto-detect language per chunk and optionally translate into analyst language while preserving originals; translations clearly labeled as machine-generated with confidence
- Purpose: Support multilingual corpora without losing original text fidelity
- Trigger: Language detection script runs post-chunking or manually
- Progression: Detect language → store detection with confidence → optionally translate to target language → label translation as machine-generated → link translation to original chunk → surface in search with language facets
- Success criteria: Language detection displays confidence and script code; translations never overwrite originals; machine-generated label always present; search supports per-language filtering

**Temporal Normalization & Uncertainty Model**
- Functionality: Represent dates with uncertainty levels (certain, year-only, month-only, approximate, range, unknown) and show raw date phrase alongside normalized value
- Purpose: Avoid false precision and support timeline filtering by confidence
- Trigger: Temporal normalization script runs post-entity extraction
- Progression: Extract date entities → attempt normalization → classify uncertainty level → store raw phrase and normalized date → surface in timeline with confidence badges
- Success criteria: Dates display uncertainty level; raw phrase shown alongside normalized value; timeline supports filtering by confidence; never guess missing years

**Relationship Edge Explainers**
- Functionality: For every graph edge, compute and display a short neutral explanation with evidence snippets; require at least one snippet per edge
- Purpose: Improve trust and reduce hallucinated connections with transparent explanations
- Trigger: Relationship explainer script runs post-relationship generation
- Progression: Analyze relationship → extract evidence snippets → generate neutral explanation → verify prohibited terms not used → link snippets to graph edge
- Success criteria: Every edge displays explanation with computation method; evidence snippets linked and clickable; neutral language verified; no accusatory terms present

**Structured Table/Form Extraction**
- Functionality: Detect tables and common form layouts (headers, checkboxes, stamped fields) and extract into structured JSON; link fields back to page coordinates
- Purpose: Enable querying by specific fields and reduce reliance on keyword search
- Trigger: Structured extraction script runs post-extraction or manually
- Progression: Analyze page layout → detect tables/forms → extract structure to JSON → store field coordinates → link to source page index → queue for review if low confidence
- Success criteria: Structured data displays field names and values; coordinates enable highlighting on source page; low-confidence extractions queued for manual review

## Edge Case Handling

- **Local Engine Not Running**: Show clear "Not Connected" state with setup instructions and link to LOCAL_ENGINE_SETUP.md
- **Pairing Expired**: Generate new pairing code automatically, show expiration timer in UI
- **Session Token Expired**: Auto-refresh before expiration; fallback to re-pairing if refresh fails
- **Provider API Key Invalid**: Mark provider as disabled, surface error in provider list, allow key rotation
- **Spending Cap Reached**: Pause jobs using that provider, notify user, require manual cap increase
- **Download Failures**: Retry with exponential backoff, surface in run error log, allow manual replay
- **Corrupted PDFs**: Detect during extraction, mark status, attempt repair, escalate to admin if unrecoverable
- **OCR Failures**: Mark page as OCR-failed, continue with remaining pages, allow re-OCR at higher DPI
- **Entity Ambiguity**: Surface low-confidence entities separately, require reviewer approval for merges
- **Empty Search Results**: Show helpful suggestions, recent documents, or entity browse as fallback
- **Graph Overload**: Limit initial nodes, require filters for large graphs, provide zoom and pan controls
- **Concurrent Edits**: Last-write-wins with audit trail showing conflict, surface warnings on stale data
- **Rate Limit Exceeded**: Pause ingestion, show throttle status, auto-resume after cooldown period
- **Low Quality Documents**: Flag with quality badge, queue for review, offer reprocess workflow
- **Duplicate Documents**: Collapse into canonical record, preserve all source URLs, show duplicate count
- **Ambiguous Languages**: Show detection confidence, allow manual correction, flag for translation review
- **Uncertain Dates**: Display uncertainty level, show raw text alongside normalized value, never guess missing components
- **Translation Errors**: Label as machine-generated, show confidence, preserve original text, allow manual review
- **Missing Citations**: Block saving Evidence Quote annotations without required citations, show validation error
- **Review Queue Overload**: Sort by priority and due date, show urgent items prominently, enable bulk assignment
- **Sensitive Content**: Flag and queue for review, provide role-gated controls, default exports to redaction mode
- **Network Partition**: PWA shows "Offline" mode, queue write operations, sync when connection restored
- **Engine Crash**: Health check detects failure, show error state, preserve unsaved work in browser
- **Browser-Only Mode Limits**: Show clear warnings about speed and memory constraints for large files

## Design Direction

The design should evoke **forensic precision, institutional trust, and evidence-based clarity**—the aesthetic of a legal research library or intelligence analysis workstation. The interface must feel sober, methodical, and non-sensational, prioritizing readability and traceability over visual flourish.

## Color Selection

A dark-first color scheme emphasizing **deep navy foundations with amber accents** for an authoritative, research-focused atmosphere.

- **Primary Color**: Deep Navy `oklch(0.25 0.05 250)` - Communicates seriousness, institutional authority, and focus
- **Secondary Colors**: 
  - Muted Slate `oklch(0.35 0.02 250)` for secondary UI elements
  - Warm Charcoal `oklch(0.20 0.01 250)` for cards and elevated surfaces
- **Accent Color**: Amber Alert `oklch(0.75 0.15 70)` - Highlights critical actions, warnings, and key status indicators
- **Foreground/Background Pairings**:
  - Background (Dark Navy #0a1628): Light Text (oklch(0.95 0.01 250) #e8ecf3) - Ratio 13.2:1 ✓
  - Card (Warm Charcoal #1a1f2e): Light Text (oklch(0.95 0.01 250) #e8ecf3) - Ratio 11.8:1 ✓
  - Accent (Amber oklch(0.75 0.15 70)): Dark Text (oklch(0.15 0.01 250) #0d1421) - Ratio 9.1:1 ✓
  - Muted (Slate oklch(0.35 0.02 250)): Light Text (oklch(0.95 0.01 250)) - Ratio 7.2:1 ✓

## Font Selection

Typography should convey **technical precision and editorial authority**, balancing monospaced clarity for data with humanist readability for prose.

- **Typographic Hierarchy**:
  - H1 (Screen Titles): Space Grotesk Bold/32px/tight tracking (-0.02em)
  - H2 (Section Headers): Space Grotesk Semibold/24px/normal tracking
  - H3 (Subsection): Space Grotesk Medium/18px/normal tracking
  - Body (Readable Text): IBM Plex Sans Regular/15px/1.6 line-height
  - Metadata (Chips/Labels): IBM Plex Sans Medium/13px/0.02em tracking
  - Code/Hashes: JetBrains Mono Regular/14px/1.5 line-height
  - Captions: IBM Plex Sans Regular/13px/muted color

## Animations

Animations should reinforce **state transitions and evidence connections** without delaying workflow.

Subtle state transitions (200ms) for status chips and loading states; smooth page transitions (300ms) with directional context; elastic micro-interactions (150ms) on buttons to confirm actions; graph edge animations (400ms ease-out) when revealing evidence connections; no decorative motion that delays analyst workflows.

## API Surface (PWA ↔ Local Engine)

The PWA communicates with the Local Engine via a stable REST/JSON API with optional WebSocket for progress streaming.

**Authentication**:
- `POST /api/pairing/request` - Request pairing session (returns pairing code)
- `POST /api/pairing/complete` - Complete pairing (submit code, receive JWT token)
- `POST /api/auth/refresh` - Refresh session token
- `POST /api/auth/revoke` - Revoke session token

**Health & Status**:
- `GET /api/health` - Engine health check (services status, version)
- `GET /api/providers` - List configured LLM providers (no keys exposed)
- `GET /api/capabilities` - List available features (OCR, Whisper, embeddings, etc.)

**Projects**:
- `GET /api/projects` - List user projects
- `POST /api/projects` - Create new project
- `GET /api/projects/:id` - Get project details
- `GET /api/projects/:id/export` - Export project manifest
- `POST /api/projects/import` - Import project from manifest

**Sources & Ingestion**:
- `GET /api/sources` - List sources
- `POST /api/sources` - Create source
- `POST /api/sources/:id/runs` - Start ingestion run
- `GET /api/runs` - List ingestion runs
- `GET /api/runs/:id` - Get run details with progress
- `WS /api/runs/:id/stream` - Stream progress events

**Documents**:
- `GET /api/documents` - List documents (with filters)
- `GET /api/documents/:id` - Get document details
- `GET /api/documents/:id/text` - Get extracted text
- `GET /api/documents/:id/pages` - Get page metadata
- `POST /api/documents/:id/reprocess` - Trigger reprocessing

**Search**:
- `POST /api/search/keyword` - Keyword search with filters
- `POST /api/search/semantic` - Semantic/vector search
- `POST /api/search/export` - Export search results

**Entities & Graph**:
- `GET /api/entities` - List entities (with filters)
- `GET /api/entities/:id` - Get entity details
- `GET /api/entities/:id/mentions` - Get entity mentions
- `POST /api/entities/merge` - Merge entities (requires approval)
- `GET /api/graph` - Query relationship graph
- `POST /api/graph/export` - Export graph slice with citations

**Analysis Scripts**:
- `GET /api/scripts` - List available scripts
- `POST /api/scripts/:id/run` - Execute script
- `GET /api/script-runs` - List script runs
- `GET /api/script-runs/:id` - Get script run results

**Review & Annotations**:
- `GET /api/proposals` - List reviewer proposals
- `POST /api/proposals/:id/approve` - Approve proposal
- `POST /api/proposals/:id/reject` - Reject proposal
- `GET /api/queues` - List review queues
- `POST /api/annotations` - Create annotation
- `GET /api/annotations` - List annotations

**Exports**:
- `POST /api/exports/bundle` - Create evidence bundle
- `POST /api/exports/report` - Generate report (PDF/JSON/CSV)
- `GET /api/exports/:id` - Download export

**Audit**:
- `GET /api/audit` - Query audit log
- `GET /api/audit/llm-calls` - LLM usage audit (no keys logged)

## Component Selection

- **Components**:
  - **Sidebar**: Persistent navigation with collapsible sections for Sources, Documents, Search, Entities, Graph, Reports, Architecture
  - **Card**: Document cards, entity cards, run status cards, feasibility analysis cards with elevated surface treatment
  - **Badge**: Status indicators (Downloaded, Extracted, OCR Used, Indexed, Entity-Ready) with color-coded confidence levels
  - **Table**: Document lists, audit logs, entity mentions with sortable columns and row selection
  - **Tabs**: Switch between document text/OCR views, entity types, graph filters
  - **Dialog**: Source configuration, entity merge workflows, provenance details
  - **Sheet**: Slide-out panels for document quick-preview, entity details, relationship evidence
  - **Input/Textarea**: Search bars, filter inputs, entity name editing with clear validation states
  - **Select/Combobox**: Source selection, entity type filters, date range pickers
  - **Button**: Primary (Start Ingestion), Secondary (View Details), Destructive (Delete Source - admin only)
  - **Separator**: Visual breaks between provenance sections, metadata groups, and analysis sections
  - **ScrollArea**: Long document text, entity mention lists, audit event streams
  - **Tooltip**: Hover explanations for confidence scores, hash formats, processing status
  - **Alert**: System warnings (OCR failures, rate limiting, low confidence entities), feasibility notes
  - **Progress**: Ingestion run progress, document processing queues
  - **Checkbox/Switch**: Filter toggles (OCR used, high confidence only), feature flags

- **Customizations**:
  - **ProvenancePanel**: Custom component showing SHA-256 hash, source URL, discovery timestamp, download metadata, processing version in a structured layout
  - **EvidenceSnippet**: Custom component rendering text chunk with highlighted match, confidence score, and link to source document
  - **RelationshipEdge**: Custom graph edge visualization with evidence count badge and confidence-based styling
  - **ConfidenceBar**: Custom horizontal bar showing entity/relationship confidence with color gradient (amber for high, muted for low)
  - **FeasibilityCalculator**: Custom analysis cards showing timeline/cost breakdowns for large-scale processing scenarios

- **States**:
  - Buttons: Default (solid), Hover (brightness increase), Active (subtle scale), Disabled (muted with cursor-not-allowed)
  - Inputs: Default (border-input), Focus (ring-2 ring-accent), Error (border-destructive with error text), Success (border-accent subtle)
  - Status Chips: Color-coded by state (blue for in-progress, green for complete, amber for needs-review, red for error)

- **Icon Selection**:
  - **Database** for Sources, **Play** for Start Ingestion, **FileText** for Documents
  - **MagnifyingGlass** for Search, **UsersThree** for Entities, **Graph** for Relationship Graph
  - **FileArrowDown** for Downloads, **ScanSmiley** for OCR status, **Hash** for SHA-256
  - **ArrowsClockwise** for Reprocess, **ClockCounterClockwise** for Audit Log, **Gear** for Architecture
  - **Warning** for Errors, **CheckCircle** for Success, **Clock** for In Progress
  - **Export** for Exports, **ShieldCheck** for Provenance, **UserCircle** for RBAC
  - **Calculator** for Feasibility Analysis, **CurrencyDollar** for Cost Estimates, **ChartLine** for Timelines
  - **Microphone** for Audio Transcription, **Eye** for OCR Processing, **Flask** for Prototype Status

- **Spacing**: Consistent padding using 4/6/8/12/16/24px scale; card padding of 24px; list item padding of 12px vertical; section gaps of 32px

- **Mobile**: 
  - Sidebar collapses to hamburger menu
  - Document viewer switches to single-column with swipeable provenance drawer
  - Tables convert to card stack with key fields visible
  - Graph view provides touch zoom/pan with simplified legend
  - Search filters accessible via bottom sheet
