"""
Evident Legal Case Models
Core data models for case management, evidence tracking, and legal workflows.

Design principles:
  - Cases are first-class entities for organizing evidence, analysis, and exports.
  - Evidence is linked to cases via CaseEvidence (many-to-many) — never copied.
  - Jurisdiction metadata is factual and non-inferential.
  - No legal conclusions are encoded in the schema.
"""

from datetime import datetime, timezone
from auth.models import db, User


class LegalCase(db.Model):
    """
    Represents a legal case or matter.
    Supports civil, criminal, administrative, and insurance matters.
    """
    __tablename__ = 'legal_case'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    case_name = db.Column(db.String(500), nullable=False)
    case_type = db.Column(db.String(50), nullable=False)  # civil, criminal, admin, insurance
    description = db.Column(db.Text)
    jurisdiction = db.Column(db.String(200))  # Federal, State (which state), County
    court_name = db.Column(db.String(300))
    judge_name = db.Column(db.String(200))

    # Jurisdiction metadata (factual, non-inferential)
    jurisdiction_state = db.Column(db.String(2))   # Two-letter state code (e.g., NJ, CA, TX)
    jurisdiction_agency_type = db.Column(db.String(100))  # law_enforcement, prosecutor, public_defender, court, regulatory
    retention_policy_ref = db.Column(db.String(500))  # Reference to applicable retention policy (metadata only)

    # Incident-level grouping (for BWC cross-sync)
    incident_number = db.Column(db.String(200), index=True)  # Agency incident/event number
    incident_date = db.Column(db.DateTime)
    
    # Dates
    filed_date = db.Column(db.DateTime)
    discovery_deadline = db.Column(db.DateTime)
    trial_date = db.Column(db.DateTime)
    
    # Status and Metadata
    status = db.Column(db.String(50), default='open')  # open, closed, on_hold, appeal
    is_legal_hold = db.Column(db.Boolean, default=False)
    legal_hold_date = db.Column(db.DateTime)
    
    # Access Control
    lead_attorney_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    
    # Audit
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    lead_attorney = db.relationship('User', foreign_keys=[lead_attorney_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    case_parties = db.relationship('CaseParty', backref='legal_case', cascade='all, delete-orphan')
    case_evidence_links = db.relationship('CaseEvidence', back_populates='case')
    privilege_logs = db.relationship('PrivilegeLog', backref='legal_case', cascade='all, delete-orphan')

    # Case events, timeline, and export records
    events = db.relationship(
        'Event', backref='case', lazy='dynamic',
        cascade='all, delete-orphan',
    )
    timeline_entries = db.relationship(
        'CaseTimelineEntry', backref='case', cascade='all, delete-orphan',
        order_by='CaseTimelineEntry.timestamp',
    )
    export_records = db.relationship(
        'CaseExportRecord', backref='case', cascade='all, delete-orphan',
    )

    # Keep backward-compatible relationship via origin_case_id for legacy queries
    origin_evidence_items = db.relationship(
        'EvidenceItem',
        foreign_keys='EvidenceItem.origin_case_id',
        backref='origin_case',
        lazy='dynamic',
    )

    @property
    def evidence_items(self):
        """Return all actively linked evidence items for this case."""
        return [link.evidence for link in self.case_evidence_links
                if link.unlinked_at is None]

    @property
    def evidence_count(self):
        """Count of actively linked evidence items."""
        return sum(1 for link in self.case_evidence_links if link.unlinked_at is None)

    def __repr__(self):
        return f'<LegalCase {self.case_number}: {self.case_name}>'


class Organization(db.Model):
    """
    Represents a law firm, police department, insurance company, or civic organization
    """
    __tablename__ = 'organization'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, unique=True)
    org_type = db.Column(db.String(50), nullable=False)  # law_firm, police, insurance, civic, prosecutor
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    website = db.Column(db.String(300))
    
    # Organization Configuration
    max_cases = db.Column(db.Integer, default=-1)  # -1 = unlimited
    max_users = db.Column(db.Integer, default=-1)
    storage_gb = db.Column(db.Integer, default=1000)
    
    # Features
    can_process_video = db.Column(db.Boolean, default=True)
    can_process_audio = db.Column(db.Boolean, default=True)
    can_use_ai_analysis = db.Column(db.Boolean, default=True)
    can_redact = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Organization {self.name}>'


class CaseParty(db.Model):
    """
    Represents parties involved in a case (plaintiff, defendant, witness, judge, etc.)
    """
    __tablename__ = 'case_party'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    name = db.Column(db.String(300), nullable=False)
    party_type = db.Column(db.String(50))  # plaintiff, defendant, witness, judge, attorney, investigator, adjuster
    role = db.Column(db.String(200))  # e.g., "Lead Defense Counsel", "Witness"
    
    contact_info = db.Column(db.String(300))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CaseParty {self.name} ({self.party_type})>'
