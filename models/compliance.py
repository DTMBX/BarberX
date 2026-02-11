"""
Legal Compliance & Reporting Models
Models for regulatory compliance tracking, audit logs, and legal reporting
"""

from datetime import datetime
from auth.models import db, User


class ComplianceObligation(db.Model):
    """
    Tracks specific compliance obligations for a case
    """
    __tablename__ = 'compliance_obligation'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Obligation Definition
    obligation_name = db.Column(db.String(300), nullable=False)
    obligation_type = db.Column(db.String(100), nullable=False)  # disclosure, preservation, production, certification, etc.
    regulation = db.Column(db.String(200))  # FRCP 26, FRCP 33, etc.
    description = db.Column(db.Text)
    
    # Timeline
    identified_date = db.Column(db.DateTime, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, waived, extension_granted
    is_met = db.Column(db.Boolean, default=False)
    
    # Compliance Details
    required_actions = db.Column(db.Text)  # JSON array of actions
    responsible_party = db.Column(db.String(300))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Documentation
    supporting_documents = db.Column(db.Text)  # JSON array of document IDs
    certification_status = db.Column(db.String(50))  # uncertified, certified
    certified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    certified_date = db.Column(db.DateTime)
    
    # Risk Assessment
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    remediation_plan = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    certified_by = db.relationship('User', foreign_keys=[certified_by_id])
    
    def __repr__(self):
        return f'<ComplianceObligation {self.obligation_name}>'


class DeadlineTracker(db.Model):
    """
    Tracks all case deadlines and milestones
    """
    __tablename__ = 'deadline_tracker'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Deadline Information
    deadline_name = db.Column(db.String(300), nullable=False)
    deadline_date = db.Column(db.DateTime, nullable=False)
    deadline_type = db.Column(db.String(100))  # discovery, motion, disclosure, trial, etc.
    
    # Related Documents
    court_order = db.Column(db.String(500))  # Reference to order
    regulation = db.Column(db.String(200))  # FRCP 26, etc.
    
    # Status & Completion
    status = db.Column(db.String(50), default='pending')  # pending, met, missed, extended, waived
    completion_date = db.Column(db.DateTime)
    extension_granted = db.Column(db.Boolean, default=False)
    new_deadline = db.Column(db.DateTime)
    
    # Responsibility
    responsible_party = db.Column(db.String(300))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Notifications
    days_before_alert = db.Column(db.Integer, default=7)
    alert_sent = db.Column(db.Boolean, default=False)
    alert_sent_date = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f'<DeadlineTracker {self.deadline_name}>'


class AuditLog(db.Model):
    """
    Comprehensive audit log for all system activities
    """
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'))
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'))
    
    # Activity Information
    activity_type = db.Column(db.String(100), nullable=False)  # view, edit, delete, export, access, etc.
    entity_type = db.Column(db.String(100), nullable=False)  # evidence, case, document, user, etc.
    entity_id = db.Column(db.String(100))
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(200))
    
    # Change Details
    old_value = db.Column(db.Text)  # Previous value if applicable
    new_value = db.Column(db.Text)  # New value if applicable
    description = db.Column(db.Text)  # Full description
    
    # Security Information
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    
    # Result
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Timestamp (immutable)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<AuditLog {self.activity_type} by {self.username}>'


class CustodyAffidavit(db.Model):
    """
    Records custodian affidavits for chain of custody certification
    """
    __tablename__ = 'custody_affidavit'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'))
    
    # Affiant Information
    affiant_name = db.Column(db.String(300), nullable=False)
    affiant_title = db.Column(db.String(200))
    affiant_organization = db.Column(db.String(300))
    affiant_contact = db.Column(db.String(300))
    
    # Affidavit Content
    affidavit_date = db.Column(db.DateTime, nullable=False)
    custody_statement = db.Column(db.Text, nullable=False)  # Formal statement of custody
    
    # Evidence Covered
    materials_described = db.Column(db.Text, nullable=False)  # Description of covered materials
    
    # Administration of Oath
    administered_by = db.Column(db.String(300))  # Notary or court official
    administered_date = db.Column(db.DateTime)
    
    # Signature/Verification
    is_signed = db.Column(db.Boolean, default=False)
    signature_date = db.Column(db.DateTime)
    signature_file = db.Column(db.String(500))  # Path to stored signature image
    
    # Legal Compliance
    sworn_under_penalty = db.Column(db.Boolean, default=True)
    jurisdiction = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, signed, notarized, filed, challenged
    
    # Storage
    affidavit_document_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'))  # If stored as document
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    affidavit_document = db.relationship('EvidenceItem', foreign_keys=[affidavit_document_id])
    
    def __repr__(self):
        return f'<CustodyAffidavit {self.affiant_name}>'


class CertificationOfCustody(db.Model):
    """
    Official certification of evidence custody for legal proceedings
    """
    __tablename__ = 'certification_of_custody'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Certification Information
    certification_date = db.Column(db.DateTime, nullable=False)
    certification_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Certifying Officer
    certifying_officer = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(200))
    organization = db.Column(db.String(300))
    
    # Materials Certificate
    materials_description = db.Column(db.Text, nullable=False)
    total_items = db.Column(db.Integer)
    
    # Custody Chain
    custody_chain_summary = db.Column(db.Text)  # Summary of chain of custody
    
    # Certification Statement
    certification_statement = db.Column(db.Text, nullable=False)  # Official statement
    
    # Integrity Assurances
    maintained_integrity = db.Column(db.Boolean, default=True)
    not_altered = db.Column(db.Boolean, default=True)
    proper_storage = db.Column(db.Boolean, default=True)
    access_controlled = db.Column(db.Boolean, default=True)
    
    # Signature & Verification
    is_signed = db.Column(db.Boolean, default=False)
    signature_date = db.Column(db.DateTime)
    notarized = db.Column(db.Boolean, default=False)
    notary_seal_date = db.Column(db.DateTime)
    
    # Submission
    submitted_to = db.Column(db.String(300))  # Court, opposing counsel, etc.
    submission_date = db.Column(db.DateTime)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, signed, notarized, filed, challenged, accepted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submitted_by = db.relationship('User', foreign_keys=[submitted_by_id])
    
    def __repr__(self):
        return f'<CertificationOfCustody {self.certification_number}>'


class ComplianceReport(db.Model):
    """
    Automated compliance reports and certifications
    """
    __tablename__ = 'compliance_report'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Report Information
    report_name = db.Column(db.String(300), nullable=False)
    report_type = db.Column(db.String(100), nullable=False)  # discovery, production, privilege_log, hold, etc.
    report_period_start = db.Column(db.DateTime)
    report_period_end = db.Column(db.DateTime)
    
    # Report Content
    report_summary = db.Column(db.Text)  # Executive summary
    detailed_findings = db.Column(db.Text)  # JSON with detailed data
    recommendations = db.Column(db.Text)  # JSON array
    
    # Compliance Assessment
    overall_compliance_status = db.Column(db.String(50))  # compliant, non_compliant, partial, needs_review
    compliance_percentage = db.Column(db.Float)
    
    # Issues & Remediation
    critical_issues = db.Column(db.Integer, default=0)
    major_issues = db.Column(db.Integer, default=0)
    minor_issues = db.Column(db.Integer, default=0)
    issues_remediated = db.Column(db.Integer, default=0)
    
    # Sign-Off
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_date = db.Column(db.DateTime)
    approved = db.Column(db.Boolean, default=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_date = db.Column(db.DateTime)
    
    # Metadata
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    distribution_list = db.Column(db.Text)  # JSON array of recipients
    
    # Relationships
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f'<ComplianceReport {self.report_name}>'


class RiskAssessment(db.Model):
    """
    Risk assessments for discovery and litigation
    """
    __tablename__ = 'risk_assessment'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Assessment Information
    assessment_name = db.Column(db.String(300), nullable=False)
    assessment_date = db.Column(db.DateTime, nullable=False)
    risk_area = db.Column(db.String(100), nullable=False)  # discovery_completeness, privilege, redaction, etc.
    
    # Risk Evaluation
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    probability = db.Column(db.Float)  # 0-1
    impact = db.Column(db.Float)  # 0-1
    risk_score = db.Column(db.Float)  # Calculated risk
    
    # Risk Description
    risk_description = db.Column(db.Text, nullable=False)
    potential_consequences = db.Column(db.Text)
    
    # Mitigation
    mitigation_strategy = db.Column(db.Text)
    responsible_party = db.Column(db.String(300))
    mitigation_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, mitigated, accepted, rejected
    
    # Monitoring
    monitoring_plan = db.Column(db.Text)
    next_review_date = db.Column(db.DateTime)
    
    # Assessment Details
    assessed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessed_by = db.relationship('User', foreign_keys=[assessed_by_id])
    
    def __repr__(self):
        return f'<RiskAssessment {self.assessment_name}>'


class LegalHold_Evidence(db.Model):
    """
    Junction table linking litigation holds to specific evidence items
    """
    __tablename__ = 'legal_hold_evidence'
    
    id = db.Column(db.Integer, primary_key=True)
    hold_id = db.Column(db.Integer, db.ForeignKey('litigation_hold.id'), nullable=False, index=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, index=True)
    
    # Relationship Details
    included_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_preserved = db.Column(db.Boolean, default=True)
    preservation_method = db.Column(db.String(100))  # backup, snapshot, archive, etc.
    
    # Status Tracking
    status = db.Column(db.String(50), default='held')  # held, released, transferred
    released_date = db.Column(db.DateTime)
    release_reason = db.Column(db.String(300))
    
    # Metadata
    notes = db.Column(db.Text)
    
    __table_args__ = (db.UniqueConstraint('hold_id', 'evidence_id', name='uq_hold_evidence'),)
    
    def __repr__(self):
        return f'<LegalHold_Evidence Hold:{self.hold_id} Evidence:{self.evidence_id}>'


class DocumentRetention(db.Model):
    """
    Tracks retention and destruction of documents
    """
    __tablename__ = 'document_retention'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Retention Policy
    retention_policy = db.Column(db.String(200), nullable=False)
    retention_period = db.Column(db.String(100))  # e.g., "7 years"
    scheduled_destruction_date = db.Column(db.DateTime)
    
    # Hold Status
    is_under_legal_hold = db.Column(db.Boolean, default=False)
    hold_reason = db.Column(db.Text)
    
    # Destruction
    destruction_approved = db.Column(db.Boolean, default=False)
    destruction_approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    destruction_approved_date = db.Column(db.DateTime)
    
    destruction_completed = db.Column(db.Boolean, default=False)
    destruction_date = db.Column(db.DateTime)
    destruction_method = db.Column(db.String(100))  # shred, securely_delete, burn, etc.
    destruction_completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Certification
    destruction_certificate = db.Column(db.String(500))  # Path to certificate
    certificate_issuer = db.Column(db.String(300))
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    destruction_approved_by = db.relationship('User', foreign_keys=[destruction_approved_by_id])
    destruction_completed_by = db.relationship('User', foreign_keys=[destruction_completed_by_id])
    
    def __repr__(self):
        return f'<DocumentRetention Evidence:{self.evidence_id}>'
