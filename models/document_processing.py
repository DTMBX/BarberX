"""
Advanced Document Processing Models
Models for OCR, transcription processing, redaction, and content analysis
"""

from datetime import datetime
from auth.models import db, User


class DocumentProcessingTask(db.Model):
    """
    Tracks document processing jobs (OCR, transcription, analysis)
    """
    __tablename__ = 'document_processing_task'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Task Information
    task_type = db.Column(db.String(100), nullable=False)  # ocr, transcription, entity_extraction, privilege_detection, redaction
    task_uuid = db.Column(db.String(36), unique=True)
    
    # Processing Status
    status = db.Column(db.String(50), default='queued')  # queued, processing, completed, failed, paused
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    
    # Processing Details
    processing_engine = db.Column(db.String(200))  # e.g., "Tesseract 5.0", "Whisper-v2", "GPT-4"
    model_version = db.Column(db.String(100))
    parameters = db.Column(db.Text)  # JSON configuration
    
    # Results
    confidence_score = db.Column(db.Float)  # 0-1 confidence in results
    result_data = db.Column(db.LargeBinary)  # Processed content (compressed if large)
    error_message = db.Column(db.Text)
    
    # Timing
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    processing_time_seconds = db.Column(db.Integer)
    
    # Resources Used
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    
    # Batch reference (nullable — only set when task belongs to a batch)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_processing_queue.id'), nullable=True, index=True)
    
    # Metadata
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    requested_by = db.relationship('User', foreign_keys=[requested_by_id])
    completed_by = db.relationship('User', foreign_keys=[completed_by_id])
    
    def __repr__(self):
        return f'<DocumentProcessingTask {self.task_type} Evidence:{self.evidence_id}>'


class OCRResult(db.Model):
    """
    Stores OCR processing results for image-based documents
    """
    __tablename__ = 'ocr_result'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), unique=True, nullable=False)
    processing_task_id = db.Column(db.Integer, db.ForeignKey('document_processing_task.id'))
    
    # OCR Results
    extracted_text = db.Column(db.Text, nullable=False)
    confidence_per_line = db.Column(db.Text)  # JSON array of confidence scores
    average_confidence = db.Column(db.Float)
    
    # Processing Details
    total_pages = db.Column(db.Integer)
    pages_processed = db.Column(db.Integer)
    failed_pages = db.Column(db.Integer)
    
    # Language Detection
    detected_languages = db.Column(db.String(200))  # CSV or JSON
    primary_language = db.Column(db.String(10))  # ISO 639-1 code
    
    # Quality Metrics
    char_accuracy = db.Column(db.Float)
    word_accuracy = db.Column(db.Float)
    
    # Searchability
    is_searchable = db.Column(db.Boolean, default=True)
    quality_issues = db.Column(db.Text)  # JSON array of issues
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processing_task = db.relationship('DocumentProcessingTask', foreign_keys=[processing_task_id])
    
    def __repr__(self):
        return f'<OCRResult Evidence:{self.evidence_id}>'


class TranscriptionResult(db.Model):
    """
    Stores transcription results for audio/video evidence
    """
    __tablename__ = 'transcription_result'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), unique=True, nullable=False)
    processing_task_id = db.Column(db.Integer, db.ForeignKey('document_processing_task.id'))
    
    # Transcription Content
    full_transcript = db.Column(db.Text, nullable=False)
    
    # Timing & Alignment
    duration_seconds = db.Column(db.Integer)
    has_timecodes = db.Column(db.Boolean, default=True)
    timecoded_transcript = db.Column(db.Text)  # JSON with timestamps
    
    # Quality Metrics
    average_confidence = db.Column(db.Float)  # Word accuracy
    detected_speakers = db.Column(db.Integer)
    
    # Speaker Information
    speakers_identified = db.Column(db.Text)  # JSON array of speaker info
    speaker_diarization = db.Column(db.Boolean, default=False)
    
    # Language
    detected_language = db.Column(db.String(10))  # ISO 639-1
    language_accuracy = db.Column(db.Float)
    
    # Content Flags
    contains_profanity = db.Column(db.Boolean, default=False)
    contains_background_noise = db.Column(db.Boolean, default=False)
    background_noise_level = db.Column(db.String(20))  # low, medium, high
    
    # Accuracy & Corrections
    requires_review = db.Column(db.Boolean, default=False)
    review_notes = db.Column(db.Text)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Final Transcript
    corrected_transcript = db.Column(db.Text)  # QA-approved version
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processing_task = db.relationship('DocumentProcessingTask', foreign_keys=[processing_task_id])
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    
    def __repr__(self):
        return f'<TranscriptionResult Evidence:{self.evidence_id}>'


class RedactionRule(db.Model):
    """
    Defines redaction rules for automatically masking sensitive content
    """
    __tablename__ = 'redaction_rule'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Rule Definition
    rule_name = db.Column(db.String(200), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # regex, entity_type, keyword, pattern
    
    # Pattern/Rule Details
    pattern = db.Column(db.String(500), nullable=False)  # Regex or keyword pattern
    entity_type = db.Column(db.String(100))  # For NER-based redaction: PII, PHONE, SSN, Credit_Card, etc.
    
    # Application
    applies_to_document_types = db.Column(db.Text)  # JSON array or CSV (blank = all)
    applies_to_fields = db.Column(db.Text)  # JSON: which fields to apply rule to
    
    # Redaction Style
    redaction_style = db.Column(db.String(50), default='blackout')  # blackout, redact_text, partial_mask
    replacement_text = db.Column(db.String(100))  # e.g., "[REDACTED]", "***"
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=100)  # Higher = applied later
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<RedactionRule {self.rule_name}>'


class RedactionInstance(db.Model):
    """
    Records individual redactions made to documents
    """
    __tablename__ = 'redaction_instance'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    
    # Redaction Details
    redaction_rule_id = db.Column(db.Integer, db.ForeignKey('redaction_rule.id'))
    redaction_type = db.Column(db.String(50), nullable=False)  # pii, attorney_client, work_product, trade_secret, etc.
    
    # Location Information
    page_number = db.Column(db.Integer)
    line_number = db.Column(db.Integer)
    original_text = db.Column(db.String(500))  # Text that was redacted
    context_before = db.Column(db.String(200))  # Surrounding text for context
    context_after = db.Column(db.String(200))
    
    # Redaction Method
    redaction_method = db.Column(db.String(50))  # manual, automatic, ai_suggested
    confidence_score = db.Column(db.Float)  # Confidence if AI-derived
    
    # Approval
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Justification
    justification = db.Column(db.Text)  # Why this was redacted
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rule = db.relationship('RedactionRule', foreign_keys=[redaction_rule_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f'<RedactionInstance Evidence:{self.evidence_id}>'


class ComplianceReview(db.Model):
    """
    Quality assurance reviews of processed documents
    """
    __tablename__ = 'compliance_review'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Review Information
    review_type = db.Column(db.String(50), nullable=False)  # ocr_quality, transcription_accuracy, redaction, privilege, completeness
    review_date = db.Column(db.DateTime, nullable=False)
    
    # Review Results
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, needs_revision
    findings = db.Column(db.Text)  # Detailed review notes
    issues_found = db.Column(db.Integer, default=0)
    
    # Quality Scores
    accuracy_score = db.Column(db.Float)  # 0-100
    completeness_score = db.Column(db.Float)  # 0-100
    compliance_score = db.Column(db.Float)  # 0-100
    
    # Specific Issues
    has_ocr_errors = db.Column(db.Boolean, default=False)
    has_transcription_errors = db.Column(db.Boolean, default=False)
    has_missed_redactions = db.Column(db.Boolean, default=False)
    has_privilege_issues = db.Column(db.Boolean, default=False)
    
    # Reviewer Information
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Required Actions
    requires_reprocessing = db.Column(db.Boolean, default=False)
    reprocessing_reason = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    
    def __repr__(self):
        return f'<ComplianceReview {self.review_type} Evidence:{self.evidence_id}>'


class ContentExtractionIndex(db.Model):
    """
    Full-text search index and content extraction summary
    """
    __tablename__ = 'content_extraction_index'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), unique=True, nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Content Summary
    content_type = db.Column(db.String(50), nullable=False)  # text, ocr, transcript, extracted
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    line_count = db.Column(db.Integer)
    
    # Content Storage (for indexing)
    full_text = db.Column(db.Text)  # Full extracted text for FTS
    summary = db.Column(db.Text)  # Auto-generated summary
    
    # Entity Information (NER Results)
    entities_json = db.Column(db.Text)  # JSON with detected entities
    persons = db.Column(db.Text)  # CSV of person names
    organizations = db.Column(db.Text)  # CSV of org names
    locations = db.Column(db.Text)  # CSV of location names
    email_addresses = db.Column(db.Text)  # CSV
    phone_numbers = db.Column(db.Text)  # CSV
    
    # Key Content Indicators
    key_phrases = db.Column(db.Text)  # JSON array
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    is_sensitive = db.Column(db.Boolean, default=False)
    
    # Processing Status
    is_indexed = db.Column(db.Boolean, default=False)
    last_indexed = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContentExtractionIndex Evidence:{self.evidence_id}>'


class BatchProcessingQueue(db.Model):
    """
    Manages batch processing of multiple documents
    """
    __tablename__ = 'batch_processing_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Batch Information
    batch_name = db.Column(db.String(300), nullable=False)
    batch_uuid = db.Column(db.String(36), unique=True)
    
    # Document Selection
    document_count = db.Column(db.Integer, default=0)
    processing_type = db.Column(db.String(100), nullable=False)  # ocr_all, transcribe_all, analyze_all, etc.
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, paused, failed
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Results
    successful_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    # Timing
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    
    # Cost Estimation
    estimated_total_cost = db.Column(db.Float)
    actual_total_cost = db.Column(db.Float)
    
    # Configuration
    processing_parameters = db.Column(db.Text)  # JSON with batch parameters
    priority = db.Column(db.String(20), default='normal')
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    tasks = db.relationship('DocumentProcessingTask', backref='batch_queue')
    
    def __repr__(self):
        return f'<BatchProcessingQueue {self.batch_name}>'
