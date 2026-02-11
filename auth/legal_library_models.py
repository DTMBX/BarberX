"""
Evident Legal Resource Library Models
Complete database schema for Supreme Court cases, founding documents, amendments, etc.
"""

from auth.models import db
from datetime import datetime
from enum import Enum
import uuid


class DocumentCategory(Enum):
    """Types of legal documents"""
    SUPREME_COURT = "supreme_court"
    COURT_OF_APPEALS = "court_of_appeals"
    DISTRICT_COURT = "district_court"
    FOUNDING_DOCUMENT = "founding_document"
    AMENDMENT = "amendment"
    BILL_OF_RIGHTS = "bill_of_rights"
    STATUTE = "statute"
    CONSTITUTION = "constitution"
    OPINION = "opinion"
    BRIEF = "brief"
    RULE = "rule"


class DocumentStatus(Enum):
    """Document status"""
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    WITHDRAWN = "withdrawn"
    ARCHIVED = "archived"


class LegalDocument(db.Model):
    """Legal document - Supreme Court cases, founding docs, amendments, etc."""
    __tablename__ = 'legal_documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Info
    title = db.Column(db.String(500), nullable=False, index=True)
    case_number = db.Column(db.String(100), unique=True, index=True)  # e.g., "No. 21-1086"
    docket_number = db.Column(db.String(100), index=True)
    
    # Classification
    category = db.Column(db.String(50), nullable=False, index=True)  # DocumentCategory
    status = db.Column(db.String(50), default='published')  # DocumentStatus
    
    # Content
    full_text = db.Column(db.Text, nullable=True)  # Full document text
    summary = db.Column(db.Text, nullable=True)  # Summary/abstract
    syllabus = db.Column(db.Text, nullable=True)  # Official syllabus
    
    # Metadata
    date_decided = db.Column(db.DateTime, nullable=True, index=True)
    date_filed = db.Column(db.DateTime, nullable=True, index=True)
    publication_date = db.Column(db.DateTime, nullable=True)
    
    # Court Information
    court = db.Column(db.String(200), nullable=True, index=True)  # "U.S. Supreme Court", etc.
    jurisdiction = db.Column(db.String(100), nullable=True)  # "Federal", "State", etc.
    
    # Parties
    petitioner = db.Column(db.String(500), nullable=True, index=True)
    respondent = db.Column(db.String(500), nullable=True, index=True)
    
    # Citation
    citation_supreme = db.Column(db.String(100), nullable=True, index=True)  # e.g., "597 U.S. 442"
    citation_reporter = db.Column(db.String(100), nullable=True)  # Secondary citations
    citation_westlaw = db.Column(db.String(100), nullable=True)
    citation_lexis = db.Column(db.String(100), nullable=True)
    
    # Justices
    author = db.Column(db.String(500), nullable=True)  # Authoring justice/official
    justices_concur = db.Column(db.JSON, nullable=True)  # List of concurring justices
    justices_dissent = db.Column(db.JSON, nullable=True)  # List of dissenting justices
    
    # Topics
    issues = db.Column(db.JSON, nullable=True)  # [{"topic": "First Amendment", "details": "..."}]
    keywords = db.Column(db.JSON, nullable=True)  # ["free speech", "prior restraint", ...]
    headnotes = db.Column(db.JSON, nullable=True)  # Legal headnotes
    
    # Relationships
    related_cases = db.Column(db.JSON, nullable=True)  # [{"case_id": "...", "relationship": "overruled"}]
    statutes_cited = db.Column(db.JSON, nullable=True)  # Statutes cited in opinion
    cases_cited = db.Column(db.JSON, nullable=True)  # Cases cited in opinion
    
    # Links
    url_supremecourt = db.Column(db.String(500), nullable=True)
    url_google_scholar = db.Column(db.String(500), nullable=True)
    url_justia = db.Column(db.String(500), nullable=True)
    
    # Document metadata
    file_path = db.Column(db.String(500), nullable=True)  # For uploaded documents
    file_hash = db.Column(db.String(64), nullable=True)  # SHA-256 for deduplication
    import_source = db.Column(db.String(200), nullable=True)  # "supremecourt.gov", "congress.gov", etc.
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = db.Column(db.DateTime, nullable=True)  # For search indexing
    
    # Access tracking
    view_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'case_number': self.case_number,
            'category': self.category,
            'status': self.status,
            'date_decided': self.date_decided.isoformat() if self.date_decided else None,
            'court': self.court,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'citation_supreme': self.citation_supreme,
            'author': self.author,
            'keywords': self.keywords,
            'summary': self.summary,
            'url_supremecourt': self.url_supremecourt,
            'view_count': self.view_count,
        }


class DocumentCollection(db.Model):
    """Collections of legal documents (e.g., "4th Amendment Cases", "Free Speech Precedents")"""
    __tablename__ = 'document_collections'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)  # "Constitutional", "Statutory", etc.
    
    document_ids = db.Column(db.JSON, nullable=True)  # List of document IDs
    document_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SearchIndex(db.Model):
    """Full-text search index"""
    __tablename__ = 'search_index'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    document_id = db.Column(db.String(36), db.ForeignKey('legal_documents.id'), nullable=False, index=True)
    
    # Search fields
    search_text = db.Column(db.Text, nullable=False)  # Combined text for fulltext search
    vector = db.Column(db.LargeBinary, nullable=True)  # For vector search (embeddings)
    
    indexed_at = db.Column(db.DateTime, default=datetime.utcnow)


class DocumentComment(db.Model):
    """User annotations and comments on documents"""
    __tablename__ = 'document_comments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    document_id = db.Column(db.String(36), db.ForeignKey('legal_documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    highlight_text = db.Column(db.Text, nullable=True)  # Text being commented on
    comment = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedDocument(db.Model):
    """Documents saved by users"""
    __tablename__ = 'saved_documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    document_id = db.Column(db.String(36), db.ForeignKey('legal_documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    folder = db.Column(db.String(200), nullable=True)  # User's folder name
    
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.Text, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('document_id', 'user_id', name='unique_saved_doc'),)


class DocumentVersion(db.Model):
    """Track different versions of documents"""
    __tablename__ = 'document_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    document_id = db.Column(db.String(36), db.ForeignKey('legal_documents.id'), nullable=False)
    
    version_number = db.Column(db.Integer, default=1)
    version_date = db.Column(db.DateTime, nullable=True)
    
    full_text = db.Column(db.Text, nullable=True)
    changes = db.Column(db.Text, nullable=True)  # What changed in this version
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
