"""
Court-Grade Discovery Validation Models
FRCP compliance checking, pre-submission validation, and court-admissible 
discovery package preparation
"""

from datetime import datetime
from enum import Enum
from auth.models import db, User


class ComplianceCheckType(Enum):
    """Types of discovery compliance checks"""
    FRCP_COMPLETENESS = "frcp_completeness"
    METADATA_PRESERVATION = "metadata_preservation"
    PRIVILEGE_PROTECTION = "privilege_protection"
    CONFIDENTIALITY_MARKINGS = "confidentiality_markings"
    BATES_NUMBERING = "bates_numbering"
    LOAD_FILE_FORMAT = "load_file_format"
    NATIVE_FORMAT = "native_format"
    REDACTION_COMPLIANCE = "redaction_compliance"
    CHAIN_OF_CUSTODY = "chain_of_custody"


class ComplianceStatus(Enum):
    """Status of compliance check"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ISSUES_FOUND = "issues_found"
    PASSED = "passed"
    FAILED = "failed"


class QASamplingStrategy(Enum):
    """Statistical quality assurance sampling approaches"""
    RANDOM = "random"
    STRATIFIED = "stratified"
    SYSTEMATIC = "systematic"
    RISK_BASED = "risk_based"
    HIGH_VALUE = "high_value"


class CourtGradeDiscoveryPackage(db.Model):
    """
    Complete court-ready discovery production package
    Ensures FRCP compliance and court admissibility
    """
    __tablename__ = 'court_grade_discovery_package'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False, index=True)
    production_set_id = db.Column(db.Integer, db.ForeignKey('production_set.id'), nullable=False, unique=True)
    
    # Package Details
    package_name = db.Column(db.String(300), nullable=False)
    responding_party = db.Column(db.String(200), nullable=False)
    requesting_party = db.Column(db.String(200), nullable=False)
    
    # Scope
    document_count = db.Column(db.Integer)  # Total documents in production
    page_count = db.Column(db.Integer)  # Total pages
    file_count = db.Column(db.Integer)  # Total native files
    
    # Temporal Scope
    date_range_start = db.Column(db.DateTime)
    date_range_end = db.Column(db.DateTime)
    date_sent = db.Column(db.DateTime)
    
    # FRCP Compliance Declaration
    frcp_complaint = db.Column(db.Boolean, default=False)  # Complies with FRCP
    frcp_version = db.Column(db.String(50))  # FRCP as of which year
    
    # Rule 26 Compliance
    rule_26_reasonable_scope = db.Column(db.Boolean)  # Reasonable scope
    rule_26_proportionality = db.Column(db.Boolean)  # Proportionality analysis done
    rule_26_privilege_log = db.Column(db.Boolean)  # Privilege log provided
    rule_26_withheld_items = db.Column(db.Integer)  # Count of withheld items
    
    # ESI Specifications
    esi_protocol_compliant = db.Column(db.Boolean)  # Follows agreed ESI protocol
    esi_protocol_id = db.Column(db.Integer, db.ForeignKey('esi_protocol.id'))
    
    # Metadata Specifications
    metadata_produced = db.Column(db.Boolean, default=True)
    metadata_fields = db.Column(db.Text)  # JSON: list of produced fields
    metadata_standard = db.Column(db.String(100))  # EDRM XML, CSV, native, etc.
    metadata_integrity_verified = db.Column(db.Boolean)  # Hash verification done
    
    # Load File Information
    load_file_format = db.Column(db.String(50), nullable=False)  # LFLEX, OPT, Relativity
    load_file_count = db.Column(db.Integer)  # Number of load files
    load_files_tested = db.Column(db.Boolean, default=False)  # Load tested
    
    # Bates Numbering
    bates_numbering_used = db.Column(db.Boolean, default=True)
    bates_prefix = db.Column(db.String(50))  # e.g., "ACME_0001"
    bates_start = db.Column(db.Integer)
    bates_end = db.Column(db.Integer)
    bates_sequential = db.Column(db.Boolean)  # No gaps
    
    # Format Information
    native_format_produced = db.Column(db.Boolean, default=True)
    native_format_list = db.Column(db.Text)  # JSON: formats produced
    pdf_produced = db.Column(db.Boolean, default=True)
    tiff_produced = db.Column(db.Boolean, default=False)
    
    # Redactions
    redactions_made = db.Column(db.Boolean, default=False)
    redaction_count = db.Column(db.Integer, default=0)
    redaction_log = db.Column(db.Text)  # JSON reference
    
    # Privilege Log
    privilege_log_provided = db.Column(db.Boolean, default=False)
    privilege_log_entries = db.Column(db.Integer, default=0)
    privilege_log_complete = db.Column(db.Boolean, default=False)
    
    # Objections
    objections_stated = db.Column(db.Text)  # JSON: list of objections
    objections_overruled = db.Column(db.Integer, default=0)
    
    # Certifications
    verified_complete = db.Column(db.Boolean, default=False)
    verified_accurate = db.Column(db.Boolean, default=False)
    verified_responsive = db.Column(db.Boolean, default=False)
    
    # Expert Certification
    producing_attorney_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    producing_attorney_name = db.Column(db.String(200))
    producing_attorney_firm = db.Column(db.String(200))
    producing_attorney_bar_number = db.Column(db.String(50))
    
    certification_date = db.Column(db.DateTime)
    certification_text = db.Column(db.Text)  # Actual certification language
    
    # Quality Assurance
    qa_completed = db.Column(db.Boolean, default=False)
    qa_date = db.Column(db.DateTime)
    qa_sample_size = db.Column(db.Integer)
    qa_results = db.Column(db.Text)  # JSON: detailed results
    
    # Submission
    submitted = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime)
    submission_method = db.Column(db.String(100))  # email, portal, mail
    submission_recipient = db.Column(db.String(200))
    
    # Storage
    delivery_media = db.Column(db.String(100))  # USB, cloud, CD, etc.
    storage_location = db.Column(db.String(300))
    access_instructions = db.Column(db.Text)  # How to access production
    
    # Notes
    production_notes = db.Column(db.Text)
    known_issues = db.Column(db.Text)  # Any known problems
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    verified_at = db.Column(db.DateTime)
    
    # Relationships
    producing_attorney = db.relationship('User', foreign_keys=[producing_attorney_id])
    
    def __repr__(self):
        return f'<CourtGradeDiscoveryPackage {self.package_name}>'


class CourSubmissionChecklist(db.Model):
    """Mandatory checklist for court submissions"""
    __tablename__ = 'court_submission_checklist'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('court_grade_discovery_package.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Document Completeness
    all_responsive_docs_included = db.Column(db.Boolean)
    privileged_docs_logged = db.Column(db.Boolean)
    withheld_items_justified = db.Column(db.Boolean)
    document_count_verified = db.Column(db.Boolean)
    
    # Metadata Compliance
    metadata_fields_complete = db.Column(db.Boolean)
    metadata_accuracy_verified = db.Column(db.Boolean)
    date_fields_populated = db.Column(db.Boolean)
    author_information_present = db.Column(db.Boolean)
    
    # Format Compliance
    native_formats_included = db.Column(db.Boolean)
    pdf_produced_correctly = db.Column(db.Boolean)
    file_formats_correct = db.Column(db.Boolean)
    encoding_standard = db.Column(db.Boolean)  # UTF-8, etc.
    
    # Numbering & Organization
    bates_numbering_sequential = db.Column(db.Boolean)
    bates_numbers_unique = db.Column(db.Boolean)
    page_numbers_match_bates = db.Column(db.Boolean)
    attachments_properly_bated = db.Column(db.Boolean)
    
    # Privilege & Confidentiality
    privilege_claims_accurate = db.Column(db.Boolean)
    confidentiality_markings_present = db.Column(db.Boolean)
    redactions_all_identified = db.Column(db.Boolean)
    redaction_log_complete = db.Column(db.Boolean)
    
    # Redaction Quality
    redactions_consistent = db.Column(db.Boolean)
    redaction_removal_impossible = db.Column(db.Boolean)  # Can't reveal what's redacted
    no_metadata_exposure = db.Column(db.Boolean)  # Metadata not revealing redactions
    
    # ESI Compliance
    esi_protocol_followed = db.Column(db.Boolean)
    file_extensions_correct = db.Column(db.Boolean)
    no_macro_viruses = db.Column(db.Boolean)
    virus_scan_completed = db.Column(db.Boolean)
    
    # Load File Validation
    load_file_format_correct = db.Column(db.Boolean)
    load_file_structure_valid = db.Column(db.Boolean)
    load_file_tested_successfully = db.Column(db.Boolean)
    load_files_can_import = db.Column(db.Boolean)
    
    # Certifications
    attorney_certification_signed = db.Column(db.Boolean)
    certification_accurate = db.Column(db.Boolean)
    certification_timely = db.Column(db.Boolean)
    
    # Legal Standards
    frcp_compliant = db.Column(db.Boolean)
    fre_compliant = db.Column(db.Boolean)  # Federal Rules of Evidence
    state_rules_compliant = db.Column(db.Boolean)
    no_discovery_abuse = db.Column(db.Boolean)
    
    # Chain of Custody
    custody_documented = db.Column(db.Boolean)
    integrity_preserved = db.Column(db.Boolean)
    no_tampering_evidence = db.Column(db.Boolean)
    
    # Delivery & Transport
    delivery_method_appropriate = db.Column(db.Boolean)
    secure_transmission = db.Column(db.Boolean)
    backup_copies_retained = db.Column(db.Boolean)
    
    # Final Quality
    no_missing_files = db.Column(db.Boolean)
    no_corrupted_files = db.Column(db.Boolean)
    searchable_if_required = db.Column(db.Boolean)
    ocr_complete_if_needed = db.Column(db.Boolean)
    
    # Advanced Checks
    no_duplicate_documents = db.Column(db.Boolean)
    deduplication_methodology = db.Column(db.String(100))  # Hash-based, fuzzy, etc.
    family_relationships_correct = db.Column(db.Boolean)  # Email chains, attachments
    
    # Checklist Status
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100
    items_passed = db.Column(db.Integer, default=0)
    items_failed = db.Column(db.Integer, default=0)
    items_waived = db.Column(db.Integer, default=0)
    
    # Verification
    all_items_verified = db.Column(db.Boolean, default=False)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_date = db.Column(db.DateTime)
    
    # Remediation
    failed_items = db.Column(db.Text)  # JSON: items that failed with remediation plan
    remediation_complete = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])
    
    def __repr__(self):
        return f'<CourSubmissionChecklist Package:{self.package_id}>'


class CourtGradeQAWorkflow(db.Model):
    """
    Mandatory 5% statistical QA sampling workflow
    Ensures statistical confidence in document accuracy
    """
    __tablename__ = 'court_grade_qa_workflow'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('court_grade_discovery_package.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Sampling Parameters
    total_document_population = db.Column(db.Integer, nullable=False)
    sampling_strategy = db.Column(db.String(50))  # QASamplingStrategy
    sample_size_planned = db.Column(db.Integer)
    sample_size_5_percent = db.Column(db.Integer)  # 5% of population
    sample_size_actual = db.Column(db.Integer)
    
    # Confidence Levels
    confidence_level = db.Column(db.Float)  # 95%, 99%, etc.
    margin_of_error = db.Column(db.Float)  # +/- percentage
    
    # Sampling Approach
    risk_stratification = db.Column(db.Text)  # JSON: risk tiers, oversample high risk
    high_risk_documents = db.Column(db.Integer)  # Emails, attachments, edited docs
    low_risk_documents = db.Column(db.Integer)  # Templates, standard forms
    
    # Sample Selection
    documents_sampled = db.Column(db.Integer)
    sampling_date = db.Column(db.DateTime)
    sampling_method = db.Column(db.String(100))  # How documents were selected
    
    # QA Testing
    qa_coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    qa_start_date = db.Column(db.DateTime)
    qa_end_date = db.Column(db.DateTime)
    
    # Checklist Items Tested (for each sampled document)
    metadata_checked = db.Column(db.Boolean, default=False)
    responsiveness_verified = db.Column(db.Boolean, default=False)
    privilege_verified = db.Column(db.Boolean, default=False)
    bates_numbering_checked = db.Column(db.Boolean, default=False)
    redaction_verified = db.Column(db.Boolean, default=False)
    native_format_verified = db.Column(db.Boolean, default=False)
    
    # Results
    documents_passed = db.Column(db.Integer, default=0)
    documents_failed = db.Column(db.Integer, default=0)
    pass_rate_percentage = db.Column(db.Float)  # (passed/total)*100
    
    # Defect Categories
    metadata_defects = db.Column(db.Integer, default=0)
    responsiveness_issues = db.Column(db.Integer, default=0)
    privilege_issues = db.Column(db.Integer, default=0)
    numbering_errors = db.Column(db.Integer, default=0)
    redaction_errors = db.Column(db.Integer, default=0)
    format_errors = db.Column(db.Integer, default=0)
    
    # Statistical Analysis
    defect_rate = db.Column(db.Float)  # (failed/total)*100
    projected_defects_in_population = db.Column(db.Integer)  # Estimated
    acceptable_defect_rate = db.Column(db.Float)  # AQL (Acceptable Quality Level)
    defect_rate_acceptable = db.Column(db.Boolean)  # Does sample meet AQL
    
    # Detailed Findings
    findings = db.Column(db.Text)  # JSON: {doc_id, issue_type, severity, remediation}
    
    # Remediation
    remediation_required = db.Column(db.Boolean, default=False)
    remediation_scope = db.Column(db.Text)  # All documents, sampled only, etc.
    remediation_items = db.Column(db.Text)  # JSON: list of fixes needed
    remediation_date = db.Column(db.DateTime)
    
    # Re-sampling
    resampling_required = db.Column(db.Boolean, default=False)
    documents_resampled = db.Column(db.Integer, default=0)
    resampling_date = db.Column(db.DateTime)
    
    # Final Determination
    qa_passed = db.Column(db.Boolean, default=False)
    ready_for_production = db.Column(db.Boolean, default=False)
    
    # Sign-Off
    qa_approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    qa_approval_date = db.Column(db.DateTime)
    qa_approval_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    qa_coordinator = db.relationship('User', foreign_keys=[qa_coordinator_id])
    qa_approved_by = db.relationship('User', foreign_keys=[qa_approved_by_id])
    
    def __repr__(self):
        return f'<CourtGradeQAWorkflow Package:{self.package_id}>'


class ComplianceCheckResult(db.Model):
    """Individual compliance check result"""
    __tablename__ = 'compliance_check_result'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('court_grade_discovery_package.id'), nullable=False)
    
    # Check Details
    check_type = db.Column(db.String(50), nullable=False)  # ComplianceCheckType
    check_name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    
    # Result
    status = db.Column(db.String(50), nullable=False)  # ComplianceStatus
    passed = db.Column(db.Boolean)
    
    # Details
    issues_found = db.Column(db.Integer, default=0)
    issue_descriptions = db.Column(db.Text)  # JSON: list of issues
    
    # Severity
    has_critical_issues = db.Column(db.Boolean, default=False)
    has_major_issues = db.Column(db.Boolean, default=False)
    has_minor_issues = db.Column(db.Boolean, default=False)
    
    # Remediation
    remediation_required = db.Column(db.Boolean, default=False)
    remediation_plan = db.Column(db.Text)
    remediation_items = db.Column(db.Text)  # JSON
    
    # Verification
    checked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    checked_date = db.Column(db.DateTime)
    
    # Evidence
    supporting_documentation = db.Column(db.Text)  # References to evidence
    test_results = db.Column(db.Text)  # JSON: technical test results
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    checked_by = db.relationship('User', foreign_keys=[checked_by_id])
    
    def __repr__(self):
        return f'<ComplianceCheckResult {self.check_type}>'


class DiscoveryProductionTimeline(db.Model):
    """Track discovery production deadlines and compliance"""
    __tablename__ = 'discovery_production_timeline'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('court_grade_discovery_package.id'))
    
    # Request Details
    request_received_date = db.Column(db.DateTime, nullable=False)
    request_description = db.Column(db.String(500))
    
    # Deadline
    response_due_date = db.Column(db.DateTime, nullable=False)
    extension_requested = db.Column(db.Boolean, default=False)
    extension_granted_until = db.Column(db.DateTime)
    
    # Milestones
    collection_start_date = db.Column(db.DateTime)
    collection_end_date = db.Column(db.DateTime)
    processing_start_date = db.Column(db.DateTime)
    processing_end_date = db.Column(db.DateTime)
    qa_start_date = db.Column(db.DateTime)
    qa_end_date = db.Column(db.DateTime)
    certification_date = db.Column(db.DateTime)
    
    # Actual Delivery
    delivered_date = db.Column(db.DateTime)
    days_before_deadline = db.Column(db.Integer)  # Negative if late
    
    # Follow-ups
    supplementation_required = db.Column(db.Boolean, default=False)
    supplementation_reason = db.Column(db.String(500))
    supplementation_due_date = db.Column(db.DateTime)
    supplementation_delivered_date = db.Column(db.DateTime)
    
    # Compliance Tracking
    timely = db.Column(db.Boolean)  # Delivered on time
    objections_raised = db.Column(db.Boolean, default=False)
    objection_details = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DiscoveryProductionTimeline Case:{self.case_id}>'
