"""
Public Transparency Report Endpoint
=====================================
Unauthenticated endpoint that returns aggregate, public-safe statistics.

Returns COUNTS ONLY — no evidence content, no case details, no PII.

This endpoint is designed for:
  - Public accountability dashboards
  - Compliance attestation
  - Third-party auditor verification

Design principles:
  - No evidence bytes, filenames, or hashes are exposed.
  - No user identities are exposed.
  - No case numbers or names are exposed.
  - Only aggregate counts and system health metrics.
"""

import os
from datetime import datetime, timezone

from flask import Blueprint, jsonify

transparency_bp = Blueprint("transparency", __name__, url_prefix="/transparency")


@transparency_bp.route("/report", methods=["GET"])
def public_report():
    """
    Public transparency report — aggregate counts only.

    No authentication required. Safe for public consumption.
    """
    from auth.models import db
    from models.evidence import ChainOfCustody, EvidenceItem
    from models.legal_case import LegalCase

    now = datetime.now(timezone.utc)

    # Aggregate counts only — no row-level data
    total_cases = db.session.query(db.func.count(LegalCase.id)).scalar() or 0
    total_evidence_items = db.session.query(db.func.count(EvidenceItem.id)).scalar() or 0
    total_audit_entries = db.session.query(db.func.count(ChainOfCustody.id)).scalar() or 0

    # Evidence type distribution (counts only)
    type_counts = (
        db.session.query(
            EvidenceItem.evidence_type,
            db.func.count(EvidenceItem.id),
        )
        .group_by(EvidenceItem.evidence_type)
        .all()
    )

    # Audit action distribution (counts only)
    action_counts = (
        db.session.query(
            ChainOfCustody.action,
            db.func.count(ChainOfCustody.id),
        )
        .group_by(ChainOfCustody.action)
        .all()
    )

    # Version
    version = "unknown"
    try:
        version_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "VERSION"
        )
        with open(version_path, "r", encoding="utf-8") as fh:
            version = fh.read().strip()
    except OSError:
        pass

    return jsonify({
        "report_type": "public_transparency",
        "generated_at": now.isoformat(),
        "version": version,
        "aggregate_counts": {
            "cases": total_cases,
            "evidence_items": total_evidence_items,
            "audit_entries": total_audit_entries,
        },
        "evidence_type_distribution": {
            etype: count for etype, count in type_counts if etype
        },
        "audit_action_distribution": {
            action: count for action, count in action_counts if action
        },
        "notice": (
            "This report contains aggregate counts only. "
            "No case details, evidence content, user identities, "
            "or personally identifiable information is disclosed. "
            "For verification instructions, see /transparency/verify."
        ),
    }), 200


@transparency_bp.route("/verify", methods=["GET"])
def verification_instructions():
    """
    Public verification instructions — how to independently verify
    evidence integrity without accessing the evidence itself.
    """
    return jsonify({
        "title": "Evidence Integrity Verification Instructions",
        "instructions": [
            {
                "step": 1,
                "description": "Obtain the SHA-256 hash of the evidence item from the court package INDEX.json or the Integrity Statement.",
            },
            {
                "step": 2,
                "description": "Independently compute SHA-256 of the original file using any standard tool (e.g., sha256sum on Linux, Get-FileHash on Windows, shasum -a 256 on macOS).",
            },
            {
                "step": 3,
                "description": "Compare the two hashes. If they match exactly, the file has not been modified since ingest.",
            },
            {
                "step": 4,
                "description": "Verify the chain of custody by reviewing the ChainOfCustody entries in the export manifest JSON. Each entry records the action, actor, timestamp, and hash before/after.",
            },
            {
                "step": 5,
                "description": "Verify the court package integrity by computing SHA-256 of INDEX.json and comparing it to the value recorded in PACKAGE_HASH.txt.",
            },
        ],
        "tools": {
            "linux": "sha256sum <filename>",
            "macos": "shasum -a 256 <filename>",
            "windows": "Get-FileHash -Algorithm SHA256 <filename>",
            "python": "python -c \"import hashlib, sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())\" <filename>",
        },
        "notice": (
            "These instructions are provided for informational purposes. "
            "They do not constitute legal advice. Independent forensic "
            "verification should be conducted by a qualified examiner."
        ),
    }), 200
