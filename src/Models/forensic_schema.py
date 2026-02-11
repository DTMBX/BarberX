"""
EVIDENT FORENSIC-GRADE DATABASE SCHEMA
======================================

Schemas for:
1. Discovery Document Classifier (metadata + model versions)
2. Chain-of-Custody Audit Logger (immutable event stream)
3. Privilege Detection Refiner (training data, predictions)
4. Evidence Timeline Builder (extracted events, relationships)
5. Batch Discovery Processor (job tracking, progress)
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, 
    Boolean, ForeignKey, JSON, Index, UniqueConstraint, 
    Enum as SQLEnum, LargeBinary
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

Base = declarative_base()


# ============================================================================
# 1. DISCOVERY DOCUMENT CLASSIFIER
# ============================================================================

class DocumentClassifierModel(Base):
    """Store classifier models and versions for A/B testing"""
    __tablename__ = "classifier_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True)
    model_name = Column(String(255), nullable=False)  # e.g., "bert-legal-v2"
    model_version = Column(String(50), nullable=False)  # e.g., "2.1.0"
    model_type = Column(String(50), nullable=False)  # "transformer", "xgboost", "ensemble"
    model_file_path = Column(String(512), nullable=False)  # S3 path or local path
    model_hash = Column(String(128), nullable=False)  # SHA-256 of model binary
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    
    # Training config
    training_config = Column(JSONB)  # {"epochs": 5, "batch_size": 32, "lr": 0.0001}
    training_date = Column(DateTime, default=datetime.utcnow)
    
    # Status & deployment
    status = Column(String(50))  # "active", "archived", "testing"
    is_production = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('case_id', 'model_name', 'model_version', name='uq_classifier_version'),
        Index('idx_classifier_active', 'case_id', 'is_production'),
    )


class DocumentClassification(Base):
    """Store classification results for each document"""
    __tablename__ = "document_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(String(255), ForeignKey('evidence.id'), index=True, nullable=False)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True, nullable=False)
    classifier_model_id = Column(UUID(as_uuid=True), ForeignKey('classifier_models.id'))
    
    # Classification result
    classification = Column(String(50), nullable=False)  # "responsive", "irrelevant", "privileged", "uncertain"
    confidence_score = Column(Float, nullable=False)  # 0.0-1.0
    
    # Explanation for audit
    explanation = Column(Text)  # Why was it classified this way?
    shap_values = Column(JSONB)  # Feature importance from SHAP for interpretability
    
    # Batch processing reference
    batch_job_id = Column(UUID(as_uuid=True), ForeignKey('batch_jobs.id'), index=True)
    
    classified_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_doc_class_case_ev', 'case_id', 'evidence_id'),
        Index('idx_doc_class_confidence', 'case_id', 'confidence_score'),
    )


# ============================================================================
# 2. CHAIN-OF-CUSTODY AUDIT LOGGER
# ============================================================================

class AuditEventType(enum.Enum):
    """Define all audit event types"""
    EVIDENCE_UPLOADED = "evidence.uploaded"
    EVIDENCE_VIEWED = "evidence.viewed"
    EVIDENCE_DOWNLOADED = "evidence.downloaded"
    EVIDENCE_CLASSIFIED = "evidence.classified"
    EVIDENCE_ANALYZED = "evidence.analyzed"
    EVIDENCE_REDACTED = "evidence.redacted"
    EVIDENCE_SHARED = "evidence.shared"
    EVIDENCE_DELETED = "evidence.deleted"
    PRIVILEGE_ASSERTED = "privilege.asserted"
    PRIVILEGE_WAIVED = "privilege.waived"
    CHAIN_OF_CUSTODY_BREAK = "chain_of_custody.break"


class ChainOfCustodyAuditLog(Base):
    """Immutable audit log for all evidence interactions"""
    __tablename__ = "chain_of_custody_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event metadata
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True, nullable=False)
    evidence_id = Column(String(255), ForeignKey('evidence.id'), index=True, nullable=False)
    
    # Actor information
    user_id = Column(String(255), ForeignKey('users.id'), index=True, nullable=False)
    user_name = Column(String(255), nullable=False)  # Cached for audit trail
    user_email = Column(String(255), nullable=False)  # Cached for audit trail
    user_role = Column(String(50), nullable=False)  # "attorney", "paralegal", "admin"
    
    # Timestamp with precision
    event_timestamp = Column(DateTime, default=datetime.utcnow, 
                            nullable=False, index=True)  # UTC-normalized
    received_timestamp = Column(DateTime, default=datetime.utcnow)  # When logged to DB
    
    # Cryptographic proof
    event_hash = Column(String(128), nullable=False, unique=True)  # SHA-256 of event
    previous_hash = Column(String(128), nullable=True)  # Hash of previous event (chain)
    
    # Event details
    description = Column(Text, nullable=False)
    metadata = Column(JSONB)  # {"ip_address": "...", "user_agent": "...", "action_result": "success"}
    
    # Verification fields
    signature = Column(LargeBinary, nullable=True)  # RSA signature for non-repudiation
    verified = Column(Boolean, default=False)
    verification_timestamp = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_coc_case_time', 'case_id', 'event_timestamp'),
        Index('idx_coc_evidence_time', 'evidence_id', 'event_timestamp'),
        Index('idx_coc_user_time', 'user_id', 'event_timestamp'),
        Index('idx_coc_event_type', 'event_type', 'event_timestamp'),
        Index('idx_coc_chain', 'previous_hash'),  # For chain validation
    )


# ============================================================================
# 3. PRIVILEGE DETECTION REFINER
# ============================================================================

class PrivilegeDetectionModel(Base):
    """Track privilege detection model versions and performance"""
    __tablename__ = "privilege_detection_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_file_path = Column(String(512), nullable=False)
    model_hash = Column(String(128), nullable=False)  # SHA-256
    
    # Performance
    precision = Column(Float)  # Minimize false-positive privilege assertions
    recall = Column(Float)     # Catch all truly privileged docs
    f1_score = Column(Float)
    confusion_matrix = Column(JSONB)  # [[TP, FP], [FN, TN]]
    
    training_date = Column(DateTime, default=datetime.utcnow)
    training_data_size = Column(Integer)  # How many labeled examples?
    is_production = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PrivilegeDetection(Base):
    """Results of privilege detection on documents"""
    __tablename__ = "privilege_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(String(255), ForeignKey('evidence.id'), index=True, nullable=False)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True, nullable=False)
    privilege_model_id = Column(UUID(as_uuid=True), ForeignKey('privilege_detection_models.id'))
    
    # Classification
    is_privileged = Column(Boolean, nullable=False)
    privilege_type = Column(String(50))  # "attorney-client", "attorney-work-product", "none"
    confidence_score = Column(Float)  # 0.0-1.0
    
    # Evidence for audit
    document_excerpt = Column(Text)  # Key passage that triggered privilege detection
    keywords_found = Column(JSONB)  # ["attorney", "confidential", "legal advice"]
    tone_analysis = Column(JSONB)   # {"formality": 0.8, "legal_terminology": 0.9}
    
    # Manual review
    reviewed_by = Column(String(255), ForeignKey('users.id'))
    review_status = Column(String(50))  # "pending", "approved", "disputed"
    review_notes = Column(Text)
    reviewed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# 4. EVIDENCE TIMELINE BUILDER
# ============================================================================

class TimelineEvent(Base):
    """Extracted events from evidence (dates, actions, references)"""
    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True, nullable=False)
    
    # Event data
    event_date = Column(DateTime, index=True, nullable=False)  # Normalized to UTC
    event_date_precision = Column(String(50))  # "exact", "approximate", "year_only"
    event_title = Column(String(255), nullable=False)
    event_description = Column(Text)
    
    # Source evidence
    evidence_id = Column(String(255), ForeignKey('evidence.id'), index=True)
    source_type = Column(String(50))  # "email", "document", "video", "audio", "manual"
    
    # Entities involved
    entities = Column(JSONB)  # {"people": [...], "locations": [...], "organizations": [...]}
    
    # Relationships to other events
    related_events = Column(JSONB)  # [{"event_id": "...", "relationship": "precedes"}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_timeline_case_date', 'case_id', 'event_date'),
    )


class CaseTimeline(Base):
    """Aggregate timeline for a case"""
    __tablename__ = "case_timelines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), ForeignKey('cases.id'), unique=True, nullable=False)
    
    # Timeline stats
    event_count = Column(Integer, default=0)
    earliest_event = Column(DateTime)
    latest_event = Column(DateTime)
    timeline_span_days = Column(Integer)
    
    # Visualization data
    timeline_json = Column(JSONB)  # Pre-computed timeline for UI rendering
    conflicts = Column(JSONB)  # Date inconsistencies found: [{"evidence_a": "...", "evidence_b": ...}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# 5. BATCH DISCOVERY PROCESSOR
# ============================================================================

class BatchJobStatus(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class BatchJob(Base):
    """Track batch processing jobs"""
    __tablename__ = "batch_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True, nullable=False)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=False)
    
    # Job definition
    job_name = Column(String(255), nullable=False)
    job_type = Column(String(50), nullable=False)  # "classify", "extract_timeline", "privilege_check"
    
    # Processing scope
    evidence_ids = Column(JSONB)  # ["ev_001", "ev_002", ...]
    processing_params = Column(JSONB)  # Job-specific config
    
    # Status tracking
    status = Column(SQLEnum(BatchJobStatus), default=BatchJobStatus.QUEUED, index=True)
    progress_percent = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    total_count = Column(Integer, nullable=False)
    
    # Timing
    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Error tracking
    error_message = Column(Text)
    error_count = Column(Integer, default=0)
    failed_evidence_ids = Column(JSONB)  # ["ev_005", ...]
    
    # Results reference
    results_summary = Column(JSONB)  # {"classifications": {responsive: 45, irrelevant: 23}, ...}
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_batch_case_status', 'case_id', 'status'),
        Index('idx_batch_user_time', 'user_id', 'created_at'),
    )


class BatchJobTask(Base):
    """Individual tasks within a batch job"""
    __tablename__ = "batch_job_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_job_id = Column(UUID(as_uuid=True), ForeignKey('batch_jobs.id'), index=True, nullable=False)
    evidence_id = Column(String(255), ForeignKey('evidence.id'), index=True, nullable=False)
    
    # Task status
    status = Column(SQLEnum(BatchJobStatus), default=BatchJobStatus.QUEUED)
    result = Column(JSONB)  # Job-specific result (classification, timeline events, etc.)
    error = Column(Text)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# BASELINE SCHEMA (Existing Evidence & Cases)
# ============================================================================
# These are placeholders — adapt to your existing schema

class Case(Base):
    """Cases (assuming you have this)"""
    __tablename__ = "cases"

    id = Column(String(255), primary_key=True)
    # ... your existing case fields


class Evidence(Base):
    """Evidence items"""
    __tablename__ = "evidence"

    id = Column(String(255), primary_key=True)
    case_id = Column(String(255), ForeignKey('cases.id'), index=True)
    # ... your existing evidence fields


class User(Base):
    """Users"""
    __tablename__ = "user"

    id = Column(String(255), primary_key=True)
    # ... your existing user fields
