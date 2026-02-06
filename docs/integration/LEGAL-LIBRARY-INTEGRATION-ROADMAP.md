# Legal Reference Library - Integration Roadmap

## ✅ Phase 1: Core Infrastructure (COMPLETE)

- [x] Database schema (4 tables)
- [x] REST API (11 endpoints)
- [x] Citation parser
- [x] Document ingestion (PDF/DOCX/TXT)
- [x] Web scraping (CourtListener)
- [x] Full-text search
- [x] User annotations
- [x] Access control

--

## 🔧 Phase 2: AI Tool Integration (IN PROGRESS)

### ChatGPT Integration

**File:** `chatgpt_legal_library_integration.py`

- [x] Integration class created
- [ ] Hook into `/api/v1/chat/message` endpoint
- [ ] Search library on user questions
- [ ] Enhance system prompt with relevant cases
- [ ] Format citations as clickable links
- [ ] Test with live ChatGPT conversations

**Integration Points:**

```python
# In api/chatgpt.py, add:
from chatgpt_legal_library_integration import ChatGPTLegalLibraryIntegration

library_integration = ChatGPTLegalLibraryIntegration()

# In chat endpoint:
relevant_cases = library_integration.search_library_for_context(user_message)
enhanced_prompt = library_integration.enhance_system_prompt(base_prompt, relevant_cases)
response = library_integration.format_citation_links(chatgpt_response)
```

--

### Document Optimizer Integration

**File:** `document_optimizer_library_integration.py`

- [x] Integration class created
- [ ] Hook into `legal_document_optimizer.py`
- [ ] Auto-suggest citations when optimizing
- [ ] Verify citations exist in library
- [ ] Add citation coverage metrics to reports
- [ ] Test with real legal documents

**Integration Points:**

```python
# In legal_document_optimizer.py, add:
from document_optimizer_library_integration import DocumentOptimizerLibraryIntegration

class LegalDocumentOptimizer:
    def __init__(self):
        self.library_integration = DocumentOptimizerLibraryIntegration()

    def optimize_document(self, text):
        suggestions = self.library_integration.suggest_citations_for_document(text)
        enhanced_prompt = self.library_integration.enhance_optimization_prompt(base_prompt, text)
        # ... optimization logic
```

--

### Violation Finder Integration

**File:** `violation_finder_library_integration.py` (TODO)

- [ ] Create integration class
- [ ] Link violations to precedent cases
- [ ] Auto-cite relevant case law in reports
- [ ] Example: Miranda violation → Miranda v. Arizona

**Planned Structure:**

```python
class ViolationFinderLibraryIntegration:
    def link_violation_to_precedent(self, violation_type):
        """Find precedent case for violation"""

    def enhance_violation_report(self, violations):
        """Add case law citations to report"""
```

--

### Evidence Analyzer Integration

**File:** `evidence_analyzer_library_integration.py` (TODO)

- [ ] Create integration class
- [ ] Reference legal standards from case law
- [ ] Cite evidentiary rules from library
- [ ] Example: Hearsay analysis → Crawford v. Washington

--

## 📱 Phase 3: MAUI Mobile/Desktop UI

### Legal Library Page

**File:** `src/Evident.MatterDocket.MAUI/Views/LegalLibraryPage.cs`

- [x] Placeholder created
- [ ] Implement search UI
- [ ] Implement document viewer
- [ ] Implement annotation UI
- [ ] Implement citation browser
- [ ] Implement related cases view
- [ ] Implement import dialog

**UI Components Needed:**

```
✓ Search bar with filters
✓ Results list (CollectionView)
✓ Document viewer (WebView or RichTextEditor)
✓ Annotation toolbar (highlight, note, tag)
✓ Citation network graph
✓ Import from CourtListener dialog
✓ Upload PDF/DOCX dialog
```

### ChatViewModel Integration

**File:** `src/Evident.MatterDocket.MAUI/ViewModels/ChatViewModel.cs`

- [ ] Add "Legal Library" tool button
- [ ] Show relevant cases during chat
- [ ] Click citation to open in library
- [ ] Suggest importing cited cases

--

## 🚀 Phase 4: Advanced Features

### Batch Import Tool

**File:** `batch_import_foundation_cases.py`

- [x] Script created
- [ ] Test with CourtListener API
- [ ] Add progress tracking
- [ ] Add error recovery
- [ ] Create import queue system
- [ ] Add rate limiting

**Usage:**

```bash
# Import all foundation cases
python batch_import_foundation_cases.py all

# Import specific practice area
python batch_import_foundation_cases.py civil_rights

# Import custom list
python batch_import_foundation_cases.py -custom citations.txt
```

--

### Citation Network Visualization

**File:** `citation_network_visualizer.py` (TODO)

- [ ] Build citation graph
- [ ] Visualize with D3.js or similar
- [ ] Show cases cited BY this case
- [ ] Show cases citing THIS case
- [ ] Interactive navigation

--

### Shepardize Integration

**File:** `shepardize_integration.py` (TODO)

- [ ] Check case validity
- [ ] Flag overruled cases
- [ ] Show treatment (positive, negative, neutral)
- [ ] Integrate with Westlaw/Lexis (if API available)

--

### Vector Embeddings Search

**File:** `legal_library_embeddings.py` (TODO)

- [ ] Generate embeddings for cases (OpenAI)
- [ ] Semantic search (find similar cases)
- [ ] Topic clustering
- [ ] Auto-categorization

--

## 🧪 Phase 5: Testing & Quality Assurance

### Integration Tests

**File:** `tests/test_legal_library_integration.py`

- [x] Test file created
- [ ] Implement API endpoint tests
- [ ] Implement citation parser tests
- [ ] Implement ChatGPT integration tests
- [ ] Implement Document Optimizer tests
- [ ] Implement search accuracy tests
- [ ] Add performance benchmarks

**Test Coverage Goals:**

```
✓ Citation parser: 100%
✓ API endpoints: 100%
✓ Search functionality: 95%
✓ Integration hooks: 90%
✓ MAUI UI: 85%
```

--

## 📊 Phase 6: Analytics & Metrics

### Usage Analytics (TODO)

- [ ] Track most searched cases
- [ ] Track most annotated passages
- [ ] Track citation network usage
- [ ] Track integration usage (ChatGPT, Optimizer)
- [ ] Generate usage reports

### Performance Metrics (TODO)

- [ ] Search performance (target: <100ms)
- [ ] Import performance
- [ ] Citation linking performance
- [ ] Database query optimization

--

## 🎯 Priority Order

### Immediate (This Week)

1. ✅ Core infrastructure (DONE)
2. 🔧 ChatGPT integration (IN PROGRESS)
3. 🔧 Document Optimizer integration (IN PROGRESS)
4. 📱 MAUI search UI
5. 🚀 Batch import testing

### Short-term (This Month)

6. Violation Finder integration
7. Evidence Analyzer integration
8. MAUI document viewer
9. MAUI annotation UI
10. Integration tests

### Long-term (Next Quarter)

11. Citation network visualization
12. Vector embeddings search
13. Shepardize integration
14. Analytics dashboard
15. Team library sharing

--

## 📝 Integration Checklist

### For Each AI Tool Integration:

- [ ] Create `{tool}_library_integration.py`
- [ ] Implement search/suggest logic
- [ ] Enhance prompts with library context
- [ ] Add citation verification
- [ ] Update tool's main file to use integration
- [ ] Write integration tests
- [ ] Update documentation
- [ ] Test with real use cases

### For Each MAUI UI Component:

- [ ] Create `.xaml` and `.cs` files
- [ ] Implement data binding
- [ ] Add API client calls
- [ ] Implement navigation
- [ ] Add loading indicators
- [ ] Add error handling
- [ ] Test on all platforms (Windows, iOS, Android)
- [ ] Update user guide

--

## 🆘 Known Issues & TODOs

### High Priority

- [ ] Fix Unicode encoding in app.py print statements (partial fix applied)
- [ ] Add foreign key constraints when `cases` table exists
- [ ] Implement rate limiting for CourtListener API
- [ ] Add pagination to search results

### Medium Priority

- [ ] Improve citation parser accuracy (state reporters)
- [ ] Add full-text search indexing (FTS5)
- [ ] Implement relevance scoring algorithm
- [ ] Add document caching

### Low Priority

- [ ] Add export to Zotero
- [ ] Add export to PDF with annotations
- [ ] Add sharing/collaboration features
- [ ] Add mobile offline mode

--

**Last Updated:** January 27, 2026  
**Status:** Phase 1 complete, Phase 2 in progress  
**Next Milestone:** ChatGPT integration live
