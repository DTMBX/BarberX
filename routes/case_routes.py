"""
Evident Case Management Routes
===============================
CRUD for cases, batch evidence linking, case dashboard.

Design principles:
  - Cases are first-class entities — not UI-only groupings.
  - Evidence is linked, never copied.
  - All membership changes produce audit entries.
  - No legal conclusions are emitted by any endpoint.
"""

import json
import logging
from datetime import datetime, timezone

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)
from flask_login import current_user, login_required

from auth.models import db
from models.evidence import CaseEvidence, EvidenceItem
from models.legal_case import LegalCase
from services.audit_stream import AuditAction, AuditStream
from services.evidence_store import EvidenceStore

logger = logging.getLogger(__name__)

case_bp = Blueprint("cases", __name__, url_prefix="/cases")

_evidence_store = EvidenceStore(root="evidence_store")


# ============================================================================
# Case CRUD
# ============================================================================


@case_bp.route("/", methods=["GET"])
@login_required
def case_list():
    """List all cases accessible to the current user."""
    cases = LegalCase.query.order_by(LegalCase.created_at.desc()).all()
    if request.accept_mimetypes.best == "application/json":
        return jsonify([_case_summary(c) for c in cases])
    return render_template("cases/list.html", cases=cases, user=current_user)


@case_bp.route("/create", methods=["GET", "POST"])
@login_required
def case_create():
    """Create a new case."""
    if request.method == "GET":
        return render_template("cases/create.html", user=current_user)

    # Accept both form-encoded and JSON
    data = request.json if request.is_json else request.form

    case_number = (data.get("case_number") or "").strip()
    case_name = (data.get("case_name") or "").strip()
    case_type = (data.get("case_type") or "criminal").strip()

    if not case_number or not case_name:
        return jsonify({"error": "case_number and case_name are required"}), 400

    # Check uniqueness
    if LegalCase.query.filter_by(case_number=case_number).first():
        return jsonify({"error": f"Case number '{case_number}' already exists"}), 409

    case = LegalCase(
        case_number=case_number,
        case_name=case_name,
        case_type=case_type,
        description=data.get("description", ""),
        jurisdiction=data.get("jurisdiction"),
        jurisdiction_state=data.get("jurisdiction_state"),
        jurisdiction_agency_type=data.get("jurisdiction_agency_type"),
        retention_policy_ref=data.get("retention_policy_ref"),
        incident_number=data.get("incident_number"),
        court_name=data.get("court_name"),
        judge_name=data.get("judge_name"),
        status="open",
        created_by_id=current_user.id,
    )

    # Parse optional dates
    for date_field in ("filed_date", "incident_date", "discovery_deadline", "trial_date"):
        raw = data.get(date_field)
        if raw:
            try:
                setattr(case, date_field, datetime.fromisoformat(raw))
            except ValueError:
                pass

    db.session.add(case)
    db.session.commit()

    logger.info("Case created: %s (%s) by user %s", case.case_number, case.case_name, current_user.email)

    if request.is_json:
        return jsonify(_case_summary(case)), 201
    return render_template("cases/detail.html", case=case, user=current_user)


@case_bp.route("/<int:case_id>", methods=["GET"])
@login_required
def case_detail(case_id: int):
    """View case details with linked evidence summary."""
    case = LegalCase.query.get_or_404(case_id)
    linked_evidence = _get_linked_evidence(case_id)

    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            **_case_summary(case),
            "evidence": [_evidence_summary(e) for e in linked_evidence],
        })
    return render_template(
        "cases/detail.html",
        case=case,
        evidence_items=linked_evidence,
        user=current_user,
    )


@case_bp.route("/<int:case_id>", methods=["PATCH"])
@login_required
def case_update(case_id: int):
    """Update case metadata (no evidence mutation)."""
    case = LegalCase.query.get_or_404(case_id)
    data = request.json if request.is_json else request.form

    updatable = (
        "case_name", "case_type", "description", "jurisdiction",
        "jurisdiction_state", "jurisdiction_agency_type", "retention_policy_ref",
        "incident_number", "court_name", "judge_name", "status",
    )
    for field in updatable:
        val = data.get(field)
        if val is not None:
            setattr(case, field, val.strip() if isinstance(val, str) else val)

    db.session.commit()
    return jsonify(_case_summary(case))


# ============================================================================
# Evidence Linking
# ============================================================================


@case_bp.route("/<int:case_id>/link", methods=["POST"])
@login_required
def link_evidence(case_id: int):
    """
    Link one or more evidence items to a case.

    Body (JSON):
      { "evidence_ids": [1, 2, 3], "purpose": "discovery" }
    """
    case = LegalCase.query.get_or_404(case_id)
    data = request.json or {}
    evidence_ids = data.get("evidence_ids", [])
    purpose = data.get("purpose", "reference")

    if not evidence_ids:
        return jsonify({"error": "evidence_ids required"}), 400

    audit = AuditStream(db.session, _evidence_store)
    linked = []
    skipped = []

    for eid in evidence_ids:
        item = EvidenceItem.query.get(eid)
        if not item:
            skipped.append({"id": eid, "reason": "not found"})
            continue

        existing = CaseEvidence.query.filter_by(
            case_id=case_id, evidence_id=eid
        ).first()
        if existing and existing.is_active:
            skipped.append({"id": eid, "reason": "already linked"})
            continue

        link = CaseEvidence(
            case_id=case_id,
            evidence_id=eid,
            linked_by_id=current_user.id,
            link_purpose=purpose,
        )
        db.session.add(link)
        linked.append(eid)

        # Audit: case_link_added
        if item.evidence_store_id:
            audit.record(
                evidence_id=item.evidence_store_id,
                db_evidence_id=item.id,
                action="case_link_added",
                actor_id=current_user.id,
                actor_name=current_user.email,
                details={
                    "case_id": case_id,
                    "case_number": case.case_number,
                    "purpose": purpose,
                },
            )

    db.session.commit()

    return jsonify({
        "linked": linked,
        "skipped": skipped,
        "case_id": case_id,
    })


@case_bp.route("/<int:case_id>/unlink", methods=["POST"])
@login_required
def unlink_evidence(case_id: int):
    """
    Soft-unlink evidence from a case (append-only — row is preserved).

    Body (JSON): { "evidence_ids": [1, 2] }
    """
    data = request.json or {}
    evidence_ids = data.get("evidence_ids", [])
    unlinked = []

    audit = AuditStream(db.session, _evidence_store)

    for eid in evidence_ids:
        link = CaseEvidence.query.filter_by(
            case_id=case_id, evidence_id=eid
        ).first()
        if link and link.is_active:
            link.unlinked_at = datetime.now(timezone.utc)
            link.unlinked_by_id = current_user.id
            unlinked.append(eid)

            item = EvidenceItem.query.get(eid)
            if item and item.evidence_store_id:
                audit.record(
                    evidence_id=item.evidence_store_id,
                    db_evidence_id=item.id,
                    action="case_link_removed",
                    actor_id=current_user.id,
                    actor_name=current_user.email,
                    details={"case_id": case_id},
                )

    db.session.commit()
    return jsonify({"unlinked": unlinked, "case_id": case_id})


# ============================================================================
# Case-Scoped Export
# ============================================================================


@case_bp.route("/<int:case_id>/export", methods=["POST"])
@login_required
def export_case(case_id: int):
    """Generate a court-ready export for all evidence linked to a case."""
    from services.evidence_export import CaseExporter

    case = LegalCase.query.get_or_404(case_id)
    evidence_items = _get_linked_evidence(case_id)

    if not evidence_items:
        return jsonify({"error": "No evidence linked to this case"}), 400

    exporter = CaseExporter(_evidence_store, export_dir="exports")
    result = exporter.export_case(
        case=case,
        evidence_items=evidence_items,
        exported_by=current_user.email,
    )

    if not result.success:
        return jsonify({"error": result.error}), 500

    return jsonify(result.to_dict()), 200


# ============================================================================
# API helpers for case selector (used by upload UI)
# ============================================================================


@case_bp.route("/api/list", methods=["GET"])
@login_required
def api_case_list():
    """Return a lightweight list of cases for dropdowns and selectors."""
    cases = LegalCase.query.filter_by(status="open").order_by(LegalCase.case_name).all()
    return jsonify([
        {
            "id": c.id,
            "case_number": c.case_number,
            "case_name": c.case_name,
            "case_type": c.case_type,
        }
        for c in cases
    ])


# ============================================================================
# Helpers
# ============================================================================


def _case_summary(case: LegalCase) -> dict:
    """Serialize a case to a summary dict."""
    return {
        "id": case.id,
        "case_number": case.case_number,
        "case_name": case.case_name,
        "case_type": case.case_type,
        "description": case.description,
        "jurisdiction": case.jurisdiction,
        "jurisdiction_state": case.jurisdiction_state,
        "jurisdiction_agency_type": case.jurisdiction_agency_type,
        "incident_number": case.incident_number,
        "status": case.status,
        "evidence_count": case.evidence_count,
        "is_legal_hold": case.is_legal_hold,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }


def _evidence_summary(item: EvidenceItem) -> dict:
    """Serialize an evidence item to a summary dict."""
    return {
        "id": item.id,
        "original_filename": item.original_filename,
        "evidence_type": item.evidence_type,
        "hash_sha256": item.hash_sha256,
        "file_size_bytes": item.file_size_bytes,
        "processing_status": item.processing_status,
        "media_category": item.media_category,
        "device_label": item.device_label,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def _get_linked_evidence(case_id: int) -> list:
    """Return all actively linked EvidenceItems for a case."""
    links = CaseEvidence.query.filter_by(case_id=case_id).filter(
        CaseEvidence.unlinked_at.is_(None)
    ).all()
    return [link.evidence for link in links if link.evidence]
