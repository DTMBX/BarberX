# FORENSIC-GRADE DISCOVERY PIPELINE — INTEGRATION GUIDE
## 5-Module Architecture for Evident Technologies

---

## QUICK START

```bash
# 1. Install dependencies
pip install -r requirements-forensic-grade.txt

# 2. Run migrations
flask db upgrade

# 3. Configure services
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/0"

# 4. Start Celery worker (for batch processing)
celery -A src.tasks.celery_app worker --loglevel=info

# 5. Deploy modules via Spark (see Spark Prompts below)
```

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVIDENCE INPUT STREAM                            │
│  (PDF, Video, Email, Documents, Discovery Batches)                 │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐        ┌────────▼─────────┐
        │   CLASSIFIER   │        │  TIMELINE        │
        │   (1)          │        │  EXTRACTOR       │
        │ Responsive?    │        │  (4)             │
        │ Irrelevant?    │        │ Extract dates &  │
        │ Privileged?    │        │ events           │
        └────────┬───────┘        └────────┬─────────┘
                 │                         │
                 │        ┌────────────────┴──────────────┐
                 │        │                               │
        ┌────────▼──────┐ │  ┌──────────────┬──────────────┐
        │  PRIVILEGE     │ │  │              │              │
        │  DETECTOR      │ │  │              │              │
        │  (3)           │ │  │              │              │
        │ Attorney-      │ │  │              │              │
        │ client?        │ │  │              │              │
        └────────┬───────┘ │  │              │              │
                 │         │  │              │              │
        ┌────────▼────────────▼──────────────▼──────────────▼────┐
        │                                                        │
        │        CHAIN-OF-CUSTODY AUDIT LOGGER (2)             │
        │                                                        │
        │  ✓ Immutable event stream                           │
        │  ✓ Cryptographic signatures                         │
        │  ✓ Non-repudiation timestamps                       │
        │  ✓ Full audit trail for legal review                │
        │                                                        │
        └────────┬────────────────────────────────────────────┬─┘
                 │                                            │
        ┌────────▼────────────────────────────────────────────▼─────┐
        │                                                            │
        │        BATCH DISCOVERY PROCESSOR (5) — ORCHESTRATOR       │
        │                                                            │
        │  Async pipeline for 100+ documents:                      │
        │  • Parallel classification                              │
        │  • Progress tracking & resumable jobs                   │
        │  • Error handling & retry logic                         │
        │  • Results aggregation                                  │
        │                                                            │
        └────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  POSTGRESQL - Forensic Schema              │
        │  ├─ classifier_models & classifications   │
        │  ├─ chain_of_custody_audit_log             │
        │  ├─ privilege_detections                  │
        │  ├─ timeline_events & case_timelines      │
        │  └─ batch_jobs & batch_job_tasks          │
        └────────────────────────────────────────────┘

DATABASE LAYER (PostgreSQL):
├── Immutable audit log with Merkle-tree chaining
├── JSONB for flexible event metadata
├── Index strategy for court-admissible queries
└── Full-text search for discovery
```

---

## 5 MODULES — DEPLOYMENT VIA SPARK

### Module 1: Discovery Document Classifier

**What it does**: Auto-classify documents as responsive/irrelevant/privileged

**Spark Prompt Template**:
```
You are building a forensic-grade document classifier for legal discovery.

CONTEXT:
- Target: Self-represented litigants processing discovery without paralegal help
- Urgency: Automatic classification in <2 seconds per document
- Accuracy: >92% precision (minimize false-positives that miss responsive docs)
- Explainability: SHAP scores for every classification decision (for audit)

REQUIREMENTS:
1. Fine-tune BERT-legal on our training set
   - Input: Document text (up to 10K tokens)
   - Output: {"classification": "responsive|irrelevant|privileged", "confidence": 0.92, "explanation": "..."}
   - Model: Use transformers library with sentence-transformers as fallback

2. Implement model versioning
   - Store in PostgreSQL: classifier_models table
   - Track: accuracy, precision, recall, F1, AUC-ROC
   - A/B testing: is_production flag for safe rollout

3. SHAP Explainability
   - Use shap.TreeExplainer (XGBoost) or shap.TransformerExplainer (BERT)
   - Return top-5 features driving the classification
   - Store in DocumentClassification.shap_values for audit trail

4. Batch Integration
   - Accept batch_job_id parameter
   - Update progress: processed_count in batch_jobs table
   - Store results in document_classifications table

5. Error Handling
   - Graceful fallback to "uncertain" (human review needed)
   - Log all errors to chain_of_custody_audit_log
   - Retry with exponential backoff via Celery

DELIVERABLE:
- File: src/ai/discovery_classifier.py (400-500 lines)
- Test: tests/test_discovery_classifier.py
- API: POST /api/v1/classify-documents (batch or single)
- Uses: transformers, scikit-learn, shap
```

### Module 2: Chain-of-Custody Audit Logger

**What it does**: Immutable event log with cryptographic timestamps for legal defensibility

**Spark Prompt Template**:
```
You are building a forensic-grade audit logging system for a legal eDiscovery platform.

CONTEXT:
- Requirement: Every evidence interaction must be logged for legal review
- Admissibility: Logs must be defensible in court (non-repudiation, authenticity)
- Integrity: Cannot be modified without detection
- Scale: 10,000+ events/day per case

REQUIREMENTS:
1. Immutable Event Stream
   - Table: chain_of_custody_audit_log (see forensic_schema.py)
   - Events: Evidence uploaded, viewed, downloaded, classified, shared, deleted
   - Metadata: User, IP, timestamp (UTC), action result

2. Cryptographic Hashing (SHA-256 + Merkle Chain)
   - Each event: event_hash = SHA256(previous_hash + event_data)
   - Purpose: Break the chain if ANY event is modified
   - Verify chain integrity with validate_chain() function

3. Timestamps with UTC Precision
   - event_timestamp: UTC normalized (no timezone conversion errors)
   - Use pytz & dateutil for precision
   - Log both "when event happened" AND "when we logged it"

4. Non-Repudiation via Digital Signatures (Optional)
   - RSA 2048 signature of event (using cryptography library)
   - Store signature in audit_log.signature
   - Verify with public key for legal defensibility

5. Query Interface for Legal Review
   - GET /api/v1/audit-trail?case_id=...&date_range=...
   - Return: Chronological events with signatures intact
   - Export to PDF with tamper-proof formatting

6. Audit Trail Analytics
   - Chain breaks detected (alerts for tampering)
   - User activity by role (attorney, paralegal, admin)
   - Evidence hotspots (most-accessed documents)

DELIVERABLE:
- File: src/services/chain_of_custody_logger.py (300-400 lines)
- Test: tests/test_chain_of_custody.py
- API: POST /api/v1/audit-log (auto-called on evidence actions)
- Uses: cryptography, merkle-tree, sqlalchemy-audit
```

### Module 3: Privilege Detection Refiner

**What it does**: Improve accuracy of attorney-client privilege detection

**Spark Prompt Template**:
```
You are building an improved privilege detection system for legal discovery.

CONTEXT:
- Compliance: Accidentally releasing privileged docs = malpractice liability
- Trade-off: High precision (minimize false-negatives) over speed
- Training: You'll use labeled data from past cases
- Accuracy baseline: 87% precision, 89% recall (improve to >92% both)

REQUIREMENTS:
1. Multi-Model Ensemble
   - Model A: spaCy NER (named entity recognition) to find "attorney", "legal advice"
   - Model B: BERT fine-tuned on privilege language
   - Model C: Sentiment/tone analysis (formal, legalistic tone = more likely privileged)
   - Ensemble: Weighted vote (test different weights via A/B)

2. Feature Engineering
   - Lexical: presenceOf(["confidential", "privileged", "legal advice"])
   - Syntactic: Document structure (memo with "RE: Legal Analysis")
   - Semantic: Sentence-transformers to find "attorney-client communication" concepts
   - Metadata: Email headers (from attorney's domain, subject line)

3. Training Pipeline
   - Input: Labeled dataset (~1000 docs: privileged vs. non-privileged)
   - Split: 70% train, 15% val, 15% test
   - Metrics: Precision, recall, F1, confusion matrix
   - Validation: Cross-validation to prevent overfitting

4. Model Versioning & A/B Testing
   - Table: privilege_detection_models
   - Deploy: New model as "testing", compare against "production"
   - Rollout: is_production flag when > 95% confidence

5. Review Workflow
   - Store: PrivilegeDetection.review_status = "pending" initially
   - Human review: Lawyer approves/disputes classification
   - Feedback loop: Use disputes to retrain model

6. Audit Trail
   - Log: Every privilege assertion to chain_of_custody_audit_log
   - Field: privilege_type (attorney-client, work-product, none)
   - Evidence: Excerpt + keywords that triggered detection

DELIVERABLE:
- File: src/ai/privilege_detector.py (400+ lines)
- Test: tests/test_privilege_detector.py
- API: POST /api/v1/detect-privilege
- Uses: spacy, transformers, vaderSentiment, bertopic, sklearn
```

### Module 4: Evidence Timeline Builder

**What it does**: Extract dates/events from multimodal evidence and build chronology

**Spark Prompt Template**:
```
You are building a timeline extraction system for legal discovery evidence.

CONTEXT:
- Purpose: Help lawyers see "what happened when" across documents, emails, videos
- Multimodal: Extract dates from text (emails), video metadata, audio transcripts
- Scale: Build timeline from 500+ pieces of evidence
- Visualization: Interactive timeline UI for case presentation

REQUIREMENTS:
1. Date Extraction from Text
   - Library: dateparser (flexible natural language dates)
   - Input: "As discussed on March 15, 2023..."
   - Output: DateTime(2023-03-15)
   - Precision: "exact", "approximate", "year_only"

2. Event Extraction from Documents
   - Extract: Sentences containing dates + actions
   - NLP: Use spaCy to find events (verbs + entities)
   - Example: "John signed the contract on July 1, 2022"
   - Output: TimelineEvent(date=2022-07-01, title="Contract signed", entities={people: ["John"]})

3. Multimodal Sources
   - Email: Headers (Date: ...) + body content
   - Video: Metadata + transcript timestamps (from Whisper)
   - Audio: Transcription timestamps
   - Documents: Creation date + embedded dates in text

4. Entity Linking
   - Extract: People, locations, organizations mentioned
   - Relationships: "John and Mary discussed..." → link entities
   - Store: TimelineEvent.entities (JSONB)

5. Timeline Relationships
   - Graph: Which events are causally related?
   - Types: precedes, contradicts, reinforces
   - Example: "Email sent" → precedes "Meeting held"

6. Conflict Detection
   - Find: Contradictory dates in different sources
   - Alert: Timeline inconsistencies (crucial for disproving claims)
   - Store: CaseTimeline.conflicts

7. Visualization
   - JSON output: Pre-computed for UI rendering
   - Format: [{date: "2023-01-15", events: [{title: "...", evidence_id: "..."}]}]
   - Interactive: Plotly for zoom/pan

DELIVERABLE:
- File: src/ai/timeline_builder.py (400+ lines)
- Test: tests/test_timeline_builder.py
- API: POST /api/v1/extract-timeline
- Returns: CaseTimeline JSON + conflicts
- Uses: dateparser, spacy, pandas, plotly, networkx
```

### Module 5: Batch Discovery Processor

**What it does**: Async pipeline orchestrating Modules 1-4 for 100+ documents

**Spark Prompt Template**:
```
You are building an async batch processor for forensic discovery tasks.

CONTEXT:
- Scale: Process 100-1000 documents without blocking the user
- Orchestration: Run Classifier → Timeline → Privilege Detector in sequence
- Progress: Real-time updates on UI (WebSocket)
- Resumability: User can pause/resume mid-batch
- Error handling: Fail individual items, continue batch

REQUIREMENTS:
1. Job Definition & Queuing
   - JobType: "classify_batch", "extract_timeline", "detect_privilege", "full_discovery"
   - Queue: Redis + Celery for async tasks
   - Status: queued → processing → completed (or failed)

2. Task Scheduling
   - Celery topology:
     • task_classify_document(evidence_id, batch_job_id)
     • task_extract_timeline(evidence_id, case_id)
     • task_detect_privilege(evidence_id, batch_job_id)
   - Chain/parallel: Classify first, then timeline + privilege in parallel
   - Retry: Exponential backoff for transient failures

3. Progress Tracking
   - Update: BatchJob.progress_percent + processed_count every N items
   - WebSocket: Real-time progress push to client
   - Persist: progress in Redis (fast updates) + PostgreSQL (durability)

4. Error Handling
   - Per-task errors: Log to batch_job_tasks.error, continue batch
   - Batch errors: If >10% failures, alert user
   - Retry logic: Max 3 retries with exponential backoff
   - Dead letter queue: Failed items sent to "review" queue

5. Results Aggregation
   - Aggregate: Classification stats (45 responsive, 23 irrelevant, 5 uncertain)
   - Store: BatchJob.results_summary (JSONB)
   - Timeline: Merged timeline across all evidence
   - Privilege report: Flagged documents for attorney review

6. Resumability & State Management
   - Pause: User can pause job, state saved to BatchJob
   - Resume: Restart from last checkpoint (don't reprocess done items)
   - Cleanup: Automatic cleanup of old jobs (>30 days) from Celery

7. API Endpoints
   - POST /api/v1/batch-jobs (create job)
   - GET /api/v1/batch-jobs/{job_id} (get status)
   - PUT /api/v1/batch-jobs/{job_id}/pause (pause)
   - PUT /api/v1/batch-jobs/{job_id}/resume (resume)
   - GET /api/v1/batch-jobs/{job_id}/results (download results CSV)

8. Monitoring & Observability
   - Metrics: Job duration, tasks completed/failed, error rate
   - Logs: JSON structured logs (python-json-logger)
   - Alerts: Failed jobs notify admin

DELIVERABLE:
- File: src/tasks/discovery_batch_processor.py (500+ lines)
- File: src/services/batch_job_service.py (300+ lines)
- Test: tests/test_batch_processor.py
- API: src/api/batch_routes.py
- Uses: celery, redis, sqlalchemy, tqdm, pydantic, flower
```

---

## INTEGRATION CHECKLIST

### Phase 1: Foundation
- [ ] Install forensic-grade dependencies: `pip install -r requirements-forensic-grade.txt`
- [ ] Run migrations: `flask db upgrade` (uses forensic_schema.py)
- [ ] Set environment: REDIS_URL, CELERY_BROKER_URL

### Phase 2: Build via Spark (One Module at a Time)
- [ ] **Module 2** (Audit Logger) — Deploy first, all others depend on it
- [ ] **Module 1** (Classifier) — Core discovery workflow
- [ ] **Module 3** (Privilege Detector) — Compliance/liability mitigation
- [ ] **Module 4** (Timeline Builder) — Visualization for lawyers
- [ ] **Module 5** (Batch Processor) — Orchestrate all above

### Phase 3: Integration Testing
```bash
# Test audit logging on evidence upload
pytest tests/test_chain_of_custody.py::test_immutable_chain

# Test classifier on sample documents
pytest tests/test_discovery_classifier.py::test_classification_accuracy

# Test batch job end-to-end
pytest tests/test_batch_processor.py::test_batch_job_full_workflow
```

### Phase 4: Deployment
- [ ] Configure Celery worker: `celery -A src.tasks worker --loglevel=info`
- [ ] Set up Flower monitoring: `celery -A src.tasks flower`
- [ ] Enable WebSocket for progress: Update frontend socket client
- [ ] Deploy with gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`

---

## DATABASE MIGRATIONS

```bash
# Create migration
flask db migrate -m "Add forensic schema (classifier, audit, privilege, timeline, batch)"

# Auto-detect schema changes from forensic_schema.py
flask db stamp head  # If starting fresh

# Apply
flask db upgrade

# Verify tables created
psql -d evident_db -c "\dt" | grep -E "classifier|audit|privilege|timeline|batch"
```

---

## SPARK-TO-LOCAL WORKFLOW

After building each module in Spark:

1. **Copy the Spark output** (src/ai/XXX.py or src/tasks/XXX.py)
2. **Place in local repo**: `c:\web-dev\github-repos\Evident\src\...`
3. **Run tests**: `pytest tests/test_XXX.py`
4. **Commit**: `git add . && git commit -m "Add [Module] via Spark"`
5. **Deploy Celery**: Worker picks up new tasks automatically

---

## KEY ARCHITECTURAL DECISIONS

| Aspect | Choice | Why |
|--------|--------|-----|
| **Async Framework** | Celery | Proven in legal-tech, Redis backend, Flower UI |
| **ML Framework** | Transformers (BERT) + XGBoost ensemble | BERT for NLP, XGBoost for explainability (SHAP) |
| **Hashing** | SHA-256 + Merkle tree | Industry standard, court-defensible, collisions impossible |
| **Timestamps** | UTC-normalized, pytz | No timezone ambiguity (critical for legal) |
| **Audit Trail** | PostgreSQL JSONB + append-only | Immutable, queryable, full-text searchable |
| **Explainability** | SHAP + LIME | Both model-agnostic and specific (SHAP for trees) |
| **Progress Tracking** | Redis + DB dual-write | Fast UI updates + durability if server crashes |

---

## LEGAL & COMPLIANCE NOTES

✅ **Chain of Custody**: Every action logged with timestamps + user + IP  
✅ **Non-Repudiation**: RSA signatures on audit events (optional but recommended)  
✅ **Privilege**: Automatic detection + human review required before production use  
✅ **FRCP Compliance**: Export-ready results (meet discovery rules)  
✅ **Data Minimization**: Stores only necessary metadata, documents referenced by ID  

---

## SUPPORT & TROUBLESHOOTING

**Celery tasks not running?**
```bash
celery -A src.tasks inspect active
```

**Audit log chain broken?**
```python
from src.services.chain_of_custody_logger import ChainValidator
ChainValidator.verify_chain(case_id="case_001")
```

**Classifier accuracy low?**
→ Retrain on recently-labeled cases (see privilege_detector training logic)

**Timeline conflicts?**
→ Review CaseTimeline.conflicts JSONB field for date mismatches

---

**Next**: Choose a module and post its Spark prompt to GitHub Copilot Spark. Start with **Module 2** (Audit Logger) — everything depends on it.
