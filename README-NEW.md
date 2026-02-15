# Public Records Analysis Platform - UI Prototype

An audit-grade, browser-based demonstration showcasing advanced document analysis workflows with evidence-backed outputs, quality controls, and investigative rigor.

## 🎯 Overview

This platform demonstrates comprehensive capabilities for processing and analyzing public records at scale, with a focus on:
- **Truthfulness**: Quality scoring, duplicate detection, and temporal uncertainty modeling
- **Provenance**: Complete chain-of-custody tracking with immutable audit trails
- **Usability**: Review queues, annotation workflows, and team-scale operations
- **Non-accusatory outputs**: Neutral relationship explainers with mandatory evidence citations

## ✨ Key Features

### Core Analysis Pipeline
- **Source Management**: Configure ingestion sources with crawl rules and rate limits
- **Document Processing**: Text extraction with OCR fallback, chunking, and indexing
- **Entity Extraction**: People, organizations, locations, dates with confidence scoring
- **Relationship Graphs**: Evidence-backed connections with explainable edges
- **Search**: Keyword and semantic search with provenance tracking

### High-Value Additions (Latest)

**Quality & Integrity**
- **OCR/Text Quality Scoring**: Per-page and per-document metrics with reprocess recommendations
- **Near-Duplicate Detection**: Hash-based and similarity-based deduplication with canonical records
- **Multilingual Detection**: Language detection per chunk with translation workflow support
- **Temporal Uncertainty**: Date normalization with confidence levels (certain, year-only, approximate, range, unknown)

**Team Operations**
- **Review Queues**: Organized workflows for low OCR quality, ambiguous entities, relationship proposals, sensitive content, translations, and exports
- **Annotations System**: Evidence Quotes (mandatory citations), Interpretations, Hypotheses, and To-Verify items
- **Assignment & Tasking**: Due dates, priorities, and reviewer sign-offs

**Analysis Transparency**
- **Relationship Explainers**: Neutral explanations with highlighted evidence snippets for every graph edge
- **Structured Extraction**: Table and form detection with field-level coordinate anchoring
- **Compliance Tracking**: Built-in audit logs, rate limit compliance, and provenance preservation

### Analysis Scripts (Modular Automation)
- Pattern Scanner: Keyword/phrase dictionaries with false-positive controls
- Entity Alias Detector: Fuzzy matching with reviewer-approved merges
- Timeline Builder: Date extraction and normalization with uncertainty handling
- Similarity Linker: Document similarity with explainable concept matching
- Relationship Engine: Evidence-backed edge generation with neutral language
- Quality Scorer: Multi-metric quality assessment with review flagging
- Deduplicator: Exact and near-duplicate detection with provenance preservation

## 🔐 Safety & Ethics

- **Non-Accusatory Language**: All outputs use neutral terms like "mentioned in" and "co-occurs with"
- **Evidence Requirements**: Relationship edges and Evidence Quote annotations require source citations
- **Probabilistic Warnings**: Clear disclaimers that all analysis must be verified against source documents
- **Privacy Controls**: Sensitive content flagging, redaction workflows, and role-gated access
- **Audit Trails**: Complete logging of all entity/relationship edits with who/when/why

## 🚀 Technology Stack

- React + TypeScript with Vite
- Tailwind CSS v4 with custom dark theme
- shadcn/ui component library (v4)
- Phosphor Icons for visual consistency
- Browser-based persistence via Spark KV
- Sample data demonstrating 3M+ document-scale concepts

## 🧠 Architecture

This is a **UI prototype** demonstrating patterns for a full-stack implementation. A production deployment would require:
- Backend ingestion pipeline (Python/Node)
- OCR engine (Tesseract or cloud service)
- Vector database (PostgreSQL + pgvector)
- Document storage (S3 or equivalent)
- Job queue system (Celery/Bull)
- Authentication & RBAC enforcement

## 📊 Data Model Highlights

- **Source**: Crawl configuration with rate limits and allowed domains
- **IngestionRun**: Discovery and download tracking with throttling
- **Document**: SHA-256 hashes, page counts, OCR flags, quality metrics
- **Entity**: Canonical names, aliases, confidence, disambiguation status
- **Relationship**: Evidence-backed edges with reviewer approval workflow
- **QualityMetrics**: Text density, OCR confidence, error rates, layout quality
- **Annotation**: Evidence quotes, interpretations, hypotheses with mandatory citations
- **ReviewQueueItem**: Tasks with assignments, priorities, and due dates
- **RelationshipExplainer**: Neutral explanations with evidence snippets for graph edges

## 🎨 Design Philosophy

- **Dark-first aesthetic**: Deep navy with amber accents for forensic precision
- **Typography**: Space Grotesk (headings), IBM Plex Sans (body), JetBrains Mono (code/hashes)
- **Evidence-first UX**: Provenance panels, confidence bars, citation links throughout
- **Accessibility**: WCAG AA contrast ratios, keyboard navigation, clear status indicators

## 📄 License

The Spark Template files and resources from GitHub are licensed under the terms of the MIT license, Copyright GitHub, Inc.
