# Phases 9-11 Enhanced Implementation Plan

## Modern Legal Pro Workspace with Batch PDF Processing & AI Chat

**Status**: Ready for Implementation  
**Timeline**: 8-12 weeks (accelerated phases 9-11)  
**Priority**: CRITICAL - Foundation for legal workspace era

---

## Overview: The Legal Pro Workspace Vision

Transform Evident from a document analysis tool into a **comprehensive legal workspace** that:

1. **Batch processes 10-25 PDFs** simultaneously with OCR & context extraction
2. **Enables case-to-case knowledge transfer** (dismissed → new case reuse)
3. **Provides AI chat with persistent memory** (learns from user interactions)
4. **Manages multiple projects** with file storage and organization
5. **Supports split-window workflows** for simultaneous case work
6. **Operates on subscription model** with flexible BYOK enterprise option

---

## Phase 9 Enhanced: Testing Suite with Document Processing

**Timeline**: 2-3 weeks  
**Team**: QA Engineers (2), Document Processing Specialist (1)  
**Focus**: Validate existing code + NEW batch PDF/OCR pipeline

### 9.1 Existing Test Suite (from Phase 9 roadmap)

- 500+ unit tests (models, services)
- 300+ integration tests
- 150+ AI/ML tests
- 100+ compliance tests
- Performance benchmarks

### 9.2 NEW: Batch PDF Processing Test Suite

**Components to Test**:

```
tests/
├── batch_processing/
│   ├── test_pdf_batch_loader.py (50 tests)
│   ├── test_ocr_extraction.py (40 tests)
│   ├── test_document_context_extraction.py (45 tests)
│   ├── test_case_knowledge_graph.py (35 tests)
│   └── test_batch_integration.py (30 tests)
```

#### Test 1: PDF Batch Loading

```python
def test_batch_load_pdf_documents():
    """Load 10-25 PDFs concurrently"""
    pdf_files = [f'sample_{i}.pdf' for i in range(25)]
    loader = PDFBatchLoader(max_concurrent=5)

    results = loader.load_batch(pdf_files)

    assert len(results) == 25
    assert all(r['status'] == 'loaded' for r in results)
    assert all(r['page_count'] > 0 for r in results)
    assert sum(r['file_size_bytes'] for r in results) < 500_000_000  # 500MB total

def test_batch_load_with_error_handling():
    """Handle corrupted/invalid PDFs gracefully"""
    pdf_files = ['valid.pdf', 'corrupted.pdf', 'missing.pdf', 'valid2.pdf']
    loader = PDFBatchLoader(skip_errors=True)

    results = loader.load_batch(pdf_files)

    assert results[0]['status'] == 'loaded'
    assert results[1]['status'] == 'error'  # Corrupted
    assert results[2]['status'] == 'error'  # Missing
    assert results[3]['status'] == 'loaded'
    assert len(results[1]['error_message']) > 0
```

#### Test 2: OCR Extraction

```python
def test_ocr_extraction_high_accuracy():
    """Extract text from scanned PDFs with 95%+ accuracy"""
    pdf = load_scanned_pdf('legal_document.pdf')
    ocr_engine = OCREngine(model='tesseract-v5')

    result = ocr_engine.extract_text(pdf)

    assert result['confidence'] >= 0.95
    assert len(result['text']) > 1000
    assert result['page_count'] == pdf.page_count
    assert 'defendant' in result['text'].lower() or 'plaintiff' in result['text'].lower()

def test_ocr_batch_performance():
    """OCR 25 PDFs (100 pages) in < 5 minutes"""
    pdfs = [load_pdf(f'document_{i}.pdf') for i in range(25)]
    ocr_engine = OCREngine()

    start_time = time.time()
    results = ocr_engine.batch_extract(pdfs, workers=4)
    duration = time.time() - start_time

    assert duration < 300  # 5 minutes
    assert len(results) == 25
    assert all(r['confidence'] > 0.90 for r in results)
```

#### Test 3: Document Context Extraction

```python
def test_extract_legal_context():
    """Extract case-specific context from document"""
    text = """
    CASE NO. 2023-CV-12345
    Plaintiff: John Smith v. Defendant: Acme Corp

    The court finds that...
    The defendant failed to...
    Relief requested: $500,000 in damages
    """

    extractor = DocumentContextExtractor()
    context = extractor.extract(text)

    assert context['case_number'] == '2023-CV-12345'
    assert context['parties'] == {
        'plaintiff': 'John Smith',
        'defendant': 'Acme Corp'
    }
    assert context['relief_requested'] == '$500,000 in damages'
    assert context['violations'] == ['Breach of contract', 'Negligence']
```

#### Test 4: Case Knowledge Graph

```python
def test_build_case_knowledge_graph():
    """Build semantic graph linking case elements"""
    case_docs = [
        {'id': 1, 'type': 'complaint', 'text': '...'},
        {'id': 2, 'type': 'discovery', 'text': '...'},
        {'id': 3, 'type': 'motion', 'text': '...'}
    ]

    graph_builder = CaseKnowledgeGraphBuilder()
    graph = graph_builder.build(case_docs)

    assert graph.num_nodes == 50+  # Entities from documents
    assert graph.num_edges == 100+  # Relationships
    assert 'case_number' in graph.nodes
    assert 'defendant' in graph.nodes
    assert graph.has_edge('complaint', 'motion')
```

#### Test 5: Batch Integration Workflow

```python
def test_full_batch_workflow():
    """End-to-end: Load 10 PDFs → OCR → Extract → Graph"""
    pdf_files = [f'legal_case_{i}.pdf' for i in range(10)]

    workflow = BatchDocumentWorkflow()
    result = workflow.process_batch(pdf_files)

    assert result['pdfs_loaded'] == 10
    assert result['pdfs_processed'] == 10
    assert result['errors'] == 0
    assert result['total_pages'] > 50
    assert result['knowledge_graph']['num_nodes'] > 20
    assert result['duration_seconds'] < 120
```

### 9.3 Test Infrastructure

**New Test Fixtures**:

```python
# tests/fixtures/sample_documents.py
@pytest.fixture
def sample_pdfs():
    """10 sample legal PDFs for batch testing"""
    return [
        generate_fake_complaint(),
        generate_fake_discovery(),
        generate_fake_motion(),
        # ... 7 more PDFs
    ]

@pytest.fixture
def dismissed_case_docs():
    """Case dismissed without prejudice"""
    return {
        'complaint': load_from_disk('dismissed_complaint.pdf'),
        'discovery': load_from_disk('dismissed_discovery.pdf'),
        'certification': load_from_disk('dismissed_certification.pdf')
    }
```

### Success Criteria

- ✓ 1,000+ tests total (500 existing + 500 new)
- ✓ 90%+ code coverage
- ✓ All batch PDF tests passing
- ✓ OCR accuracy >= 95%
- ✓ Batch processing <= 5 min for 25 PDFs

---

## Phase 10 Enhanced: FastAPI with Chat & Memory

**Timeline**: 3-4 weeks  
**Team**: Backend Engineers (3), ML Engineer (1)  
**Focus**: Async API + Chat system + Project management

### 10.1 Existing FastAPI Endpoints (from Phase 10 roadmap)

- 6 core endpoints (violations, forensics, discovery)
- Async task processing
- Background tasks and caching

### 10.2 NEW: Batch Document Processing API

**Endpoint: POST /api/v2/documents/batch-analyze**

```python
@app.post("/api/v2/documents/batch-analyze")
async def batch_analyze_documents(
    request: BatchDocumentRequest,
    background_tasks: BackgroundTasks
) -> AsyncTaskResponse:
    """
    Process 10-25 PDFs simultaneously

    Request:
    {
        "project_id": "proj_123",
        "case_id": 456,
        "pdf_files": ["file1.pdf", "file2.pdf", ...],
        "extract_context": true,
        "build_knowledge_graph": true,
        "perform_ocr": true
    }

    Response:
    {
        "task_id": "task_abc123",
        "status": "processing",
        "pdfs_count": 12,
        "estimated_duration_seconds": 180
    }
    """
    task_id = create_task_id()
    background_tasks.add_task(
        process_batch_documents,
        task_id,
        request
    )
    return {
        "task_id": task_id,
        "status": "processing",
        "pdfs_count": len(request.pdf_files),
        "estimated_duration_seconds": len(request.pdf_files) * 15
    }
```

**Endpoint: GET /api/v2/documents/batch-status/{task_id}**

```python
@app.get("/api/v2/documents/batch-status/{task_id}")
async def get_batch_status(task_id: str) -> Dict:
    """
    Response:
    {
        "task_id": "task_abc123",
        "status": "processing",
        "progress": 45,
        "processed": 5,
        "total": 12,
        "current_file": "document_5.pdf",
        "results": {
            "document_1.pdf": {
                "status": "complete",
                "pages": 25,
                "text_extracted": 15000,
                "confidence": 0.98
            }
        }
    }
    """
```

**Endpoint: POST /api/v2/documents/compare-cases**

```python
@app.post("/api/v2/documents/compare-cases")
async def compare_cases(
    request: CompareCasesRequest
) -> Dict:
    """
    Compare dismissed case with new case
    Extract reusable elements and certifications

    Request:
    {
        "dismissed_case_id": 789,
        "new_case_id": 456,
        "extract_certifications": true,
        "find_similar_violations": true,
        "build_template": true
    }

    Response:
    {
        "comparison_id": "comp_xyz789",
        "dismissed_case_id": 789,
        "new_case_id": 456,
        "shared_violations": [
            {
                "violation_type": "breach_of_contract",
                "confidence": 0.92,
                "citations": ["Jones v. Smith (2023)"]
            }
        ],
        "reusable_certifications": [
            {
                "type": "authentication",
                "text": "I certify that...",
                "applicable": true
            }
        ],
        "suggested_template": "..."
    }
    """
```

### 10.3 NEW: AI Chat System with Memory

**Components**:

#### Chat Message Service

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: int (PK)
    chat_id (FK → Chat)
    user_id (FK → User)
    project_id (FK → Project) (optional)

    role: str ("user", "assistant", "system")
    content: str  # Message text
    context: JSON  # Embedded context
    citations: List[str]  # Supporting documents

    embeddings: List[float]  # For semantic search

    created_at: datetime
    updated_at: datetime

class Chat(Base):
    __tablename__ = "chats"

    id: int (PK)
    user_id (FK → User)
    project_id (FK → Project)

    title: str  # "Contract Review - Acme Corp"
    system_prompt: str  # Custom instructions
    model: str  # "gpt-4", "claude-3", etc.

    messages: Relationship[ChatMessage]
    memory_items: Relationship[ChatMemory]

    created_at: datetime
    last_active: datetime

    # Settings
    preserve_context: bool  # Keep full history
    max_context_tokens: int
    temperature: float
    top_p: float
```

#### Chat Memory Service

```python
class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id: int (PK)
    chat_id (FK → Chat)

    key: str  # "case_number", "defendant_name", "damages_claimed"
    value: JSON  # Extracted fact/value
    confidence: float (0-1)

    source_message_id (FK → ChatMessage)
    learned_at: datetime
    usage_count: int  # Times referenced

    category: str  # "case_fact", "legal_principle", "custom"

class ChatMemoryService:
    async def extract_facts_from_message(self, message: str) -> List[ChatMemory]:
        """Extract learnable facts from user message"""
        # Uses LLM to identify key facts
        facts = await llm.extract_facts(message)
        return facts

    async def retrieve_relevant_memory(self, context: str) -> List[ChatMemory]:
        """Find relevant learned facts for response generation"""
        # Semantic search over memory
        embedding = await embedder.embed(context)
        memory_items = await db.vector_search('chat_memory', embedding)
        return memory_items

    async def generate_response_with_memory(self, chat_id: int, user_message: str):
        """Generate response informed by learned memory"""
        # Retrieve relevant memory
        relevant_memory = await self.retrieve_relevant_memory(user_message)

        # Build context
        memory_context = "\n".join([
            f"{m.key}: {m.value}" for m in relevant_memory
        ])

        # Generate response
        system_prompt = f"""
        You are a legal assistant with access to this learned information:

        {memory_context}

        Use this context to provide better responses.
        """

        response = await llm.generate(
            messages=chat_messages,
            system_prompt=system_prompt
        )

        return response
```

**Chat Endpoints**:

```python
@app.post("/api/v2/chat/create")
async def create_chat(request: CreateChatRequest):
    """
    Request:
    {
        "project_id": "proj_123",
        "title": "Contract Review - Acme Corp",
        "system_prompt": "You are a legal expert..."
    }
    """

@app.post("/api/v2/chat/{chat_id}/message")
async def send_chat_message(
    chat_id: int,
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks
):
    """
    Request:
    {
        "content": "What violations did we find?",
        "include_project_context": true,
        "citations": ["doc_123", "doc_456"]
    }

    Response: WebSocket stream of tokens OR polling
    {
        "message_id": 789,
        "content": "Based on our analysis...",
        "memory_updated": true,
        "facts_learned": 3,
        "citations": ["...", "..."]
    }
    """

@app.get("/api/v2/chat/{chat_id}/memory")
async def get_chat_memory(chat_id: int):
    """
    Response:
    {
        "chat_id": 100,
        "memory_items": [
            {"key": "defendant", "value": "Acme Corp", "confidence": 0.99, "learned_at": "2024-01-15"},
            {"key": "case_type", "value": "Contract Dispute", "confidence": 0.95}
        ]
    }
    """

@app.get("/api/v2/chat/{chat_id}/messages")
async def get_chat_history(chat_id: int, limit: int = 50):
    """Full conversation history with context"""
```

### 10.4 NEW: Project Management API

**Data Models**:

```python
class Project(Base):
    __tablename__ = "projects"

    id: int (PK)
    user_id (FK → User)

    name: str  # "Acme Corp Litigation"
    description: str
    case_id (Optional, FK → LegalCase)

    # File storage
    documents: Relationship[ProjectDocument]
    chats: Relationship[Chat]
    cases: Relationship[LegalCase]

    # Settings
    storage_limit_bytes: int  # 1GB for paid, unlimited enterprise
    storage_used_bytes: int
    visibility: str  # "private", "shared", "team"

    created_at: datetime
    updated_at: datetime
    last_accessed: datetime
    archived: bool

class ProjectDocument(Base):
    __tablename__ = "project_documents"

    id: int (PK)
    project_id (FK → Project)

    filename: str
    original_filename: str
    file_type: str  # "pdf", "docx", "txt"
    file_size_bytes: int
    file_path: str  # S3 or local storage

    # Processing
    processing_status: str  # "uploaded", "processing", "complete"
    ocr_applied: bool
    text_extracted: str
    page_count: int

    # Metadata
    uploaded_at: datetime
    processed_at: datetime
    tags: List[str]  # For organization
```

**Project Endpoints**:

```python
@app.post("/api/v2/projects/create")
async def create_project(request: CreateProjectRequest):
    """Create new workspace project"""

@app.post("/api/v2/projects/{project_id}/upload-documents")
async def upload_project_documents(project_id: int, files: List[UploadFile]):
    """Upload files to project (10-25 at once)"""

@app.get("/api/v2/projects/{project_id}")
async def get_project_details(project_id: int):
    """Get project info + files + chats"""

@app.post("/api/v2/projects/{project_id}/chats")
async def get_project_chats(project_id: int):
    """List all chats in project"""

@app.delete("/api/v2/projects/{project_id}/archive")
async def archive_project(project_id: int):
    """Archive project (soft delete)"""
```

### Success Criteria

- ✓ Batch document upload/processing functional
- ✓ PDF OCR working at 95%+ accuracy
- ✓ Chat message creation and retrieval working
- ✓ Memory extraction and retrieval working
- ✓ Project management CRUD complete
- ✓ All endpoints async and responsive (<200ms basic)

---

## Phase 11 Enhanced: Vector DB with Case Knowledge

**Timeline**: 2-3 weeks  
**Team**: ML Engineer (1-2), Data Engineer (1)  
**Focus**: Semantic search + case knowledge graph

### 11.1 Case Knowledge Graph

**Entities to Extract & Index**:

```
Case Elements:
├── Parties (plaintiff, defendant, court, judge)
├── Violations (from legal_violations model)
├── Documents (complaint, discovery, motion, settlement)
├── Statutes (cited laws and regulations)
├── Precedents (case law citations)
├── Damages (claimed amounts, awarded)
├── Timelines (key dates and deadlines)
├── Certifications (sworn statements)
└── Remedies (relief requested/granted)

Relationships:
├── party_defendant_in_case
├── case_cites_statute
├── statute_prohibits_action
├── precedent_applies_to_violation
├── document_supports_claim
├── certification_attests_fact
└── case_preceded_by_case (for dismissed → new)
```

**Graph Building Service**:

```python
class CaseKnowledgeGraphBuilder:
    def __init__(self, vector_db):
        self.vector_db = vector_db  # Pinecone/Weaviate

    async def build_from_documents(self, case_id: int, documents: List[str]):
        """Build knowledge graph from case documents"""

        # Step 1: Extract entities
        entities = await self._extract_entities(documents)

        # Step 2: Build relationships
        relationships = await self._build_relationships(entities)

        # Step 3: Embed and index
        await self._index_graph_elements(case_id, entities, relationships)

        return {
            "case_id": case_id,
            "num_entities": len(entities),
            "num_relationships": len(relationships),
            "entity_types": self._count_by_type(entities)
        }

    async def _extract_entities(self, documents: List[str]):
        """Use Legal-BERT to find case entities"""
        # NER on steroids
        # Find: parties, amounts, dates, statutes, precedents
        pass

    async def _build_relationships(self, entities):
        """Determine relationships between entities"""
        pass

    async def search_similar_cases(self, case_id: int, top_k: int = 10):
        """Find cases with similar knowledge graphs"""
        # Use graph embedding similarity
        pass
```

### 11.2 Case-to-Case Transfer Service

**Dismissed → New Case Knowledge Transfer**:

```python
class CaseKnowledgeTransferService:
    async def transfer_case_knowledge(
        self,
        dismissed_case_id: int,
        new_case_id: int,
        transfer_types: List[str] = ["violations", "certifications", "precedents"]
    ):
        """
        Transfer learned facts from dismissed case to new case

        transfer_types:
        - "violations": Copy violation patterns (if similar)
        - "certifications": Reuse relevant certifications
        - "precedents": Find applicable case law
        - "templates": Generate motions from old patterns
        """

        # Load both cases' knowledge graphs
        dismissed_graph = await self.get_case_graph(dismissed_case_id)
        new_graph = await self.get_case_graph(new_case_id)

        transfer_report = {
            "violations_transferred": 0,
            "certifications_reusable": [],
            "precedents_applicable": [],
            "templates_generated": []
        }

        if "violations" in transfer_types:
            # Find violations from dismissed case
            violations = dismissed_graph.get_node_category("violation")

            # Check relevance to new case
            for v in violations:
                similarity = await self.similarity_score(v, new_case_id)
                if similarity > 0.75:  # 75%+ match
                    transfer_report["violations_transferred"].append({
                        "type": v.type,
                        "similarity": similarity,
                        "from_dismissed": dismissed_case_id,
                        "to_new": new_case_id
                    })

        if "certifications" in transfer_types:
            # Extract certifications from dismissed case
            certs = dismissed_graph.get_node_category("certification")

            for cert in certs:
                if self._is_reusable(cert, new_case_id):
                    transfer_report["certifications_reusable"].append({
                        "type": cert.type,
                        "text": cert.text,
                        "adaptations_needed": self._get_adaptations(cert, new_case_id)
                    })

        if "precedents" in transfer_types:
            # Find precedents from dismissed case
            precedents = dismissed_graph.get_node_category("precedent")

            # Check if applicable to new violations
            for p in precedents:
                if self._applies_to_new_case(p, new_case_id):
                    transfer_report["precedents_applicable"].append({
                        "citation": p.citation,
                        "holding": p.holding,
                        "relevance": "high"
                    })

        if "templates" in transfer_types:
            # Generate motion templates from old case
            motion_history = await self.get_motion_history(dismissed_case_id)

            for motion in motion_history:
                template = self._generate_template(motion, new_case_id)
                transfer_report["templates_generated"].append({
                    "motion_type": motion.type,
                    "template_id": template.id,
                    "adaptations": template.required_changes
                })

        return transfer_report

    async def _get_adaptations(self, certification, new_case_id):
        """What needs to change in this certification for new case"""
        return [
            "Update party names (Old: ABC Corp → New: XYZ LLC)",
            "Update dates (2022 → 2024)",
            "Update court jurisdiction"
        ]
```

### 11.3 Vector Indices for Case Search

**Namespaces to Create**:

```
pinecone/
├── case_documents/
│   ├── documents (full texts)
│   ├── violations (patterns)
│   └── precedents (case citations)
│
├── dismissed_cases/
│   ├── certifications (reusable)
│   ├── violations (transferable)
│   └── templates (motion patterns)
│
├── new_cases/
│   └── current_analysis (working analysis)
│
└── legal_concepts/
    ├── statutory_elements (what proves violation)
    ├── burden_of_proof (burden allocations)
    └── damages_theories (how to calculate)
```

**Search Endpoint**:

```python
@app.post("/api/v2/search/similar-cases")
async def search_similar_cases(request: SimilarCaseSearchRequest):
    """
    Find dismissed cases with similar elements

    Request:
    {
        "case_id": 456,
        "search_type": "violations",
        "top_k": 10,
        "min_similarity": 0.75
    }

    Response:
    {
        "query_case_id": 456,
        "similar_cases": [
            {
                "case_id": 789,
                "case_name": "Smith v. Jones",
                "similarity_score": 0.92,
                "shared_violations": ["breach_of_contract", "fraud"],
                "precedents_shared": [...]
            }
        ]
    }
    """
```

### Success Criteria

- ✓ Case knowledge graphs built successfully
- ✓ Cross-case similarity search <100ms
- ✓ Knowledge transfer functional
- ✓ Certification reuse working
- ✓ Template generation producing valid motions

---

## Integration Architecture: Batch PDF → Chat → Knowledge

```
User uploads 10-25 PDFs to project
    ↓
[Phase 9] Batch OCR & Context Extraction
    ↓ (stores extracted text + context in DB)
[Phase 10] Chat Interface accesses documents
    ├─ LLM analyzes documents
    ├─ Chat remembers key facts (memory service)
    └─ Knowledge graph built incrementally
    ↓
[Phase 11] Vector DB indexes all elements
    ├─ Enables semantic search
    ├─ Finds similar dismissed cases
    └─ Transfers knowledge to new case
    ↓
Chat provides intelligent responses:
- "Here are violatio similar dismissed case"
- "Here's a reusable certification from ABC v. XYZ"
- "Here's a template motion you can adapt"
```

### Data Flow

```
PDFs (10-25)
    ↓
Batch Loader
    ↓
OCR Engine
    ↓ (text + confidence)
Context Extractor
    ↓ (parties, case #, violations)
Knowledge Graph Builder
    ↓ (entities + relationships)
Vector Embeddings
    ↓ (Legal-BERT embeddings)
Pinecone Vector DB
    ↓
Chat Memory Service (stores facts)
    ↓
Chat responses (with context + memory)
    ↓
Similar Case Finder (for dismissed cases)
    ↓
Knowledge Transfer (reuse certifications)
```

---

## Technology Stack

### Batch Processing

- **PDF Reading**: PyPDF2, pdfplumber, PyMuPDF
- **OCR**: Tesseract 5, EasyOCR, PaddleOCR (fallback)
- **Async Orchestration**: asyncio, concurrent.futures
- **Error Handling**: Exponential backoff, retry logic

### Chat System

- **LLM**: GPT-4, Claude 3 (or local LLaMA)
- **LangChain**: For memory, RAG chains
- **WebSocket**: Real-time message streaming
- **Vector Embeddings**: Legal-BERT (768-dim)

### Knowledge Graph

- **Graph DB**: Neo4j (for relationship queries)
- **Vector DB**: Pinecone (for semantic search)
- **Entity Extraction**: spaCy NER + Legal-BERT

### Storage

- **Documents**: S3/Azure Blob (cloud) or local
- **Metadata**: PostgreSQL
- **Cache**: Redis (chat history, searches)

---

## Multi-Chat Window Architecture (UI)

### Split-Window Layout

```
┌─────────────────────────────────────────────┐
│ Project: Acme Corp Litigation               │
├─────────────────────────────────────────────┤
│ Chat 1: Contract Review │ Chat 2: Discovery │
│ ┌──────────────────────┬──────────────────┐ │
│ │ Q: What violations?  │ Q: Motion draft?  │ │
│ │ A: Found 3 critical  │ A: Here's motiontpl│ │
│ │    violations...     │    ready to adapt │ │
│ │                      │                   │ │
│ │ [Send]               │ [Send]            │ │
│ └──────────────────────┴──────────────────┘ │
│                                              │
│ [+ New Chat]  [Split View]  [Research Panel]│
└─────────────────────────────────────────────┘
```

### UI Components

1. **Chat Window** (each can be dragged, resized, split)
2. **Project Sidebar** (files, chats, cases)
3. **Document Viewer** (PDF with highlights)
4. **Memory Panel** (learned facts sidebar)
5. **Search Panel** (similar cases, precedents)
6. **Results Panel** (violations, certifications, templates)

---

## Enhanced Features

### 1. Batch OCR (10-25 PDFs)

- Concurrent processing (4-8 workers)
- Target: 5 min for 25 PDFs (25 pages avg)
- Error handling (corrupted PDFs skip)
- Progress tracking

### 2. Case Reuse

- Extract certifications from dismissed case
- Find similar violations in new case
- Suggest applicable precedents
- Generate motion templates

### 3. AI Chat Memory

- Learns facts from user messages
- Remembers across sessions
- Retrieves relevant facts for responses
- Maintains context window

### 4. Project Management

- Upload 10-25 PDFs at once
- Organize chats by topic
- Tag documents
- Archive/restore projects

### 5. Split-Window Workflows

- Multiple chats simultaneously
- Drag-and-drop chat windows
- Real-time synchronization
- Independent memory per chat

---

## Implementation Sequence

**Week 1-2 (Phase 9)**

- Batch PDF loader with error handling
- OCR engine integration
- Context extraction (parties, case #)
- 200+ tests

**Week 3-4 (Phase 10)**

- FastAPI batch endpoints
- Chat system models + services
- Project management endpoints
- Memory extraction + retrieval

**Week 5-6 (Phase 10 contd.)**

- WebSocket for real-time chat
- Chat history persistence
- Memory fact learning
- URL migration testing

**Week 7-9 (Phase 11)**

- Knowledge graph building
- Vector embeddings
- Pinecone indexing
- Similar case finder
- Knowledge transfer service

**Week 10-12 (Phase 11 contd.)**

- Case-to-case transfers
- Certification reuse service
- Motion template generator
- Integration testing

---

## Success Metrics

### Phase 9

- [ ] 1000+ tests (90%+ coverage)
- [ ] OCR accuracy >= 95%
- [ ] Batch processing <= 5 min for 25 PDFs

### Phase 10

- [ ] Batch upload/process working
- [ ] Chat message send/receive <500ms
- [ ] Memory facts extracted and retrievable
- [ ] Project CRUD 100% functional

### Phase 11

- [ ] Knowledge graphs built for all cases
- [ ] Similar case search <100ms
- [ ] Knowledge transfer reusability >= 70%
- [ ] Chat using memory in responses

---

## Deliverables

1. **Batch PDF Processing Module** (pyrequests/OCR/extraction)
2. **Chat System** (models, services, endpoints)
3. **Project Management** (models, CRUD endpoints)
4. **Knowledge Graph** (entity extraction, relationships)
5. **Vector DB Integration** (Pinecone setup, indices)
6. **Case Transfer Service** (dismissed → new case reuse)
7. **1,000+ Integration Tests**
8. **API Documentation** (OpenAPI/Swagger)
9. **Chat UI Components** (React components for Phase 13)

---

## Next Steps

1. ✅ Review this plan
2. Begin Phase 9 testing suite immediately
3. Set up test fixtures for PDFs
4. Begin Phase 10 API endpoint implementation alongside tests
5. Coordinate with Phase 13 UI team on chat interface
