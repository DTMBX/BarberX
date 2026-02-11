"""
Review Models — Phase 10 Search & Review Platform
===================================================
Models for document review decisions, annotations, saved searches,
and review audit trail.

Design principles:
  - Review decisions are append-only (history preserved).
  - Annotations are non-destructive (stored separately from originals).
  - Every action is attributable and timestamped.
  - Tenant isolation via case_id → organization_id chain.
"""

import json
from datetime import datetime, timezone
from auth.models import db


# ---------------------------------------------------------------------------
# Review codes (enum-like constants)
# ---------------------------------------------------------------------------

class ReviewCode:
    """Standard review codes for e-discovery / document review."""
    RESPONSIVE = "responsive"
    NON_RESPONSIVE = "non_responsive"
    PRIVILEGED = "privileged"
    HOT = "hot"
    IRRELEVANT = "irrelevant"

    ALL = [RESPONSIVE, NON_RESPONSIVE, PRIVILEGED, HOT, IRRELEVANT]


# ---------------------------------------------------------------------------
# ReviewDecision — coding a document
# ---------------------------------------------------------------------------

class ReviewDecision(db.Model):
    """
    Stores a reviewer's coding decision on an evidence item within a case.

    Append-only: changing a code creates a new row (previous rows remain
    for audit). The 'is_current' flag marks the active decision.
    """
    __tablename__ = "review_decision"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence_item.id"), nullable=False, index=True)

    # Review code
    review_code = db.Column(db.String(50), nullable=False)  # One of ReviewCode constants
    confidence = db.Column(db.String(20), default="confirmed")  # confirmed, tentative

    # Reviewer
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    reviewer_note = db.Column(db.Text)  # Optional note explaining the decision

    # History tracking
    is_current = db.Column(db.Boolean, default=True, nullable=False, index=True)
    superseded_by_id = db.Column(db.Integer, db.ForeignKey("review_decision.id"), nullable=True)

    # Batch reference (tracks if this was applied as part of a batch action)
    batch_action_id = db.Column(db.String(36), nullable=True, index=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    reviewer = db.relationship("User", foreign_keys=[reviewer_id])
    superseded_by = db.relationship("ReviewDecision", remote_side=[id])

    __table_args__ = (
        db.Index("ix_review_decision_lookup", "case_id", "evidence_id", "is_current"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "review_code": self.review_code,
            "confidence": self.confidence,
            "reviewer_id": self.reviewer_id,
            "reviewer_note": self.reviewer_note,
            "is_current": self.is_current,
            "batch_action_id": self.batch_action_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ReviewDecision evidence={self.evidence_id} code={self.review_code}>"


# ---------------------------------------------------------------------------
# ReviewAnnotation — non-destructive sticky notes
# ---------------------------------------------------------------------------

class ReviewAnnotation(db.Model):
    """
    Non-destructive annotation on an evidence item.

    Stored separately from the evidence — never modifies the original.
    Supports positional anchoring (page + coordinates for PDFs/images).
    """
    __tablename__ = "review_annotation"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence_item.id"), nullable=False, index=True)

    # Content
    content = db.Column(db.Text, nullable=False)
    annotation_type = db.Column(db.String(30), default="note")  # note, highlight, flag

    # Positional anchoring (optional — for page-level annotations)
    page_number = db.Column(db.Integer, nullable=True)
    x_position = db.Column(db.Float, nullable=True)  # 0-1 normalized
    y_position = db.Column(db.Float, nullable=True)  # 0-1 normalized

    # Color / style
    color = db.Column(db.String(7), default="#fbbf24")  # Hex color (amber default)

    # Author
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    author = db.relationship("User", foreign_keys=[author_id])

    __table_args__ = (
        db.Index("ix_review_annotation_lookup", "case_id", "evidence_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "content": self.content,
            "annotation_type": self.annotation_type,
            "page_number": self.page_number,
            "x_position": self.x_position,
            "y_position": self.y_position,
            "color": self.color,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ReviewAnnotation evidence={self.evidence_id} type={self.annotation_type}>"


# ---------------------------------------------------------------------------
# SavedSearch — persisted search queries
# ---------------------------------------------------------------------------

class SavedSearch(db.Model):
    """
    Persists a search query with filters for reuse.
    """
    __tablename__ = "saved_search"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    name = db.Column(db.String(200), nullable=False)
    query_text = db.Column(db.String(500))
    filters_json = db.Column(db.Text)  # JSON: {file_type, date_from, date_to, has_ocr, ...}

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])

    @property
    def filters(self):
        if self.filters_json:
            try:
                return json.loads(self.filters_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @filters.setter
    def filters(self, value):
        self.filters_json = json.dumps(value, default=str) if value else None

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "name": self.name,
            "query_text": self.query_text,
            "filters": self.filters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<SavedSearch '{self.name}'>"


# ---------------------------------------------------------------------------
# ReviewAuditEvent — fine-grained review action log
# ---------------------------------------------------------------------------

class ReviewAuditEvent(db.Model):
    """
    Append-only log of every review action.
    Complements ChainOfCustody with review-specific granularity.
    """
    __tablename__ = "review_audit_event"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence_item.id"), nullable=True, index=True)

    # Action
    action = db.Column(db.String(80), nullable=False)  # review.coded, review.tag_applied, etc.
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Details (JSON)
    details_json = db.Column(db.Text)

    # Request context
    ip_address = db.Column(db.String(45))

    # Timestamp
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    actor = db.relationship("User", foreign_keys=[actor_id])

    @property
    def details(self):
        if self.details_json:
            try:
                return json.loads(self.details_json)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ReviewAuditEvent {self.action}>"
