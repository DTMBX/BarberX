"""
Algorithm Models
=================
Database models for algorithm run tracking, provenance edges,
verification reports, and redaction reports.

All tables reference the shared `db` from auth.models to maintain
a single SQLAlchemy session and migration chain.
"""

import json
from datetime import datetime, timezone
from auth.models import db


class AlgorithmRun(db.Model):
    """
    Persistent record of every algorithm execution.

    Stores full provenance metadata for reproducibility and court defensibility.
    Each run is immutable once written — no updates, no deletes.
    """
    __tablename__ = "algorithm_run"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUIDv4

    # Algorithm identity
    algorithm_id = db.Column(db.String(100), nullable=False, index=True)
    algorithm_version = db.Column(db.String(20), nullable=False)

    # Context
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, nullable=False, index=True)  # organization_id
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Status
    success = db.Column(db.Boolean, nullable=False, default=True)
    error_message = db.Column(db.Text, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)

    # Integrity
    params_hash = db.Column(db.String(64), nullable=True)
    result_hash = db.Column(db.String(64), nullable=True)
    integrity_check = db.Column(db.String(64), nullable=True)

    # Provenance data (JSON)
    input_hashes_json = db.Column(db.Text, nullable=True)
    output_hashes_json = db.Column(db.Text, nullable=True)
    payload_json = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    case = db.relationship("LegalCase", backref=db.backref("algorithm_runs", lazy="dynamic"))
    actor = db.relationship("User", foreign_keys=[actor_id])

    __table_args__ = (
        db.Index("ix_algorithm_run_case_algo", "case_id", "algorithm_id"),
        db.Index("ix_algorithm_run_created", "created_at"),
    )

    def __repr__(self):
        return f"<AlgorithmRun {self.algorithm_id} v{self.algorithm_version} run={self.run_id[:8]}>"


class ProvenanceEdge(db.Model):
    """
    Directed edge in the evidence provenance graph.

    source_hash → target_hash via a transformation.
    Immutable once written.
    """
    __tablename__ = "provenance_edge"

    id = db.Column(db.Integer, primary_key=True)
    source_hash = db.Column(db.String(64), nullable=False, index=True)
    target_hash = db.Column(db.String(64), nullable=False, index=True)
    transformation = db.Column(db.String(100), nullable=False)

    # Which algorithm produced this edge
    algorithm_id = db.Column(db.String(100), nullable=False)
    algorithm_version = db.Column(db.String(20), nullable=False)
    run_id = db.Column(db.String(36), db.ForeignKey("algorithm_run.run_id"), nullable=True)

    # Context
    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=True, index=True)
    parameters_json = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        db.Index("ix_provenance_edge_source", "source_hash"),
        db.Index("ix_provenance_edge_target", "target_hash"),
        db.Index("ix_provenance_edge_case", "case_id"),
    )

    def __repr__(self):
        return f"<ProvenanceEdge {self.source_hash[:8]}→{self.target_hash[:8]} via {self.transformation}>"


class VerificationReport(db.Model):
    """
    Integrity verification report for a case.

    Stores the full JSON report and its SHA-256 for court reference.
    """
    __tablename__ = "verification_report"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(36), db.ForeignKey("algorithm_run.run_id"), nullable=False, index=True)

    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, nullable=False)

    # Results
    total_items = db.Column(db.Integer, nullable=False, default=0)
    items_passed = db.Column(db.Integer, nullable=False, default=0)
    items_failed = db.Column(db.Integer, nullable=False, default=0)
    items_missing = db.Column(db.Integer, nullable=False, default=0)
    items_error = db.Column(db.Integer, nullable=False, default=0)
    all_passed = db.Column(db.Boolean, nullable=False, default=False)

    # Full report (deterministic JSON)
    report_json = db.Column(db.Text, nullable=True)
    report_hash = db.Column(db.String(64), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    __table_args__ = (
        db.Index("ix_verification_report_case", "case_id"),
    )

    def __repr__(self):
        return f"<VerificationReport case={self.case_id} passed={self.all_passed}>"


class RedactionReport(db.Model):
    """
    Redaction verification report for a case.

    Stores per-item redaction check results and overall status.
    """
    __tablename__ = "redaction_report"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(36), db.ForeignKey("algorithm_run.run_id"), nullable=False, index=True)

    case_id = db.Column(db.Integer, db.ForeignKey("legal_case.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, nullable=False)

    # Results
    total_checked = db.Column(db.Integer, nullable=False, default=0)
    items_passed = db.Column(db.Integer, nullable=False, default=0)
    items_failed = db.Column(db.Integer, nullable=False, default=0)
    items_warning = db.Column(db.Integer, nullable=False, default=0)
    items_skipped = db.Column(db.Integer, nullable=False, default=0)

    # Full report
    report_json = db.Column(db.Text, nullable=True)
    report_hash = db.Column(db.String(64), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    __table_args__ = (
        db.Index("ix_redaction_report_case", "case_id"),
    )

    def __repr__(self):
        return f"<RedactionReport case={self.case_id} checked={self.total_checked}>"
