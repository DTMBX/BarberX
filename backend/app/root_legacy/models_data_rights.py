# models_data_rights.py
"""
Database models for data rights and export compliance.
Implements Pattern 2: Keep proprietary layers separate
"""

import json
from datetime import datetime

from .app import db


class DataSource(db.Model):
    """
    Track source type and rights for all data ingested.
    Pattern 1: Pointer, don't republish
    """

    __tablename__ = "data_sources"

    id = db.Column(db.String(32), primary_key=True)  # UUID
    source_type = db.Column(db.String(50), nullable=False, index=True)
    # Values: public_domain, client_provided, our_analysis,
    #         proprietary_database, copyrighted_document, opra_public_record

    source_name = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(1000))

    # Rights metadata
    export_allowed = db.Column(db.Boolean, default=True, nullable=False, index=True)
    fair_use_only = db.Column(db.Boolean, default=False)
    max_excerpt_words = db.Column(db.Integer, default=200)
    attribution_required = db.Column(db.Boolean, default=True)
    attribution_text = db.Column(db.Text)

    license = db.Column(db.String(200))
    copyright_holder = db.Column(db.String(200))
    restriction_reason = db.Column(db.Text)

    # Acquisition metadata
    acquired_by = db.Column(db.String(100))
    acquired_date = db.Column(db.DateTime, default=datetime.utcnow)
    acquisition_method = db.Column(db.String(100))  # OPRA request, Westlaw subscription, etc.

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "export_allowed": self.export_allowed,
            "attribution_text": self.attribution_text,
            "license": self.license,
        }


class CitationMetadata(db.Model):
    """
    Store citation metadata ONLY - never full copyrighted text.
    Pattern 1: Pointer, don't republish
    """

    __tablename__ = "citation_metadata"

    id = db.Column(db.String(32), primary_key=True)  # UUID
    case_id = db.Column(
        db.String(32), db.ForeignKey("public_case_data.id"), nullable=False, index=True
    )

    # Citation information (ALLOWED)
    citation = db.Column(db.String(500), nullable=False)  # "Smith v. Jones, 123 F.3d 456"
    westlaw_cite = db.Column(db.String(100))  # "2024 WL 123456" - citation only, NOT content
    lexis_cite = db.Column(db.String(100))  # "2024 U.S. App. LEXIS 5678"
    bluebook_cite = db.Column(db.String(500))

    # Pointer to authoritative source (ALLOWED)
    courtlistener_url = db.Column(db.String(1000))
    justia_url = db.Column(db.String(1000))
    pacer_url = db.Column(db.String(1000))

    # Fair use excerpt (ALLOWED - max 200 words)
    fair_use_excerpt = db.Column(db.Text)  # Must be <= 200 words
    excerpt_word_count = db.Column(db.Integer)
    fair_use_purpose = db.Column(db.String(200))  # "Legal argument in brief"

    # Our analysis/notes (ALLOWED - our original work)
    our_analysis = db.Column(db.Text)
    relevance_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def validate_excerpt_length(self):
        """Ensure fair use excerpt is within limits."""
        if self.fair_use_excerpt:
            word_count = len(self.fair_use_excerpt.split())
            self.excerpt_word_count = word_count
            if word_count > 200:
                raise ValueError(f"Fair use excerpt exceeds 200 words: {word_count}")


class PublicCaseData(db.Model):
    """
    Public domain case information - SAFE TO EXPORT.
    Pattern 2: Keep proprietary layers separate
    """

    __tablename__ = "public_case_data"

    id = db.Column(db.String(32), primary_key=True)  # UUID

    # Basic case information (all public domain)
    citation = db.Column(db.String(500), nullable=False, index=True)
    court = db.Column(db.String(200))
    date = db.Column(db.Date)
    docket_number = db.Column(db.String(100), index=True)
    parties = db.Column(db.Text)

    # Public domain text (from CourtListener, Justia, etc.)
    public_domain_text = db.Column(db.Text)  # Full opinion from public source
    public_source = db.Column(db.String(100))  # "CourtListener", "Justia"
    source_url = db.Column(db.String(1000))

    # Our original analysis (our work product)
    our_analysis = db.Column(db.Text)
    our_notes = db.Column(db.Text)
    relevance_score = db.Column(db.Integer)  # 1-10

    # Data source tracking
    data_source_id = db.Column(db.String(32), db.ForeignKey("data_sources.id"), index=True)
    data_source = db.relationship("DataSource", backref="cases")

    # Metadata
    added_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    citations = db.relationship("CitationMetadata", backref="case", lazy="dynamic")
    proprietary_data = db.relationship("ProprietarySourceData", backref="case", lazy="dynamic")

    def export_safe_dict(self):
        """Return only data safe for export (no proprietary content)."""
        return {
            "citation": self.citation,
            "court": self.court,
            "date": self.date.isoformat() if self.date else None,
            "docket_number": self.docket_number,
            "parties": self.parties,
            "public_domain_text": self.public_domain_text,
            "public_source": self.public_source,
            "source_url": self.source_url,
            "our_analysis": self.our_analysis,
            # NEVER include: westlaw_keycite, lexis_shepards, etc.
        }


class ProprietarySourceData(db.Model):
    """
    Proprietary legal database content - NEVER EXPORT.
    Pattern 2: Keep proprietary layers separate
    This data is for INTERNAL RESEARCH ONLY.
    """

    __tablename__ = "proprietary_source_data"

    id = db.Column(db.String(32), primary_key=True)  # UUID
    case_id = db.Column(
        db.String(32), db.ForeignKey("public_case_data.id"), nullable=False, index=True
    )

    # Source identification
    source = db.Column(db.String(50), nullable=False, index=True)  # westlaw, lexis, bloomberg

    # PROPRIETARY CONTENT - INTERNAL USE ONLY
    westlaw_keycite = db.Column(db.JSON)  # Treatment history, citing references
    westlaw_headnotes = db.Column(db.JSON)  # Editorial headnotes
    westlaw_synopsis = db.Column(db.Text)  # Editorial synopsis

    lexis_shepards = db.Column(db.JSON)  # Shepard's citator data
    lexis_headnotes = db.Column(db.JSON)  # Editorial headnotes
    lexis_summary = db.Column(db.Text)  # Editorial summary

    bloomberg_bcite = db.Column(db.JSON)  # BCite analysis

    # Research notes (our internal use)
    research_notes = db.Column(db.Text)
    internal_tags = db.Column(db.JSON)

    # Access metadata
    accessed_date = db.Column(db.DateTime, default=datetime.utcnow)
    accessed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    subscription_type = db.Column(db.String(50))  # "Westlaw Practitioner", etc.

    # CRITICAL FLAGS
    export_allowed = db.Column(db.Boolean, default=False, nullable=False)  # Always False
    internal_use_only = db.Column(db.Boolean, default=True, nullable=False)  # Always True

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force these values to protect against accidental export
        self.export_allowed = False
        self.internal_use_only = True

    def to_dict(self, include_proprietary=False):
        """
        Return dictionary representation.
        Only include proprietary data if explicitly requested and user has permission.
        """
        if not include_proprietary:
            return {
                "id": self.id,
                "source": self.source,
                "warning": "PROPRIETARY DATA - Access restricted",
                "export_allowed": False,
            }

        return {
            "id": self.id,
            "case_id": self.case_id,
            "source": self.source,
            "westlaw_keycite": self.westlaw_keycite,
            "westlaw_headnotes": self.westlaw_headnotes,
            "lexis_shepards": self.lexis_shepards,
            "lexis_headnotes": self.lexis_headnotes,
            "research_notes": self.research_notes,
            "warning": "PROPRIETARY DATA - DO NOT EXPORT OR SHARE",
        }


class ExportManifest(db.Model):
    """
    Track all exports with rights validation and attribution.
    Pattern 3: Rights-aware exports
    """

    __tablename__ = "export_manifests"

    id = db.Column(db.String(32), primary_key=True)  # Export UUID

    # Export metadata
    case_number = db.Column(db.String(100), nullable=False, index=True)
    export_type = db.Column(db.String(50))  # discovery_production, court_filing, etc.
    export_format = db.Column(db.String(20))  # pdf, docx, zip

    # Materials inventory (JSON)
    materials_included = db.Column(db.JSON)  # List of materials with rights info
    attribution_requirements = db.Column(db.JSON)  # List of attribution texts
    excluded_materials = db.Column(db.JSON)  # List of excluded items with reasons

    # Certification
    certifying_attorney = db.Column(db.String(200), nullable=False)
    attorney_bar_number = db.Column(db.String(50))
    certification_date = db.Column(db.DateTime, default=datetime.utcnow)
    certification_statement = db.Column(db.Text)

    # Validation flags
    all_materials_permitted = db.Column(db.Boolean, nullable=False)
    has_proprietary_violations = db.Column(db.Boolean, default=False)
    copyright_compliance_verified = db.Column(db.Boolean, default=False)

    # Export paths
    export_directory = db.Column(db.String(500))
    manifest_file_path = db.Column(db.String(500))
    attribution_file_path = db.Column(db.String(500))

    # Audit trail
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "export_id": self.id,
            "case_number": self.case_number,
            "export_type": self.export_type,
            "certifying_attorney": self.certifying_attorney,
            "all_materials_permitted": self.all_materials_permitted,
            "materials_count": len(self.materials_included or []),
            "excluded_count": len(self.excluded_materials or []),
            "created_at": self.created_at.isoformat(),
        }


class MaterialInventory(db.Model):
    """
    Track individual materials/files with rights metadata.
    Used for export validation.
    """

    __tablename__ = "material_inventory"

    id = db.Column(db.String(32), primary_key=True)  # UUID

    # File information
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000))
    file_hash = db.Column(db.String(64), index=True)
    file_size = db.Column(db.BigInteger)
    category = db.Column(db.String(50))  # bwc_videos, transcripts, case_law, etc.

    # Rights metadata
    data_source_id = db.Column(db.String(32), db.ForeignKey("data_sources.id"), nullable=False)
    data_source = db.relationship("DataSource", backref="materials")

    # Content type
    is_excerpt = db.Column(db.Boolean, default=False)
    excerpt_word_count = db.Column(db.Integer)
    content_preview = db.Column(db.Text)  # First 500 chars for verification

    # Acquisition tracking
    acquired_by = db.Column(db.String(200))
    acquired_date = db.Column(db.DateTime)
    source_url = db.Column(db.String(1000))

    # Case association
    case_number = db.Column(db.String(100), index=True)
    analysis_id = db.Column(db.String(32), db.ForeignKey("analyses.id"), index=True)

    # Ownership
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def can_export(self):
        """Check if material can be included in exports."""
        if not self.data_source:
            return False

        if not self.data_source.export_allowed:
            return False

        if self.data_source.fair_use_only and not self.is_excerpt:
            return False

        if self.is_excerpt and self.excerpt_word_count:
            if self.excerpt_word_count > self.data_source.max_excerpt_words:
                return False

        return True

    def get_export_info(self):
        """Get export metadata for manifest."""
        return {
            "filename": self.filename,
            "category": self.category,
            "source": self.data_source.source_name if self.data_source else "Unknown",
            "rights": self.data_source.license if self.data_source else "Unknown",
            "acquired_by": self.acquired_by,
            "acquired_date": self.acquired_date.isoformat() if self.acquired_date else None,
            "file_hash": self.file_hash,
            "export_allowed": self.can_export(),
        }


# Initialize tables
def init_data_rights_tables():
    """Create data rights tables if they don't exist."""
    with app.app_context():
        db.create_all()
        print("✅ Data rights compliance tables created")


if __name__ == "__main__":
    from app import app

    init_data_rights_tables()


