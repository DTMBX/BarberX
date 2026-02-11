"""
Legal Violations Detection Models
Comprehensive models for detecting constitutional, statutory, procedural, 
ethical, and moral code violations in legal documents
"""

from datetime import datetime
from enum import Enum
from auth.models import db, User


class ViolationType(Enum):
    """Comprehensive violation categorization"""
    CONSTITUTIONAL = "constitutional"
    STATUTORY = "statutory"
    PROCEDURAL = "procedural"
    ETHICAL = "ethical"
    MORAL_CODE = "moral_code"
    CONTRACT = "contract"
    ADMINISTRATIVE = "administrative"
    INTERNATIONAL = "international"
    DISCOVERY_FRAUD = "discovery_fraud"
    PRIVILEGE = "privilege"


class ViolationSeverity(Enum):
    """Impact assessment of violation"""
    MINOR = 1
    MODERATE = 2
    SEVERE = 3
    CRITICAL = 4


class ConfidenceLevel(Enum):
    """Detection sophistication level"""
    BASIC = 1
    COMPREHENSIVE = 2
    EXPERT = 3


class LegalViolation(db.Model):
    """
    Comprehensive record of detected legal violation
    Stores detection results, legal analysis, and expert review
    """
    __tablename__ = 'legal_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), nullable=False, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False, index=True)
    
    # Violation Details
    violation_type = db.Column(db.String(50), nullable=False)  # ViolationType enum
    violation_category = db.Column(db.String(100), nullable=False)  # e.g., "4th Amendment", "FRCP 26"
    severity = db.Column(db.String(20), nullable=False)  # ViolationSeverity
    confidence_level = db.Column(db.String(20), nullable=False)  # ConfidenceLevel
    confidence_score = db.Column(db.Float, nullable=False)  # 0-1 probability
    
    # Detection Details
    detected_text = db.Column(db.Text)  # The specific passage or audio segment
    detection_location = db.Column(db.String(500))  # Page number, timestamp, etc.
    detection_context = db.Column(db.Text)  # Surrounding context for understanding
    
    # Legal Basis
    applicable_rule = db.Column(db.String(500), nullable=False)  # Constitutional provision, statute, rule
    applicable_jurisdiction = db.Column(db.String(100))  # Federal, State, Circuit, District
    jurisdiction_code = db.Column(db.String(20))  # US, CA, IL, etc.
    supporting_precedents = db.Column(db.Text)  # JSON: [{citation, court, year, holding}]
    
    # Analysis
    violation_explanation = db.Column(db.Text, nullable=False)  # Why this is a violation
    legal_implications = db.Column(db.Text)  # Case impact analysis
    remedial_options = db.Column(db.Text)  # JSON: possible remedies
    case_impact_assessment = db.Column(db.Text)  # Potential impact on outcome
    
    # Evidence of Violation
    direct_quote = db.Column(db.Text)  # Exact violation text
    supporting_evidence = db.Column(db.Text)  # JSON: cross-references
    counterarguments = db.Column(db.Text)  # JSON: defense arguments
    
    # Detection Metadata
    detection_engine = db.Column(db.String(100))  # AI model that detected it
    detection_method = db.Column(db.String(100))  # keyword, ml_inference, rule_based, semantic
    model_version = db.Column(db.String(50))
    processing_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Expert Review & Verification
    reviewed_by_attorney_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    attorney_agrees = db.Column(db.Boolean)  # True/False/None (not reviewed)
    attorney_comments = db.Column(db.Text)
    attorney_confidence_level = db.Column(db.String(20))  # Expert assessment
    review_date = db.Column(db.DateTime)
    
    # Case Status
    is_cited = db.Column(db.Boolean, default=False)  # Used in case documents
    cited_in = db.Column(db.Text)  # JSON: document IDs that cite this
    impact_on_case = db.Column(db.String(50))  # critical, moderate, minimal
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attorney = db.relationship('User', foreign_keys=[reviewed_by_attorney_id])
    
    def __repr__(self):
        return f'<LegalViolation {self.violation_category} Severity:{self.severity}>'


class ConstitutionalViolation(db.Model):
    """Specific constitutional law violations"""
    __tablename__ = 'constitutional_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), unique=True)
    
    # Amendment Specifics
    amendment = db.Column(db.String(20), nullable=False)  # "1st", "4th", "5th", etc.
    amendment_clause = db.Column(db.String(200))  # specific clause
    
    # Category of Violation
    violation_subcategory = db.Column(db.String(100), nullable=False)
    # 4th Amendment: illegal_search, unreasonable_seizure, no_warrant, no_probable_cause
    # 5th Amendment: self_incrimination, double_jeopardy, due_process, takings
    # 6th Amendment: counsel, confrontation, speedy_trial, impartial_jury
    # 1st Amendment: free_speech, free_press, free_assembly, free_exercise
    # 14th Amendment: equal_protection, due_process, privileges_immunities
    
    # Constitutional Analysis
    fundamental_right = db.Column(db.Boolean)  # Was fundamental right implicated
    suspect_classification = db.Column(db.String(100))  # race, gender, religion, etc.
    strict_scrutiny = db.Column(db.Boolean)  # Highest level of review applies
    compelling_interest = db.Column(db.String(300))  # Government's purported interest
    narrowly_tailored = db.Column(db.Boolean)  # Is law narrowly tailored to interest
    
    # Supreme Court Precedents
    primary_scotus_case = db.Column(db.String(200))  # e.g., "Miranda v. Arizona"
    scotus_precedent_citation = db.Column(db.String(200))  # e.g., "384 U.S. 436 (1966)"
    scotus_year = db.Column(db.Integer)
    scotus_quote = db.Column(db.Text)  # Relevant quote from decision
    
    # Circuit/State Variations
    circuit_split_exists = db.Column(db.Boolean, default=False)
    circuit_authority = db.Column(db.String(100))  # "9th Cir.", "2nd Cir.", etc.
    state_law_variance = db.Column(db.String(200))  # How state law differs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConstitutionalViolation {self.amendment} Amendment>'


class StatutoryViolation(db.Model):
    """Federal or state statutory violations"""
    __tablename__ = 'statutory_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), unique=True)
    
    # Statute Information
    statute_name = db.Column(db.String(200), nullable=False)  # e.g., "Title VII"
    statute_citation = db.Column(db.String(100), nullable=False)  # e.g., "42 U.S.C. § 2000e"
    statute_type = db.Column(db.String(50), nullable=False)  # federal, state
    jurisdiction = db.Column(db.String(20))  # State code if applicable
    
    # Statutory Elements
    required_elements = db.Column(db.Text)  # JSON: list of elements
    elements_satisfied = db.Column(db.Text)  # JSON: which elements proven
    elements_missing = db.Column(db.Text)  # JSON: missing elements
    
    # Violation Nature
    violation_provision = db.Column(db.String(200))  # Which provision violated
    prohibited_conduct = db.Column(db.Text)  # What was prohibited
    actual_conduct = db.Column(db.Text)  # What actually happened
    
    # Statutory Interpretations
    plain_language = db.Column(db.Text)  # Plain meaning analysis
    legislative_intent = db.Column(db.Text)  # Intent from history
    agency_guidance = db.Column(db.Text)  # Regulatory agency interpretation
    
    # Penalties & Remedies
    civil_penalties = db.Column(db.Float)  # Potential damages
    criminal_penalties = db.Column(db.String(200))  # Prison time, fines
    injunctive_relief = db.Column(db.String(200))  # Possible orders
    attorney_fees = db.Column(db.Boolean, default=False)  # Available
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StatutoryViolation {self.statute_citation}>'


class ProceduralViolation(db.Model):
    """Court procedure and discovery rule violations"""
    __tablename__ = 'procedural_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), unique=True)
    
    # Rule Details
    rule_set = db.Column(db.String(50), nullable=False)  # FRCP, FRE, state rules
    rule_number = db.Column(db.String(20), nullable=False)  # e.g., "26", "33"
    rule_citation = db.Column(db.String(100), nullable=False)  # Full citation
    rule_text = db.Column(db.Text)  # The actual rule
    
    # Violation Type
    violation_subcategory = db.Column(db.String(100), nullable=False)
    # FRCP 26: improper_discovery, failure_to_disclose, evasive_response, unauthorized_expert
    # FRCP 33: improper_interrogatory, improper_number, burden_objection
    # FRCP 34: improper_request, improper_objection
    # FRE: hearsay, authentication, best_evidence
    
    # Discovery-Specific
    discovery_obligation = db.Column(db.String(200))  # What was required
    response_status = db.Column(db.String(50))  # complete, partial, absent, evasive
    objection_given = db.Column(db.Boolean)
    objection_basis = db.Column(db.String(200))  # overbroad, burdensome, privileged, etc.
    objection_valid = db.Column(db.Boolean)  # Is objection valid
    
    # Consequences
    subject_to_sanctions = db.Column(db.Boolean, default=True)
    sanction_type = db.Column(db.String(100))  # monetary, preclusion, default
    preclusion_likelihood = db.Column(db.Float)  # 0-1 likelihood evidence barred
    default_judgment_risk = db.Column(db.Float)  # Risk of default judgment
    
    # Meet and Confer
    meet_confer_required = db.Column(db.Boolean)
    meet_confer_occurred = db.Column(db.Boolean)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProceduralViolation {self.rule_citation}>'


class EthicalViolation(db.Model):
    """Model Rules of Professional Conduct violations"""
    __tablename__ = 'ethical_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), unique=True)
    
    # Rule Details
    model_rule = db.Column(db.String(20), nullable=False)  # e.g., "1.6", "3.3"
    rule_name = db.Column(db.String(100), nullable=False)  # e.g., "Confidentiality"
    jurisdiction_rules = db.Column(db.Text)  # JSON: variations by jurisdiction
    
    # Violation Nature
    violation_subcategory = db.Column(db.String(100), nullable=False)
    # Rule 1.6: privilege_breach, accidental_disclosure, inadequate_safeguards
    # Rule 3.3: false_statement, material_fact_omission, evidence_destruction
    # Rule 3.4: evidence_tampering, witness_intimidation, improper_discovery
    # Rule 4.4: inadvertent_privilege_disclosure
    # Rule 5.1: supervisory_failure
    # Rule 8.4: misconduct
    
    # Specific Conduct
    prohibited_conduct = db.Column(db.Text, nullable=False)  # What was done wrong
    actual_conduct = db.Column(db.Text)  # What attorney/firm did
    
    # Intent & Knowledge
    intentional = db.Column(db.Boolean)  # Knowing violation
    reckless = db.Column(db.Boolean)  # Reckless disregard
    negligent = db.Column(db.Boolean)  # Merely negligent
    
    # Disciplinary Exposure
    discipline_risk = db.Column(db.String(100))  # warning, suspension, disbarment
    sanction_likelihood = db.Column(db.Float)  # 0-1 likelihood of sanction
    
    # Affected Parties
    affected_client = db.Column(db.String(300))  # Client damaged
    affected_opponent = db.Column(db.String(300))  # Opposing party
    affected_court = db.Column(db.String(300))  # Court prejudiced
    
    # Remediation
    remediation_possible = db.Column(db.Boolean)
    remediation_steps = db.Column(db.Text)  # How to fix it
    notice_required = db.Column(db.Boolean)  # Must notify parties/court
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EthicalViolation Rule {self.model_rule}>'


class DiscoveryFraudViolation(db.Model):
    """Spoliation, metadata destruction, and discovery abuse"""
    __tablename__ = 'discovery_fraud_violation'
    
    id = db.Column(db.Integer, primary_key=True)
    legal_violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), unique=True)
    
    # Fraud Type
    fraud_type = db.Column(db.String(100), nullable=False)
    # spoliation, metadata_destruction, improper_production, bates_fraud, redaction_fraud
    
    # Document Details
    affected_documents = db.Column(db.Integer)  # Number of documents
    affected_pages = db.Column(db.Integer)
    date_destroyed = db.Column(db.DateTime)
    destruction_method = db.Column(db.String(100))  # deleted, burnt, shredded, etc.
    
    # Timing Issues
    destruction_after_notice = db.Column(db.Boolean)  # Destroyed after litigation notice
    litigation_hold_in_effect = db.Column(db.Boolean)  # Hold was in place
    notice_of_claim = db.Column(db.DateTime)  # When party knew of claim
    
    # Inference & Prejudice
    adverse_inference = db.Column(db.Boolean, default=True)  # Can infer evidence supported opponent
    prejudice_to_opponent = db.Column(db.String(300))
    impact_on_case = db.Column(db.String(300))
    
    # Intentionality
    intentional_destruction = db.Column(db.Boolean)
    willful = db.Column(db.Boolean)
    good_faith_destruction = db.Column(db.Boolean)  # Was it inadvertent
    
    # Sanctions
    sanctions_appropriate = db.Column(db.Boolean, default=True)
    terminating_sanctions = db.Column(db.Boolean)  # Case dismissal risk
    default_judgment = db.Column(db.Boolean)  # Default judgment risk
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DiscoveryFraudViolation {self.fraud_type}>'


class ViolationCache(db.Model):
    """Cache for violation detection results to avoid redundant analysis"""
    __tablename__ = 'violation_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence_item.id'), unique=True, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), index=True)
    
    # Cache Status
    analysis_complete = db.Column(db.Boolean, default=False)
    violations_found = db.Column(db.Integer, default=0)
    
    # Cached Results
    violation_ids = db.Column(db.Text)  # JSON: list of violation IDs
    critical_count = db.Column(db.Integer, default=0)
    severe_count = db.Column(db.Integer, default=0)
    moderate_count = db.Column(db.Integer, default=0)
    minor_count = db.Column(db.Integer, default=0)
    
    # Cache Metadata
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzer_version = db.Column(db.String(50))  # Which version analyzed this
    
    # Invalidation
    needs_reanalysis = db.Column(db.Boolean, default=False)
    reanalysis_reason = db.Column(db.String(200))  # Why cache is stale
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ViolationCache Evidence:{self.evidence_id}>'


class ViolationTrendAnalysis(db.Model):
    """Analyze violation patterns across cases"""
    __tablename__ = 'violation_trend_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Analysis Period
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    
    # Violation Trends
    most_common_violation = db.Column(db.String(100))
    most_severe_violation = db.Column(db.String(100))
    violation_frequency = db.Column(db.Text)  # JSON: counts by type
    
    # Opposing Party Patterns
    opposing_party_violations = db.Column(db.Text)  # JSON: violations by opponent
    party_violation_pattern = db.Column(db.String(200))  # Pattern description
    
    # Jurisdiction Patterns
    jurisdiction_common_violations = db.Column(db.Text)  # JSON
    state_variation = db.Column(db.String(200))  # How violations vary by state
    
    # Recommendations
    strategic_implications = db.Column(db.Text)  # How to use violation patterns
    case_strenghs = db.Column(db.Text)  # Where case is strong
    case_weaknesses = db.Column(db.Text)  # Where case is weak
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ViolationTrendAnalysis Case:{self.case_id}>'


class ViolationReportingLog(db.Model):
    """Track what violations were reported to whom and when"""
    __tablename__ = 'violation_reporting_log'
    
    id = db.Column(db.Integer, primary_key=True)
    violation_id = db.Column(db.Integer, db.ForeignKey('legal_violation.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('legal_case.id'), nullable=False)
    
    # Reporting
    reported_to = db.Column(db.String(300))  # Attorney, judge, bar association, etc.
    reported_date = db.Column(db.DateTime)
    report_method = db.Column(db.String(100))  # email, letter, motion, affidavit
    
    # Action Taken
    action_taken = db.Column(db.String(200))  # What response was given
    action_date = db.Column(db.DateTime)
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    resolved = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ViolationReportingLog Violation:{self.violation_id}>'
