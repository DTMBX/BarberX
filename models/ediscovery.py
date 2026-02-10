"""
E-Discovery Legal Models
Comprehensive models for managing document discovery, production, and litigation compliance
"""

from datetime import datetime
from auth.models import db, User


class DiscoveryRequest(db.Model):
    """
    Represents a discovery request from opposing counsel
    Tracks all requested materials and response status
    """
    __tablename__ = 'discovery_request'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Request Information
    request_number = db.Column(db.String(50), nullable=False)  # e.g., "RFC 1", "INTERROGATORY 1"
    request_type = db.Column(db.String(50), nullable=False)  # interrogatory, request_for_production, request_for_admission, deposition_notice
    request_text = db.Column(db.Text, nullable=False)  # Full text of the discovery request
    
    requesting_party = db.Column(db.String(300), nullable=False)
    receiving_party = db.Column(db.String(300), nullable=False)
    
    # Timeline
    received_date = db.Column(db.DateTime, nullable=False)
    response_due_date = db.Column(db.DateTime, nullable=False)
    extended_due_date = db.Column(db.DateTime)  # If extension granted
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, responded, objected, partially_responded, withdrawn
    response_submitted_date = db.Column(db.DateTime)
    
    # Responses & Objections
    response_text = db.Column(db.Text)
    objection_basis = db.Column(db.String(500))  # e.g., "overbroad", "burdensome", "privileged"
    partial_response_notes = db.Column(db.Text)
    
    # Metadata
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    responsive_items = db.relationship('ResponsiveDocument', backref='discovery_request', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DiscoveryRequest {self.request_number}>'


class ResponsiveDocument(db.Model):
    """
    Links evidence items to discovery requests
    Tracks which documents are responsive to which requests
    """
    __tablename__ = 'responsive_document'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    discovery_request_id = db.Column(db.Integer, db.ForeignKey('discovery_request.id'), nullable=False)
    
    # Designation
    is_responsive = db.Column(db.Boolean, default=True)
    reason_if_nonresponsive = db.Column(db.String(300))  # e.g., "not in possession", "privilege"
    
    # Production Status
    is_produced = db.Column(db.Boolean, default=False)
    production_version = db.Column(db.String(50))  # e.g., "Production 1", "Supplemental"
    
    # Bates Numbering
    bates_start = db.Column(db.String(20))
    bates_end = db.Column(db.String(20))
    
    # Redactions
    has_redactions = db.Column(db.Boolean, default=False)
    redaction_reason = db.Column(db.String(200))  # e.g., "attorney-client privilege", "work product"
    redacted_version_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'))
    
    # Metadata
    document_description = db.Column(db.Text)
    relevance_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    redacted_version = db.relationship('EvidenceItem', foreign_keys=[redacted_version_id])
    
    def __repr__(self):
        return f'<ResponsiveDocument Evidence:{self.evidence_id} Request:{self.discovery_request_id}>'


class ProductionSet(db.Model):
    """
    Represents a production of documents to opposing counsel
    Groups documents produced together in response to discovery
    """
    __tablename__ = 'ediscovery_production_set'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Identification
    production_number = db.Column(db.String(50), nullable=False)  # e.g., "Production 1"
    production_uuid = db.Column(db.String(36), unique=True)  # For external systems
    
    # Timeline
    production_date = db.Column(db.DateTime, nullable=False)
    produced_to_party = db.Column(db.String(300), nullable=False)
    
    # Production Details
    description = db.Column(db.Text)
    total_documents = db.Column(db.Integer, default=0)
    total_pages = db.Column(db.Integer, default=0)
    total_size_gb = db.Column(db.Float, default=0)
    
    # Format & Delivery
    delivery_format = db.Column(db.String(50))  # native, pdf, tiff, zip, etc.
    delivery_method = db.Column(db.String(50))  # email, usb, portal, ftp, etc.
    delivered_date = db.Column(db.DateTime)
    
    # Designations
    has_designations = db.Column(db.Boolean, default=False)  # Contains confidential/AEO materials
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, produced, supplemental, modified
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    production_items = db.relationship('ProductionItem', backref='production_set', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProductionSet {self.production_number}>'


class ProductionItem(db.Model):
    """
    Individual item in a production set
    Links evidence to specific productions with Bates numbering
    """
    __tablename__ = 'ediscovery_production_item'
    
    id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('ediscovery_production_set.id'), nullable=False, index=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    
    # Bates Numbering
    bates_number_start = db.Column(db.String(20), nullable=False)
    bates_number_end = db.Column(db.String(20))  # Multi-page documents
    
    # Numbering Scheme
    numbering_scheme = db.Column(db.String(50), default='sequential')  # sequential, by_request, by_custodian
    
    # Metadata
    sequence_number = db.Column(db.Integer)  # Order in production
    page_count = db.Column(db.Integer)
    file_size_bytes = db.Column(db.Integer)
    
    # Designation/Marking
    designation = db.Column(db.String(100))  # e.g., "CONFIDENTIAL - AEO"
    needs_designation = db.Column(db.Boolean, default=False)
    
    # Production Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    evidence = db.relationship('EvidenceItem', foreign_keys=[evidence_id])
    
    def __repr__(self):
        return f'<ProductionItem {self.bates_number_start}>'


class PrivilegeLog(db.Model):
    """
    Maintains privilege log for withheld documents
    Required by discovery rules when claiming privilege
    """
    __tablename__ = 'ediscovery_privilege_log'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    
    # Document Information (withheld)
    document_date = db.Column(db.DateTime)
    document_title = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))  # email, memo, report, etc.
    
    # Privilege Claim
    privilege_claimed = db.Column(db.String(100), nullable=False)  # attorney_client, work_product, spousal, doctor_patient, etc.
    privilege_description = db.Column(db.Text, nullable=False)
    
    # Parties Involved
    from_party = db.Column(db.String(300), nullable=False)
    to_party = db.Column(db.String(300), nullable=False)
    cc_parties = db.Column(db.Text)  # CSV of CC'd parties
    
    # Content Description (for log)
    general_subject = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)  # General description without revealing privileged content
    
    # Privilege Details
    attorney_involved = db.Column(db.String(300))  # Named attorney
    seeks_legal_advice = db.Column(db.Boolean, default=True)
    attorney_prepared = db.Column(db.Boolean, default=False)  # For work product doctrine
    
    # Withholding Justification
    withholding_reason = db.Column(db.Text)  # Explanation of privilege
    
    # Status
    status = db.Column(db.String(50), default='withheld')  # withheld, produced, supplemental
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<PrivilegeLog {self.document_title}>'


class DocumentMetadata(db.Model):
    """
    Stores extracted metadata from documents
    Supports advanced search and filtering
    """
    __tablename__ = 'document_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), unique=True, nullable=False)
    
    # File Metadata
    created_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    accessed_date = db.Column(db.DateTime)
    author = db.Column(db.String(300))
    last_modified_by = db.Column(db.String(300))
    
    # Email Metadata
    email_from = db.Column(db.String(300))
    email_to = db.Column(db.Text)  # CSV
    email_cc = db.Column(db.Text)  # CSV
    email_bcc = db.Column(db.Text)  # CSV
    email_subject = db.Column(db.String(500))
    email_received_date = db.Column(db.DateTime)
    email_sent_date = db.Column(db.DateTime)
    
    # Document Properties
    page_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    language = db.Column(db.String(20))  # ISO 639-1 code
    
    # Extracted Content
    keywords = db.Column(db.Text)  # CSV or JSON
    entities = db.Column(db.Text)  # JSON: persons, organizations, locations
    
    # Technical Metadata
    application = db.Column(db.String(200))  # Application that created it
    version = db.Column(db.String(50))
    template = db.Column(db.String(300))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evidence = db.relationship('EvidenceItem', foreign_keys=[evidence_id])
    
    def __repr__(self):
        return f'<DocumentMetadata Evidence:{self.evidence_id}>'


class LitigationHold(db.Model):
    """
    Manages litigation holds (legal holds) across the organization
    Tracks custodians and preserved materials
    """
    __tablename__ = 'litigation_hold'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Hold Information
    hold_name = db.Column(db.String(200), nullable=False)
    hold_uuid = db.Column(db.String(36), unique=True)
    
    # Timeline
    issued_date = db.Column(db.DateTime, nullable=False)
    effective_date = db.Column(db.DateTime)
    lifting_date = db.Column(db.DateTime)
    
    # Case Information
    initiating_event = db.Column(db.String(500), nullable=False)  # What triggered the hold
    
    # Hold Parameters
    hold_scope = db.Column(db.Text, nullable=False)  # Description of what's being held
    affected_systems = db.Column(db.Text)  # Email, file shares, databases, etc. (JSON)
    retention_instructions = db.Column(db.Text)
    
    # Custodians
    custodies = db.relationship('Custodian', backref='litigation_hold', cascade='all, delete-orphan')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='active')  # active, suspended, lifted
    
    # Metadata
    issued_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    issued_by = db.relationship('User', foreign_keys=[issued_by_id])
    hold_notices = db.relationship('HoldNotice', backref='litigation_hold', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LitigationHold {self.hold_name}>'


class Custodian(db.Model):
    """
    Individual custodian of records subject to litigation hold
    """
    __tablename__ = 'custodian'
    
    id = db.Column(db.Integer, primary_key=True)
    hold_id = db.Column(db.Integer, db.ForeignKey('litigation_hold.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Custodian Information
    name = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(200))
    department = db.Column(db.String(200))
    
    # Contact Information
    email = db.Column(db.String(300), nullable=False)
    phone = db.Column(db.String(20))
    employee_id = db.Column(db.String(50))
    
    # Systems/Locations
    email_account = db.Column(db.String(300))
    phone_numbers = db.Column(db.Text)  # Mobile, office, home
    file_locations = db.Column(db.Text)  # List of servers, shared drives
    
    # Hold Compliance
    acknowledgment_date = db.Column(db.DateTime)
    has_acknowledged = db.Column(db.Boolean, default=False)
    last_certification_date = db.Column(db.DateTime)
    has_certified_compliance = db.Column(db.Boolean, default=False)
    
    # Notes
    special_instructions = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, acknowledged, compliant, non_compliant
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Custodian {self.name}>'


class HoldNotice(db.Model):
    """
    Tracks hold notices sent to custodians
    """
    __tablename__ = 'hold_notice'
    
    id = db.Column(db.Integer, primary_key=True)
    hold_id = db.Column(db.Integer, db.ForeignKey('litigation_hold.id'), nullable=False)
    custodian_id = db.Column(db.Integer, db.ForeignKey('custodian.id'), nullable=False)
    
    # Notice Information
    notice_type = db.Column(db.String(50), default='initial')  # initial, reminder, modification, release
    notice_text = db.Column(db.Text, nullable=False)
    
    # Timeline
    sent_date = db.Column(db.DateTime, nullable=False)
    sent_via = db.Column(db.String(50))  # email, in_person, phone, etc.
    acknowledged_date = db.Column(db.DateTime)
    
    # Confirmation/Receipt
    recipient_email = db.Column(db.String(300))
    read_receipt = db.Column(db.Boolean)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    custodian = db.relationship('Custodian', foreign_keys=[custodian_id])
    
    def __repr__(self):
        return f'<HoldNotice {self.notice_type} for Custodian:{self.custodian_id}>'


class DocumentSearchQuery(db.Model):
    """
    Tracks saved search queries for document discovery
    """
    __tablename__ = 'document_search_query'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Query Information
    query_name = db.Column(db.String(300), nullable=False)
    query_type = db.Column(db.String(50))  # keyword, metadata, temporal, combination
    
    # Search Parameters (stored as JSON for flexibility)
    keywords = db.Column(db.Text)  # JSON array
    excluded_keywords = db.Column(db.Text)
    metadata_filters = db.Column(db.Text)  # JSON
    date_range_start = db.Column(db.DateTime)
    date_range_end = db.Column(db.DateTime)
    
    # Results
    results_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    
    # Metadata
    is_saved = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<DocumentSearchQuery {self.query_name}>'


class ESIProtocol(db.Model):
    """
    Electronically Stored Information (ESI) protocol agreements
    Defines how parties will handle ESI in discovery
    """
    __tablename__ = 'esi_protocol'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), unique=True, nullable=False)
    
    # Agreement Information
    agreement_date = db.Column(db.DateTime, nullable=False)
    parties_involved = db.Column(db.Text, nullable=False)  # CSV
    
    # ESI Definitions
    esi_scope = db.Column(db.Text, nullable=False)  # Definition of ESI for this case
    metadata_requirements = db.Column(db.Text)  # Native vs. extracted
    
    # Format & Production Requirements
    production_format = db.Column(db.String(100))  # native, pdf, tiff, etc.
    naming_convention = db.Column(db.String(300))  # Bates numbering scheme
    
    # Cost Allocation
    cost_responsibility = db.Column(db.String(100))  # requesting_party, producing_party, shared, etc.
    
    # Claims & Claw-back
    allows_clawback = db.Column(db.Boolean, default=False)
    claw_back_procedure = db.Column(db.Text)
    privilege_protocol = db.Column(db.Text)
    
    # Timeline
    search_methodology = db.Column(db.Text)
    custodian_list = db.Column(db.Text)
    search_terms = db.Column(db.Text)  # CSV or JSON
    
    # Technical Requirements
    technical_specifications = db.Column(db.Text)  # Load file formats, etc.
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<ESIProtocol Case:{self.case_id}>'
