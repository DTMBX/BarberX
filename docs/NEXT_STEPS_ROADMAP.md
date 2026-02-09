# Enterprise Upgrade - Next Steps Implementation Roadmap

## Overview

Five critical phases remain to complete the enterprise legal discovery platform. This roadmap prioritizes implementation in optimal dependency order, ensuring solid foundations before building higher-level capabilities.

---

## Phase Dependency Graph

```
Phase 9: Testing Suite (Foundation)
         ↓ (validates code quality)
Phase 10: FastAPI Migration (Async layer)
         ↓ (enables high-performance API)
Phase 11: Vector DB Integration (Intelligence)
         ↓ (semantic search, RAG)
Phase 12: Kubernetes Deployment (Infrastructure)
         ↓ (containerization, scaling)
Phase 13: Client UI Implementation (User Interface)
```

---

## Phase 9: Testing Suite ⏳ SCHEDULED

**Timeline**: 2-3 weeks  
**Team**: Backend QA Engineers (2-3)  
**Priority**: CRITICAL - Foundation for all downstream work  
**Deliverables**: 1,000+ test cases, 90%+ code coverage

### Objectives

- Validate all 20 new models
- Verify 8 services function correctly
- Ensure AI/ML integration works
- Establish testing standards for enterprise deployment

### Components

#### 9.1 Unit Tests

**Target**: 500+ tests  
**Files to Create**:

- `tests/unit/models/test_legal_violations.py` (50 tests)
- `tests/unit/models/test_forensic_media.py` (40 tests)
- `tests/unit/models/test_court_grade_discovery.py` (30 tests)
- `tests/unit/services/test_violation_detection_service.py` (100 tests)
- `tests/unit/services/test_forensic_media_service.py` (80 tests)
- `tests/unit/services/test_court_grade_discovery_service.py` (100 tests)
- `tests/unit/config/test_ai_ml_config.py` (50 tests)
- `tests/unit/config/test_fastapi_integration.py` (50 tests)

**Key Test Areas**:

```python
# Model tests
def test_legal_violation_creation()
def test_violation_confidence_scoring()
def test_forensic_audio_chain_of_custody()
def test_deepfake_detection_scoring()
def test_court_grade_package_compliance()
def test_qa_sampling_5_percent_calculation()

# Service tests
def test_basic_violation_detection()
def test_comprehensive_violation_detection()
def test_expert_violation_detection_with_precedents()
def test_audio_analysis_end_to_end()
def test_forensic_report_generation()
def test_discovery_production_workflow()
def test_frcp_compliance_validation()
```

#### 9.2 Integration Tests

**Target**: 300+ tests  
**Files to Create**:

- `tests/integration/test_violations_workflow.py`
- `tests/integration/test_forensic_workflow.py`
- `tests/integration/test_discovery_workflow.py`
- `tests/integration/test_ai_ml_loading.py`
- `tests/integration/test_async_orchestration.py`

**Workflows to Test**:

1. Evidence → Violation Detection → Reporting
2. Audio File → Forensic Analysis → Transcription → Report
3. Production Set → Compliance Checks → QA Sampling → Certification
4. Model Loading → Inference → Result Storage
5. Request → Background Task → Result Retrieval

#### 9.3 Performance & Load Tests

**Target**: 50+ tests  
**Files to Create**:

- `tests/performance/test_violation_detection_performance.py`
- `tests/performance/test_batch_processing.py`
- `tests/performance/test_database_queries.py`

**Key Metrics**:

```
- Violation detection: <100ms (basic), <2s (comprehensive)
- Audio analysis: 10-20x real-time
- Batch processing: 1,000+ docs/hour
- QA sampling: <5 min per 100 docs
- Database: <10ms per query
```

#### 9.4 AI/ML Model Tests

**Target**: 150+ tests  
**Files to Create**:

- `tests/ai_ml/test_legal_bert_loading.py`
- `tests/ai_ml/test_whisper_transcription.py`
- `tests/ai_ml/test_deepfake_detection.py`
- `tests/ai_ml/test_speaker_diarization.py`
- `tests/ai_ml/test_knowledge_base_search.py`

**Test Approach**:

- Load each model without error
- Validate inference on sample data
- Check output format compliance
- Measure inference latency
- Test fallback mechanisms

#### 9.5 System & Compliance Tests

**Target**: 100+ tests  
**Files to Create**:

- `tests/compliance/test_frcp_rules.py`
- `tests/compliance/test_fre_authentication.py`
- `tests/compliance/test_chain_of_custody.py`
- `tests/compliance/test_data_integrity.py`

**Compliance Checks**:

- ✓ FRCP completeness validation
- ✓ Metadata preservation
- ✓ Privilege protection
- ✓ Chain of custody integrity
- ✓ Hash verification
- ✓ Audit logging

#### 9.6 Test Infrastructure

**Framework**: pytest (already used)  
**Fixtures**: Comprehensive database and model fixtures  
**Coverage Tool**: pytest-cov targeting 90%+ coverage  
**CI/CD Integration**: GitHub Actions workflow

**Directory Structure**:

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── models/
│   ├── services/
│   └── config/
├── integration/
│   ├── test_violations_workflow.py
│   ├── test_forensic_workflow.py
│   └── test_discovery_workflow.py
├── performance/
│   ├── test_violation_detection_performance.py
│   ├── test_batch_processing.py
│   └── test_database_queries.py
├── ai_ml/
│   └── test_model_loading.py
├── compliance/
│   └── test_frcp_compliance.py
└── fixtures/
    ├── audio_samples/
    ├── video_samples/
    └── legal_documents/
```

**Running Tests**:

```bash
# All tests
pytest tests/ -v --cov --cov-report=html

# By type
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/performance/ -v

# Specific test
pytest tests/unit/services/test_violation_detection_service.py::test_basic_violation_detection -v
```

### Success Criteria

- ✓ 90%+ code coverage
- ✓ All tests passing
- ✓ No critical issues
- ✓ Performance benchmarks met
- ✓ Compliance tests passing

---

## Phase 10: FastAPI Migration ⏳ SCHEDULED

**Timeline**: 3-4 weeks  
**Team**: Backend Engineers (3-4), DevOps Specialist (1)  
**Priority**: HIGH - Essential for enterprise performance  
**Deliverables**: Async API layer, Flask compatibility bridge, performance improvements

### Objectives

- Implement full FastAPI endpoints
- Create Flask-to-FastAPI migration path
- Enable async task processing
- Maintain backward compatibility

### Components

#### 10.1 FastAPI Endpoint Implementation

**Violations Endpoint**:

```python
# POST /api/v2/violations/detect
# Background task for parallel violation detection
# Returns: task_id for polling status

# GET /api/v2/violations/{case_id}
# Get all violations for case

# GET /api/v2/violations/evidence/{evidence_id}
# Get violations for specific evidence

# POST /api/v2/violations/{violation_id}/approve
# Attorney approval workflow
```

**Forensics Endpoint**:

```python
# POST /api/v2/forensics/analyze-audio
# Submit audio for forensic analysis
# Returns: task_id

# POST /api/v2/forensics/analyze-video
# Submit video for forensic analysis

# GET /api/v2/forensics/audio/{id}/transcription
# Get transcription results

# GET /api/v2/forensics/reports/{id}
# Download forensic report
```

**Discovery Endpoint**:

```python
# POST /api/v2/discovery/productions
# Create discovery production

# GET /api/v2/discovery/productions/{id}
# Get production details

# POST /api/v2/discovery/productions/{id}/validate
# Run compliance checks

# POST /api/v2/discovery/productions/{id}/qa-sample
# Generate QA sample

# POST /api/v2/discovery/productions/{id}/certify
# Generate attorney certification

# POST /api/v2/discovery/productions/{id}/submit
# Submit to opposing party
```

**Admin/System Endpoints**:

```python
# GET /api/v2/health
# Service health

# GET /api/v2/models/status
# AI/ML model loading status

# GET /api/v2/config/ai-ml
# AI/ML configuration

# POST /api/v2/admin/models/load
# Manually load model

# GET /api/v2/admin/system/stats
# System statistics
```

#### 10.2 Async Task Processing

**Background Tasks**:

```python
@app.post("/api/v2/violations/detect")
async def detect_violations_async(
    request: ViolationDetectionRequest,
    background_tasks: BackgroundTasks
):
    task_id = create_task_id()
    background_tasks.add_task(
        process_violation_detection,
        task_id,
        request
    )
    return {"task_id": task_id, "status": "initiated"}

# Worker processes this
async def process_violation_detection(task_id: str, request: ViolationDetectionRequest):
    # Long-running detection
    results = await orchestrator.detect_violations(request)
    # Store results
    save_results(task_id, results)
```

**Task Queue**:

- Use Celery with Redis backend
- Or: Native async with background tasks
- Support task cancellation
- Implement retry logic
- Track progress

#### 10.3 Flask Compatibility Bridge

**Dual-Layer Approach**:

```python
# app.py (Flask) - routes to old endpoints still work
from flask import Flask
from fastapi_integration import app as fastapi_app

flask_app = Flask(__name__)

# Legacy routes still work
@flask_app.route('/legal/case/<case_id>/violations')
def get_violations_flask(case_id):
    # Calls FastAPI internally
    return call_fastapi_endpoint(f'/api/v2/violations/{case_id}')

# Gradual transition to FastAPI
# Eventually: Remove Flask, keep FastAPI only
```

**Migration Path**:

```
Week 1: Deploy FastAPI alongside Flask
Week 2: Redirect high-traffic endpoints to FastAPI
Week 3: Migrate remaining endpoints
Week 4: Remove Flask (or keep for legacy support)
```

#### 10.4 Performance Optimization

**Connection Pooling**:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

**Caching Strategy**:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_model_config(model_name: str):
    return AIMLConfig().get_model_config(model_name)

# Redis caching for longer-term
from redis import Redis
redis = Redis(host='localhost', port=6379)
```

**Batching & Streaming**:

```python
@app.post("/api/v2/violations/batch-detect")
async def batch_detect_violations(
    evidence_ids: List[int],
    analysis_level: str
):
    # Process in parallel batches
    results = await batch_processor.process_documents_batch(
        evidence_ids,
        detect_violations_async,
        analysis_level
    )
    yield results  # Stream results as available
```

### Success Criteria

- ✓ All endpoints functional
- ✓ 50%+ improvement in response times
- ✓ Support for concurrent requests
- ✓ Background tasks processing reliably
- ✓ Backward compatibility maintained

### Deployment Plan

- Deploy to staging environment first
- Run performance benchmarks
- Gradual traffic migration (10% → 50% → 100%)
- Rollback plan ready
- Monitor for 1 week before full production

---

## Phase 11: Vector Database Integration ⏳ SCHEDULED

**Timeline**: 2-3 weeks  
**Team**: ML Engineers (1-2), Data Engineers (1)  
**Priority**: HIGH - Powers semantic search and precedent lookup  
**Deliverables**: Vector embeddings pipeline, semantic search, RAG system

### Objectives

- Enable semantic legal search
- Implement precedent similarity matching
- Build retrieval-augmented generation (RAG) for legal analysis
- Reduce hallucinations in AI analysis

### Components

#### 11.1 Choice of Vector Database

**Option A: Pinecone (Cloud-Hosted) - Recommended**

```python
# Pros: Managed, scalable, no ops burden
# Cons: Monthly cost, external dependency

from pinecone import Pinecone

pc = Pinecone(api_key="xxx")
index = pc.Index("legal-precedents")
```

**Option B: Weaviate (Self-Hosted) - Enterprise**

```python
# Pros: Self-hosted, full control, GraphQL API
# Cons: Operational overhead

import weaviate
client = weaviate.Client("http://localhost:8080")
```

**Option C: Milvus (Open Source) - Premium**

```python
# Pros: High-performance, distributed, ML-native
# Cons: Complex setup, requires Kubernetes

from pymilvus import Collection, connections
connections.connect("default", host="localhost", port="19530")
```

**Recommendation**: Start with Pinecone for rapid deployment, migrate to Milvus for large-scale on-prem.

#### 11.2 Embedding Pipeline

**Step 1: Document Processing**

```python
from transformers import AutoTokenizer, AutoModel
import torch

class LegalDocumentEmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('nlpaueb/legal-bert-base-uncased')
        self.model = AutoModel.from_pretrained('nlpaueb/legal-bert-base-uncased')

    def embed_text(self, text: str) -> List[float]:
        """Generate 768-dim embedding from Legal-BERT"""
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # CLS token (sentence representation)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        return embedding.tolist()

    def embed_precedent(self, case_name: str, citation: str, holding: str) -> Dict:
        """Embed complete legal precedent"""
        combined_text = f"{case_name} ({citation}): {holding}"
        embedding = self.embed_text(combined_text)
        return {
            "id": f"case_{citation.replace('.', '_')}",
            "values": embedding,
            "metadata": {
                "case_name": case_name,
                "citation": citation,
                "holding": holding,
                "court": "SCOTUS",  # Could be Circuit, State, etc.
                "year": 2023
            }
        }
```

**Step 2: Batch Embedding & Indexing**

```python
async def index_scotus_decisions():
    """One-time: Index all SCOTUS decisions"""
    embedder = LegalDocumentEmbedder()
    index = pc.Index("legal-precedents")

    precedents = load_scotus_decisions()  # 35,000 cases

    batch_size = 100
    for i in range(0, len(precedents), batch_size):
        batch = precedents[i:i+batch_size]
        vectors_to_insert = [
            embedder.embed_precedent(p['name'], p['citation'], p['holding'])
            for p in batch
        ]
        index.upsert(vectors=vectors_to_insert, namespace="scotus")

    print(f"Indexed {len(precedents)} SCOTUS decisions")
```

**Step 3: Incremental Updates**

```python
async def index_new_decisions(decision_batch: List[Dict]):
    """Regularly: Add new precedents"""
    embedder = LegalDocumentEmbedder()
    index = pc.Index("legal-precedents")

    vectors = [embedder.embed_precedent(d['name'], d['citation'], d['holding'])
               for d in decision_batch]
    index.upsert(vectors=vectors)
```

#### 11.3 Semantic Search Service

**VectorSearchService**:

```python
class VectorSearchService:
    def __init__(self):
        self.embedder = LegalDocumentEmbedder()
        self.index = pc.Index("legal-precedents")

    async def search_precedents(self, query: str, top_k: int = 10) -> List[Dict]:
        """Find similar precedents to query"""
        query_embedding = self.embedder.embed_text(query)

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace="scotus",
            include_metadata=True
        )

        return [
            {
                "case_name": r['metadata']['case_name'],
                "citation": r['metadata']['citation'],
                "score": r['score'],  # 0-1 relevance
                "holding": r['metadata']['holding']
            }
            for r in results['matches']
        ]

    async def search_statutes(self, query: str, top_k: int = 10) -> List[Dict]:
        """Find relevant statutes"""
        query_embedding = self.embedder.embed_text(query)

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace="statutes",
            include_metadata=True
        )

        return results

    async def multi_namespace_search(self, query: str) -> Dict:
        """Search across all legal sources"""
        return {
            "scotus": await self.search_precedents(query),
            "circuits": await self.search_precedents(query, namespace="circuits"),
            "statutes": await self.search_statutes(query),
            "frcp": await self.search_rules(query, namespace="frcp"),
            "fre": await self.search_rules(query, namespace="fre")
        }
```

#### 11.4 Retrieval-Augmented Generation (RAG)

**RAG Pipeline for Violation Detection**:

```python
class LegalRAGService:
    def __init__(self):
        self.vector_search = VectorSearchService()
        self.llm = LangChain(model="gpt-4")  # Or local LLaMA

    async def generate_violation_analysis(
        self,
        evidence_text: str,
        violation_type: str
    ) -> Dict:
        """Generate legal analysis using precedents from vector DB"""

        # Step 1: Retrieve relevant precedents
        search_query = f"{violation_type} violation {evidence_text[:200]}"
        precedents = await self.vector_search.search_precedents(search_query, top_k=5)

        # Step 2: Retrieve relevant statutes/rules
        statutes = await self.vector_search.search_statutes(search_query, top_k=3)

        # Step 3: Build retrieval context
        context = f"""
You are a legal expert analyzing potential violations.

RELEVANT PRECEDENTS:
{json.dumps(precedents, indent=2)}

RELEVANT STATUTES/RULES:
{json.dumps(statutes, indent=2)}

EVIDENCE:
{evidence_text}

TASK: Analyze this evidence for {violation_type} violations.
1. Identify specific violations
2. Cite applicable precedents
3. Explain legal basis
4. Assess impact
"""

        # Step 4: Generate analysis with LLM using context
        analysis = await self.llm.agenerate(
            prompt=context,
            max_tokens=1000,
            temperature=0.3
        )

        return {
            "analysis": analysis,
            "precedents_used": precedents,
            "statutes_used": statutes,
            "confidence": 0.95  # High confidence with grounding
        }
```

#### 11.5 Integration with Violation Detection

**Enhanced ViolationDetectionService**:

```python
class EnhancedViolationDetectionService(ViolationDetectionService):
    def __init__(self):
        super().__init__()
        self.rag_service = LegalRAGService()

    async def detect_expert_violations(
        self,
        evidence: EvidenceItem,
        case: LegalCase
    ) -> List[dict]:
        """EXPERT level: Use RAG for deep analysis"""

        violations = await super()._detect_expert_violations(
            evidence.document_text,
            evidence,
            case
        )

        # Enhance with RAG
        for violation in violations:
            if violation['confidence'] > 0.80:
                rag_analysis = await self.rag_service.generate_violation_analysis(
                    evidence.document_text,
                    violation['category']
                )

                violation['rag_analysis'] = rag_analysis['analysis']
                violation['supporting_precedents'] = rag_analysis['precedents_used']
                violation['confidence'] = 0.98  # Boosted confidence

        return violations
```

### Namespaces to Create

```
Vector Database Structure:
├── scotus (35,000 decisions)
├── circuits (500,000 decisions)
├── statutes (50,000 statutes)
├── frcp (86 rules + commentary)
├── fre (1010 rules + commentary)
├── model_rules (60 rules + commentary)
├── case_law_citations (inter-case references)
└── legal_concepts (abstract concepts for fuzzy search)
```

### Success Criteria

- ✓ All legal sources embedded and indexed
- ✓ Sub-100ms search latency
- ✓ 95%+ precision in precedent matching
- ✓ RAG generating accurate legal analysis
- ✓ Violation confidence improved to 95%+

---

## Phase 12: Kubernetes Deployment ⏳ SCHEDULED

**Timeline**: 2-3 weeks  
**Team**: DevOps Engineers (2-3)  
**Priority**: MEDIUM - Enables production-grade deployment  
**Deliverables**: K8s manifests, helm charts, CI/CD pipeline

### Objectives

- Containerize all services
- Deploy to Kubernetes cluster
- Enable auto-scaling
- Implement monitoring and alerting
- Enable zero-downtime deployments

### Components

#### 12.1 Docker Containerization

**Dockerfile (Multi-stage build)**:

```dockerfile
# Base stage: Python with dependencies
FROM python:3.13-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Builder stage: ML models (heavy)
FROM base as builder

COPY requirements-media-ai.txt .
RUN pip install --no-cache-dir -r requirements-media-ai.txt

# Final stage: Runtime
FROM base as runtime

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

EXPOSE 5000 8000

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
```

**Docker Compose (for local development)**:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - '5000:5000'
      - '8000:8000'
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/evident
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - '8000:8000'
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/evident
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: evident
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - '5432:5432'

  redis:
    image: redis:7
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data

  vector-db:
    image: pinecone/pinecone:latest
    ports:
      - '6333:6333'
    environment:
      PINECONE_API_KEY: ${PINECONE_API_KEY}

volumes:
  postgres_data:
  redis_data:
```

#### 12.2 Kubernetes Manifests

**Deployment (Flask + FastAPI)**:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: evident-backend
  namespace: evident
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: evident-backend
  template:
    metadata:
      labels:
        app: evident-backend
    spec:
      containers:
        - name: web
          image: evident:latest
          ports:
            - containerPort: 5000
              name: flask
            - containerPort: 8000
              name: fastapi
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: evident-secrets
                  key: database-url
            - name: REDIS_URL
              value: redis://redis:6379
          resources:
            requests:
              cpu: '500m'
              memory: '512Mi'
            limits:
              cpu: '2000m'
              memory: '2048Mi'
          livenessProbe:
            httpGet:
              path: /api/v2/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v2/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

**Service**:

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: evident-backend
  namespace: evident
spec:
  type: LoadBalancer
  selector:
    app: evident-backend
  ports:
    - port: 5000
      targetPort: 5000
      name: flask
    - port: 8000
      targetPort: 8000
      name: fastapi
```

**HPA (Horizontal Pod Autoscaling)**:

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: evident-backend-hpa
  namespace: evident
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: evident-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Database StatefulSet**:

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: evident
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: evident
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ['ReadWriteOnce']
        resources:
          requests:
            storage: 100Gi
```

#### 12.3 Helm Chart

**Chart Structure**:

```
helm/evident/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-staging.yaml
├── values-prod.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   └── NOTES.txt
└── README.md
```

**values.yaml**:

```yaml
replicaCount: 3

image:
  repository: evident
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  flaskPort: 5000
  fastApiPort: 8000

resources:
  limits:
    cpu: 2000m
    memory: 2048Mi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

database:
  host: postgres
  port: 5432
  name: evident

redis:
  host: redis
  port: 6379
```

**Helm Install**:

```bash
# Install
helm install evident ./helm/evident -f values-prod.yaml -n evident

# Upgrade
helm upgrade evident ./helm/evident -f values-prod.yaml -n evident

# Rollback
helm rollback evident -n evident
```

#### 12.4 CI/CD Pipeline

**GitHub Actions Workflow**:

```yaml
# .github/workflows/deploy-k8s.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov
      - run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          registry: gcr.io
          username: _json_key
          password: ${{ secrets.GCP_SA_KEY }}
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: gcr.io/${{ secrets.GCP_PROJECT }}/evident:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: azure/setup-kubectl@v3
      - run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > $HOME/.kube/config
      - run: |
          helm upgrade --install evident ./helm/evident \
            -f values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            -n evident

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v3
      - uses: azure/setup-kubectl@v3
      - run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > $HOME/.kube/config
      - run: |
          helm upgrade --install evident ./helm/evident \
            -f values-prod.yaml \
            --set image.tag=${{ github.sha }} \
            -n evident
```

#### 12.5 Monitoring & Observability

**Prometheus Configuration**:

```yaml
# observability/prometheus.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'evident-backend'
    static_configs:
      - targets: ['localhost:8000'] # FastAPI metrics
      - targets: ['localhost:5000'] # Flask metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
```

**Grafana Dashboards**:

- Request latency by endpoint
- Error rate and types
- Model loading status
- Database query performance
- Vector DB search latency
- Pod resource usage
- Task queue depth

**Loki (Log Aggregation)**:

```yaml
# observability/loki-config.yaml
auth_enabled: false

ingester:
  chunk_idle_period: 3m
  max_chunk_age: 1h
  max_streams_per_user: 0
  lifecycler:
    ring:
      kvstore:
        store: inmemory

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema:
        version: v11
```

### Success Criteria

- ✓ Services run in K8s cluster
- ✓ Auto-scaling works (tested with load)
- ✓ Health checks passing
- ✓ Logging aggregated
- ✓ Metrics collected
- ✓ Zero-downtime deployments possible

---

## Phase 13: Client UI Implementation ⏳ SCHEDULED

**Timeline**: 3-4 weeks  
**Team**: Frontend Engineers (2-3), UX Designer (1)  
**Priority**: HIGH - Final user-facing layer  
**Deliverables**: React/Vue dashboard, workflows UI, reporting interface

### Objectives

- Build responsive web UI
- Implement violation detection dashboard
- Create forensic analysis viewer
- Build discovery production workflow UI
- Enable real-time progress tracking

### Components

#### 13.1 Technology Stack

**Frontend Framework**: React 18+ (or Vue 3)

- Components: React Query, React Hook Form, Tailwind CSS
- State: Redux or Zustand
- Real-time: WebSocket via Socket.io
- Charts: Recharts or Chart.js
- Rich Editor: Monaco Editor for code/documents

**Build**: Vite (faster than Create React App)
**Testing**: Vitest, React Testing Library
**Deployment**: Static hosting on Vercel/Netlify with API proxying

#### 13.2 UI Pages/Components

**Dashboard (Main Page)**:

```
- Quick Stats: Cases, violations found, pending tasks
- Recent Activities: Last 10 violations detected
- Task Queue: In-progress analysis tasks
- Quick Actions: "Analyze Document", "Create Production", etc.
```

**Violations Detection Page**:

```
Component Tree:
├── ViolationDashboard
│   ├── CaseSelector
│   ├── AnalysisLevelSelector (Basic/Comprehensive/Expert)
│   ├── DocumentUpload
│   ├── ViolationsList
│   │   ├── ViolationCard (each violation)
│   │   │   ├── ViolationType Badge
│   │   │   ├── SeverityIndicator
│   │   │   ├── ConfidenceScore
│   │   │   ├── ExtractedText
│   │   │   ├── LegalBasis
│   │   │   └── ExpertReviewButton
│   ├── ViolationFilters
│   │   ├── TypeFilter
│   │   ├── SeverityFilter
│   │   └── ConfidenceThreshold
│   └── ViolationStats
│       ├── Charts: Distribution by type/severity
│       └── Trends: Over time
```

**Forensic Analysis Page**:

```
Component Tree:
├── ForensicDashboard
│   ├── MediaUpload (drag-and-drop)
│   ├── AnalysisProgress
│   │   ├── ProgressBar
│   │   ├── StepIndicator (Metadata → Authenticity → Transcription → Report)
│   │   └── EstimatedTime
│   ├── AuthenticityVerdict
│   │   ├── VerdictBadge (Authentic/Questionable/Edited)
│   │   ├── ConfidenceGauge
│   │   └── DetailedFindings
│   ├── SpeakerIdentification (if audio)
│   │   ├── SpeakerTable
│   │   ├── SpeakerChart (speaking time)
│   │   └── SimilarityScores
│   ├── Transcription (if audio)
│   │   ├── FullTranscript
│   │   ├── SpeakerSegments
│   │   ├── SearchTranscript
│   │   └── DownloadButton
│   ├── ForensicReport
│   │   ├── ExecutiveSummary
│   │   ├── DetailedFindings
│   │   ├── Methodology
│   │   ├── CourtReadinessIndicator
│   │   └── DownloadPDF
│   └── ChainOfCustody
│       ├── Timeline
│       ├── Custodians
│       └── IntegrityStatus
```

**Discovery Production Page**:

```
Component Tree:
├── DiscoveryDashboard
│   ├── ProductionSelector
│   ├── ProductionStatus
│   │   ├── DocumentCount
│   │   ├── PageCount
│   │   ├── ComplianceReadiness
│   │   └── QAStatus
│   ├── ComplianceChecklist
│   │   ├── CheckItem (repeating)
│   │   │   ├── Checkbox
│   │   │   ├── CheckName
│   │   │   ├── Status (✓/✗/pending)
│   │   │   └── IssuesPanel
│   │   └── ComplianceSummary (%)
│   ├── QASamplingInterface
│   │   ├── SampleDisplay
│   │   ├── ChecklistForSample
│   │   ├── PassFailButtons
│   │   └── RemediationNotes
│   ├── Production Timeline
│   │   ├── DatelineCalendar
│   │   ├── Milestones
│   │   └── SubmissionTracker
│   └── CertificationPanel
│       ├── AttorneySelector
│       ├── CertificationPreview
│       └── SignButton
```

**Reporting Interface**:

```
Component Tree:
├── ReportsPage
│   ├── ReportTypeSelector
│   │   ├── ViolationReport
│   │   ├── ForensicReport
│   │   └── DiscoveryReport
│   ├── ReportBuilder
│   │   ├── CaseSelector
│   │   ├── DateRangeFilter
│   │   ├── IncludeOptions (checkboxes)
│   │   └── GenerateButton
│   ├── ReportPreview
│   │   ├── PDF Preview
│   │   ├── TableOfContents
│   │   ├── Charts/Graphics
│   │   └── DownloadButton
│   └── ReportHistory
│       ├── ReportList
│       ├── GeneratedDate
│       └── DownloadLinks
```

#### 13.3 API Integration

**React API Client**:

```typescript
// src/api/client.ts
import axios from 'axios';
import { io } from 'socket.io-client';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v2';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// WebSocket for real-time updates
export const socket = io(API_BASE.replace('/api/v2', ''), {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
});
```

**React Query Hooks**:

```typescript
// src/hooks/useViolations.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export function useDetectViolations() {
  return useMutation(async (formData) => {
    const { data } = await apiClient.post('/violations/detect', formData);
    return data;
  });
}

export function useViolationStatus(taskId: string) {
  return useQuery(
    ['violation-status', taskId],
    async () => {
      const { data } = await apiClient.get(`/tasks/${taskId}`);
      return data;
    },
    {
      refetchInterval: 1000, // Poll every second
    }
  );
}

export function useCaseViolations(caseId: number) {
  return useQuery(['case-violations', caseId], async () => {
    const { data } = await apiClient.get(`/violations/${caseId}`);
    return data;
  });
}
```

**WebSocket Events**:

```typescript
// Real-time task progress
socket.on('task-progress', (data) => {
  // Update UI with progress
  console.log(`Task ${data.taskId}: ${data.percentage}%`);
});

socket.on('task-complete', (data) => {
  // Show completion notification
  console.log(`Task ${data.taskId} complete`, data.result);
});

socket.on('error', (error) => {
  // Show error
  console.error('Task error:', error);
});
```

#### 13.4 Component Examples

**ViolationCard Component**:

```tsx
interface ViolationCardProps {
  violation: {
    id: number;
    type: string;
    category: string;
    severity: 'critical' | 'severe' | 'moderate' | 'minor';
    confidence: number;
    detectedText: string;
    explanation: string;
  };
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
}

export function ViolationCard({ violation, onApprove, onReject }: ViolationCardProps) {
  const severityColor = {
    critical: 'bg-red-100 border-red-500',
    severe: 'bg-orange-100 border-orange-500',
    moderate: 'bg-yellow-100 border-yellow-500',
    minor: 'bg-blue-100 border-blue-500',
  };

  return (
    <div className={`border-l-4 p-4 ${severityColor[violation.severity]}`}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold">{violation.category}</h3>
          <p className="text-sm text-gray-600">{violation.type}</p>
          <p className="mt-2 text-sm">{violation.explanation}</p>

          <div className="mt-3 p-2 bg-gray-100 rounded text-sm font-mono">
            "{violation.detectedText}"
          </div>
        </div>

        <div className="text-right">
          <div className="mb-2">
            <span className="text-lg font-bold">{(violation.confidence * 100).toFixed(0)}%</span>
            <p className="text-xs text-gray-500">confidence</p>
          </div>

          <button
            onClick={() => onApprove(violation.id)}
            className="bg-green-500 text-white px-3 py-1 rounded text-sm mr-2"
          >
            Approve
          </button>
          <button
            onClick={() => onReject(violation.id)}
            className="bg-gray-400 text-white px-3 py-1 rounded text-sm"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}
```

**ComplianceChecklist Component**:

```tsx
interface CheckResult {
  id: string;
  name: string;
  status: 'pass' | 'fail' | 'pending';
  issues?: string[];
}

export function ComplianceChecklist({ items }: { items: CheckResult[] }) {
  const passCount = items.filter((i) => i.status === 'pass').length;
  const failCount = items.filter((i) => i.status === 'fail').length;
  const percentage = Math.round((passCount / items.length) * 100);

  return (
    <div className="border rounded-lg p-4">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-bold">FRCP Compliance</h3>
          <span
            className={`font-bold ${percentage === 100 ? 'text-green-500' : 'text-yellow-500'}`}
          >
            {percentage}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-green-500 h-2 rounded-full" style={{ width: `${percentage}%` }}></div>
        </div>
      </div>

      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.id} className="flex items-start p-2 border-b">
            <div className="mr-3">
              {item.status === 'pass' && <span className="text-green-500 text-xl">✓</span>}
              {item.status === 'fail' && <span className="text-red-500 text-xl">✗</span>}
              {item.status === 'pending' && <span className="text-gray-400 text-xl">⧗</span>}
            </div>
            <div className="flex-1">
              <p className="font-medium">{item.name}</p>
              {item.issues && (
                <ul className="text-sm text-red-600 mt-1">
                  {item.issues.map((issue, i) => (
                    <li key={i}>• {issue}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**TaskProgressTracker Component**:

```tsx
export function TaskProgressTracker({ taskId }: { taskId: string }) {
  const { data: taskStatus, isLoading } = useViolationStatus(taskId);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="font-bold mb-4">Analysis Progress</h3>

      <div className="mb-4">
        <div className="flex justify-between mb-2">
          <span>Overall Progress</span>
          <span className="font-bold">{taskStatus.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-500 h-3 rounded-full transition-all"
            style={{ width: `${taskStatus.progress}%` }}
          ></div>
        </div>
      </div>

      <div className="space-y-2">
        {taskStatus.steps.map((step, i) => (
          <div key={i} className="flex items-center p-2 bg-gray-50 rounded">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center mr-3"
              style={{
                backgroundColor: step.completed ? '#10b981' : '#e5e7eb',
                color: step.completed ? 'white' : 'black',
              }}
            >
              {step.completed ? '✓' : i + 1}
            </div>
            <div className="flex-1">
              <p className="font-medium">{step.name}</p>
              <p className="text-sm text-gray-500">{step.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 13.5 Styling & Design System

**Tailwind Configuration**:

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'violation-critical': '#dc2626',
        'violation-severe': '#ea580c',
        'violation-moderate': '#eab308',
        'violation-minor': '#3b82f6',
        'forensic-authentic': '#10b981',
        'forensic-questionable': '#f59e0b',
        'forensic-edited': '#ef4444',
      },
    },
  },
};
```

**Dark Mode Support**:

```tsx
// src/context/ThemeContext.tsx
export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(false);

  return <div className={isDark ? 'dark' : ''}>{children}</div>;
}
```

### Success Criteria

- ✓ All major pages implemented
- ✓ Real-time progress tracking works
- ✓ Responsive on mobile/tablet
- ✓ 90+ Lighthouse score
- ✓ Sub-200ms API responses
- ✓ Accessible (WCAG 2.1 AA)

### Deployment

- GitHub Pages for static assets
- API proxying to Backend
- Client-side caching with React Query
- Service Worker for offline support

---

## Combined Timeline

```
TOTAL PROJECT DURATION: 12-16 weeks

Phase 9: Testing Suite              Weeks 1-3   (Feb 9 - Feb 26)
Phase 10: FastAPI Migration         Weeks 4-7   (Feb 26 - Mar 26)
Phase 11: Vector DB Integration     Weeks 8-10  (Mar 26 - Apr 16)
Phase 12: K8s Deployment            Weeks 11-13 (Apr 16 - May 7)
Phase 13: Client UI Implementation  Weeks 14-17 (May 7 - Jun 4)

Total: ~4 months from start to production-ready system
```

---

## Success Metrics

### Phase 9: Testing

- [ ] 90%+ code coverage achieved
- [ ] 1,000+ tests passing
- [ ] 0 critical issues
- [ ] All compliance tests passing

### Phase 10: FastAPI

- [ ] All 6 endpoints functional
- [ ] 50%+ latency improvement
- [ ] Support 100+ concurrent requests
- [ ] Zero downtime during migration

### Phase 11: Vector DB

- [ ] All legal sources embedded
- [ ] <100ms search latency
- [ ] 95%+ precision in matching
- [ ] RAG improving analysis confidence to 95%+

### Phase 12: Kubernetes

- [ ] Services running in cluster
- [ ] Auto-scaling working
- [ ] Health checks passing
- [ ] Deployments zero-downtime
- [ ] Metrics collected and alerting active

### Phase 13: Client UI

- [ ] All major pages built
- [ ] Real-time updates working
- [ ] Mobile responsive
- [ ] 90+ Lighthouse score
- [ ] Accessible per WCAG 2.1 AA

---

## Resource Requirements

### Team (12-15 people)

**Backend Development (4-5)**

- 2 Python engineers
- 1 FastAPI specialist
- 1 Database/performance engineer
- 1 ML engineer

**DevOps/Infrastructure (2-3)**

- 2 Kubernetes specialists
- 1 Security/compliance officer

**Frontend Development (2-3)**

- 2 React engineers
- 1 UX/design engineer

**QA/Testing (2-3)**

- 2 QA engineers
- 1 Test automation specialist

**Product/Project Manager (1-2)**

- 1 Product manager
- 1 Scrum master/project coordinator

### Infrastructure

**Development**

- Developer laptops (Mac/Linux/Windows)
- GitHub repository
- Local Kubernetes cluster (Docker Desktop/Minikube)

**Staging**

- K8s cluster (3-5 nodes)
- PostgreSQL 15+
- Redis 7
- Pinecone/Weaviate
- Monitoring stack

**Production**

- K8s cluster (10-20 nodes, auto-scaling)
- PostgreSQL 15 replicated
- Redis cluster
- Pinecone (managed)
- Full monitoring/alerting

### Budget Estimate

**Personnel**: $300k - $600k (depending on geography)
**Infrastructure**: $50k - $100k (annually)
**Tools/Services**: $10k - $20k (annually)

**Total**: $360k - $720k for full implementation

---

## Risks & Mitigation

### Technical Risks

**Risk**: AI/ML model inference bottleneck
**Mitigation**: Use GPU acceleration, async queue, model caching

**Risk**: Vector DB scale issues
**Mitigation**: Start with Pinecone (managed), design for Milvus migration

**Risk**: Database performance degradation
**Mitigation**: Implement connection pooling, query optimization, read replicas

**Risk**: Kubernetes operational overhead
**Mitigation**: Use AKS/EKS managed services, hire K8s specialist

### Project Risks

**Risk**: Scope creep
**Mitigation**: Strict phase gates, only critical features in scope

**Risk**: Resource shortage
**Mitigation**: Hire early, build knowledge base, document thoroughly

**Risk**: Integration issues
**Mitigation**: Daily integration testing, staged rollouts

**Risk**: Performance regression  
**Mitigation**: Continuous benchmarking, automated performance tests

---

## Conclusion

This 5-phase roadmap provides a clear path from current enterprise upgrade to production-grade deployment. Each phase builds on the previous, with clear dependencies and measurable success criteria.

**Key Principles**:

1. **Foundation First**: Test before deploying, test before scaling
2. **Performance**: Measure and optimize at each step
3. **Compliance**: Every component validates legal standards
4. **Scalability**: Design for 10x growth
5. **User Experience**: Intuitive UI for legal professionals

**Next Action**: Begin Phase 9 (Testing Suite) immediately with dedicated QA team.
