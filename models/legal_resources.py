"""
Evident Legal Resource Library - Database Models
Comprehensive storage for Supreme Court cases, founding documents, amendments, and legal precedents
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from auth.models import db


class DocumentType(Enum):
    """Types of legal documents"""
    FOUNDING_DOCUMENT = "founding_document"
    AMENDMENT = "amendment"
    BILL_OF_RIGHTS = "bill_of_rights"
    SUPREME_COURT_OPINION = "supreme_court_opinion"
    PRECEDENT = "precedent"
    STATUTE = "statute"
    REGULATION = "regulation"
    COURT_RULE = "court_rule"
    OTHER = "other"


class CaseStatus(Enum):
    """Status of a case"""
    PENDING = "pending"
    DECIDED = "decided"
    REMANDED = "remanded"
    DISMISSED = "dismissed"
    SETTLED = "settled"


class LegalDocument(db.Model):
    """Base model for all legal documents"""
    __tablename__ = 'legal_documents'

    id = db.Column(db.Integer, primary_key=True)
    
    # Core metadata
    title = db.Column(db.String(500), nullable=False, index=True)
    document_type = db.Column(db.Enum(DocumentType), nullable=False, index=True)
    citation = db.Column(db.String(200), unique=True, index=True)  # e.g., "U.S. Const. art. III"
    
    # Content
    full_text = db.Column(Text, nullable=False)
    summary = db.Column(Text)
    excerpt = db.Column(db.String(1000))  # First excerpt for search results
    
    # Dates
    effective_date = db.Column(db.DateTime)
    published_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ratified_date = db.Column(db.DateTime)
    
    # Metadata
    author_or_drafter = db.Column(db.String(255))
    jurisdiction = db.Column(db.String(100))  # Federal, State, etc.
    tags = db.Column(JSON)  # Array of tags for categorization
    related_documents = db.Column(JSON)  # IDs of related documents
    
    # Source tracking
    source_url = db.Column(db.String(500))
    source_database = db.Column(db.String(100))  # e.g., "supremecourt.gov"
    version = db.Column(db.String(50))
    
    # Indexing
    full_text_index = db.Column(db.String(5000))  # For full-text search
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opinions = relationship('CourtOpinion', back_populates='document', lazy='dynamic')
    cases = relationship('SupremeCourtCase', back_populates='primary_document', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_doc_type_citation', 'document_type', 'citation'),
        Index('idx_published_date', 'published_date'),
    )

    def __repr__(self):
        return f"<LegalDocument {self.citation}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'document_type': self.document_type.value,
            'citation': self.citation,
            'excerpt': self.excerpt,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'jurisdiction': self.jurisdiction,
            'tags': self.tags or [],
            'source_url': self.source_url,
        }


class SupremeCourtCase(db.Model):
    """Supreme Court case metadata and information"""
    __tablename__ = 'supreme_court_cases'

    id = db.Column(db.Integer, primary_key=True)
    
    # Case identification
    case_name = db.Column(db.String(500), nullable=False, index=True)
    case_numbers = db.Column(JSON, nullable=False)  # Array of case numbers
    docket_number = db.Column(db.String(50), unique=True, index=True)
    citation = db.Column(db.String(200), unique=True, index=True)  # e.g., "410 U.S. 113"
    
    # Parties
    petitioner = db.Column(db.String(500), index=True)
    respondent = db.Column(db.String(500), index=True)
    
    # Case details
    summary = db.Column(Text)
    facts = db.Column(Text)
    question_presented = db.Column(Text)
    holding = db.Column(Text)
    status = db.Column(db.Enum(CaseStatus), nullable=False, default=CaseStatus.DECIDED)
    
    # Dates
    argued_date = db.Column(db.DateTime)
    decided_date = db.Column(db.DateTime, index=True)
    
    # Justices
    majority_justice = db.Column(db.String(255))
    concurring_justices = db.Column(JSON)  # Array of justice names
    dissenting_justices = db.Column(JSON)  # Array of justice names
    
    # Opinion information
    primary_document_id = db.Column(db.Integer, ForeignKey('legal_documents.id'))
    primary_document = relationship('LegalDocument', back_populates='cases')
    
    # Related information
    lower_court_citation = db.Column(db.String(200))
    lower_court_holding = db.Column(Text)
    precedents_cited = db.Column(JSON)  # Citations of precedent cases
    
    # Metadata
    areas_of_law = db.Column(JSON)  # e.g., ["Constitutional Law", "First Amendment"]
    importance_score = db.Column(db.Float)  # 1-10 importance rating
    times_cited = db.Column(db.Integer)  # Number of times case is cited
    
    # Source
    source_url = db.Column(db.String(500))
    source = db.Column(db.String(100))  # e.g., "supremecourt.gov"
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opinions = relationship('CourtOpinion', back_populates='case', lazy='dynamic')
    annotations = relationship('CaseAnnotation', back_populates='case', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_case_argued_decided', 'argued_date', 'decided_date'),
        Index('idx_case_areas_importance', 'importance_score'),
    )

    def __repr__(self):
        return f"<SupremeCourtCase {self.citation}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'case_name': self.case_name,
            'citation': self.citation,
            'docket_number': self.docket_number,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'decided_date': self.decided_date.isoformat() if self.decided_date else None,
            'holding': self.holding,
            'areas_of_law': self.areas_of_law or [],
            'importance_score': self.importance_score,
            'times_cited': self.times_cited,
            'source_url': self.source_url,
        }


class CourtOpinion(db.Model):
    """Individual court opinions (majority, concurring, dissenting)"""
    __tablename__ = 'court_opinions'

    id = db.Column(db.Integer, primary_key=True)
    
    # Opinion identification
    case_id = db.Column(db.Integer, ForeignKey('supreme_court_cases.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, ForeignKey('legal_documents.id'), nullable=False)
    
    # Opinion type
    opinion_type = db.Column(db.String(50), nullable=False)  # "majority", "concurring", "dissenting", etc.
    author = db.Column(db.String(255), index=True)
    
    # Content
    full_text = db.Column(Text, nullable=False)
    summary = db.Column(Text)
    
    # Analysis
    key_phrases = db.Column(JSON)  # Important phrases and legal rules
    citations_made = db.Column(JSON)  # Cases and documents cited
    
    # Metadata
    page_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    published_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship('SupremeCourtCase', back_populates='opinions')
    document = relationship('LegalDocument', back_populates='opinions')
    
    __table_args__ = (
        Index('idx_opinion_case_type', 'case_id', 'opinion_type'),
    )

    def __repr__(self):
        return f"<CourtOpinion {self.case_id}-{self.opinion_type}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'opinion_type': self.opinion_type,
            'author': self.author,
            'summary': self.summary,
            'key_phrases': self.key_phrases or [],
            'citations_made': self.citations_made or [],
            'word_count': self.word_count,
        }


class Precedent(db.Model):
    """Case precedent and its usage"""
    __tablename__ = 'precedents'

    id = db.Column(db.Integer, primary_key=True)
    
    # Precedent identification
    precedent_case_id = db.Column(db.Integer, ForeignKey('supreme_court_cases.id'), nullable=False, index=True)
    citing_case_id = db.Column(db.Integer, ForeignKey('supreme_court_cases.id'), nullable=False, index=True)
    
    # Relationship
    citation_type = db.Column(db.String(50))  # "followed", "distinguished", "overruled", etc.
    context = db.Column(Text)  # How the precedent was used
    
    # Metadata
    weight_of_authority = db.Column(db.Float)  # How significant the citation is
    page_number = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    precedent_case = relationship('SupremeCourtCase', foreign_keys=[precedent_case_id])
    citing_case = relationship('SupremeCourtCase', foreign_keys=[citing_case_id])
    
    __table_args__ = (
        Index('idx_precedent_cases', 'precedent_case_id', 'citing_case_id'),
    )

    def __repr__(self):
        return f"<Precedent {self.precedent_case_id} cited by {self.citing_case_id}>"


class CaseAnnotation(db.Model):
    """Annotations and notes on cases"""
    __tablename__ = 'case_annotations'

    id = db.Column(db.Integer, primary_key=True)
    
    # Reference
    case_id = db.Column(db.Integer, ForeignKey('supreme_court_cases.id'), nullable=False, index=True)
    
    # Annotation details
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(Text, nullable=False)
    annotation_type = db.Column(db.String(50))  # "note", "summary", "analysis", "application", etc.
    
    # Source
    source = db.Column(db.String(255))
    source_url = db.Column(db.String(500))
    
    # Metadata
    applies_to_states = db.Column(JSON)  # States where this applies
    practical_impact = db.Column(Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship('SupremeCourtCase', back_populates='annotations')
    
    __table_args__ = (
        Index('idx_annotation_case_type', 'case_id', 'annotation_type'),
    )

    def __repr__(self):
        return f"<CaseAnnotation {self.id}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'title': self.title,
            'body': self.body,
            'annotation_type': self.annotation_type,
            'practical_impact': self.practical_impact,
            'applies_to_states': self.applies_to_states or [],
        }


class LegalTopic(db.Model):
    """Legal topics and areas of law for categorization"""
    __tablename__ = 'legal_topics'

    id = db.Column(db.Integer, primary_key=True)
    
    # Topic definition
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(Text)
    parent_topic_id = db.Column(db.Integer, ForeignKey('legal_topics.id'))
    
    # Hierarchy
    hierarchy_level = db.Column(db.Integer)  # 1 = top level, 2 = subtopic, etc.
    
    # Metadata
    document_count = db.Column(db.Integer, default=0)
    case_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    subtopics = relationship(
        'LegalTopic',
        remote_side=[parent_topic_id],
        foreign_keys=[parent_topic_id],
        backref='parent_topic'
    )

    def __repr__(self):
        return f"<LegalTopic {self.name}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'hierarchy_level': self.hierarchy_level,
            'document_count': self.document_count,
            'case_count': self.case_count,
        }


class UserResearchSession(db.Model):
    """Track user research sessions and search history"""
    __tablename__ = 'user_research_sessions'

    id = db.Column(db.Integer, primary_key=True)
    
    # User reference
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Session information
    session_name = db.Column(db.String(255))
    query_history = db.Column(JSON)  # Array of queries performed
    saved_documents = db.Column(JSON)  # IDs of saved legal documents
    saved_cases = db.Column(JSON)  # IDs of saved cases
    
    # Session analytics
    documents_viewed = db.Column(db.Integer, default=0)
    average_read_time = db.Column(db.Float)  # Seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    
    # User reference
    user = relationship('User', backref='research_sessions')

    def __repr__(self):
        return f"<UserResearchSession {self.id}>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_name': self.session_name,
            'documents_viewed': self.documents_viewed,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
        }
