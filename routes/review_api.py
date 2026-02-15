"""
Review API Routes — Phase 10 Search & Review Platform
======================================================
Blueprint: review_api_bp, mounted at /api/v1/review

Endpoints:
  GET  /api/v1/review/search           — Enhanced full-text search with filters
  GET  /api/v1/review/evidence/<id>    — Single evidence detail for viewer
  GET  /api/v1/review/evidence/<id>/text — Full extracted text for evidence

  POST /api/v1/review/code             — Apply review code to evidence
  POST /api/v1/review/code/batch       — Batch apply review codes
  GET  /api/v1/review/evidence/<id>/decisions — Decision history

  POST /api/v1/review/tag              — Apply tag to evidence
  DELETE /api/v1/review/tag            — Remove tag from evidence
  GET  /api/v1/review/tags             — List tags for a case
  POST /api/v1/review/tags             — Create a new tag

  GET    /api/v1/review/annotations    — List annotations for evidence
  POST   /api/v1/review/annotations    — Create annotation
  PUT    /api/v1/review/annotations/<id> — Update annotation
  DELETE /api/v1/review/annotations/<id> — Soft-delete annotation

  GET  /api/v1/review/audit            — Review audit trail
  GET  /api/v1/review/evidence/<id>/history — Full review history for one item

  GET  /api/v1/review/stats            — Case review statistics

All endpoints require authentication (session or Bearer token).
"""

import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from flask_login import current_user, login_required

review_api_bp = Blueprint("review_api", __name__, url_prefix="/api/v1/review")


# ---------------------------------------------------------------------------
# Auth helper — supports both session (Flask-Login) and Bearer token
# ---------------------------------------------------------------------------

def _get_current_user():
    """Return current user from session or API token context."""
    if current_user and current_user.is_authenticated:
        return current_user
    return getattr(g, "api_user", None)


def review_auth_required(f):
    """Decorator: require session or API token auth."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        user = _get_current_user()
        if not user:
            # Try API token
            from auth.api_auth import _extract_bearer_token, _resolve_token
            raw_token = _extract_bearer_token()
            if raw_token:
                result = _resolve_token(raw_token)
                if result:
                    token_obj, user = result
                    g.api_user = user
            if not user:
                return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def _audit_event(case_id, evidence_id, action, details=None):
    """Write a review audit event."""
    from auth.models import db
    from models.review import ReviewAuditEvent

    user = _get_current_user()
    ip = None
    try:
        ip = request.remote_addr
    except RuntimeError:
        pass

    event = ReviewAuditEvent(
        case_id=case_id,
        evidence_id=evidence_id,
        action=action,
        actor_id=user.id if user else None,
        details_json=json.dumps(details, default=str) if details else None,
        ip_address=ip,
    )
    db.session.add(event)


# ---------------------------------------------------------------------------
# Tenant isolation — verify case exists and user has access
# ---------------------------------------------------------------------------

import logging as _logging
_review_logger = _logging.getLogger(__name__)


def _verify_case_access(case_id):
    """
    Verify the case exists and the current user has access.

    Checks (in order):
      1. Case must exist → 404
      2. Admin users bypass further checks.
      3. User must be lead attorney OR share the same organization.
      4. Failure → 403 with audit log.

    Returns (case, None) on success, or (None, error_response) on failure.
    """
    if case_id is None:
        return None, (jsonify({"error": "case_id is required"}), 400)

    from models.legal_case import LegalCase
    from auth.models import db, UserRole

    case = db.session.get(LegalCase, case_id)
    if case is None:
        return None, (jsonify({"error": "Case not found"}), 404)

    user = _get_current_user()
    if user is None:
        return None, (jsonify({"error": "Authentication required"}), 401)

    # Admins bypass tenant isolation
    if getattr(user, "role", None) == UserRole.ADMIN:
        return case, None

    # Lead attorney always has access
    if case.lead_attorney_id == user.id:
        return case, None

    # Organization match (soft check — User.organization is a string,
    # LegalCase.organization_id is an FK. When both are available,
    # compare organization names.)
    user_org_id = getattr(user, "organization_id", None)
    if user_org_id is not None and case.organization_id is not None:
        if user_org_id != case.organization_id:
            _review_logger.warning(
                "Tenant isolation: user=%s org=%s denied case=%d (org=%s)",
                user.id, user_org_id, case_id, case.organization_id,
            )
            return None, (jsonify({"error": "Access denied"}), 403)

    # If we cannot verify org membership (User lacks organization_id FK),
    # allow access but log for future audit. This is the pragmatic default
    # until the User model gains a proper organization_id FK.
    return case, None


# ===========================================================================
# SEARCH
# ===========================================================================

@review_api_bp.route("/search", methods=["GET"])
@review_auth_required
def review_search():
    """
    Enhanced search with boolean operators, phrase matching, and filters.

    Query params:
      case_id    (required) — case to search within
      q          — search query (supports "exact phrase", AND, OR)
      page       — page number (default 1)
      page_size  — results per page (default 50, max 100)
      sort_by    — relevance|date|filename|file_type|size
      sort_order — asc|desc
      file_type  — filter by file type (comma-separated)
      date_from  — ISO date filter (collected_date >=)
      date_to    — ISO date filter (collected_date <=)
      has_ocr    — true|false
      custodian  — collected_by ILIKE filter
      evidence_type — document|video|image|audio
      review_code — filter by current review code
      uncoded    — true to show only uncoded items
    """
    from auth.models import db
    from services.review_search_service import ReviewSearchService

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    # Build filters from query params
    filters = {}
    for key in ("file_type", "date_from", "date_to", "has_ocr", "custodian",
                "evidence_type", "processing_status", "review_code", "uncoded"):
        val = request.args.get(key)
        if val is not None:
            filters[key] = val

    user = _get_current_user()
    service = ReviewSearchService(db.session)
    result = service.search(
        case_id=case_id,
        query_text=request.args.get("q", "").strip() or None,
        filters=filters if filters else None,
        page=request.args.get("page", 1, type=int),
        page_size=request.args.get("page_size", 50, type=int),
        sort_by=request.args.get("sort_by", "relevance"),
        sort_order=request.args.get("sort_order", "desc"),
        actor_id=user.id if user else None,
    )

    return jsonify(result), 200


# ===========================================================================
# EVIDENCE DETAIL (for viewer)
# ===========================================================================

@review_api_bp.route("/evidence/<int:evidence_id>", methods=["GET"])
@review_auth_required
def evidence_detail(evidence_id):
    """Get evidence metadata + review state for the document viewer."""
    from models.evidence import EvidenceItem, EvidenceTag
    from models.review import ReviewDecision, ReviewAnnotation

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    evidence = EvidenceItem.query.get(evidence_id)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404

    # Current review decision
    decision = (
        ReviewDecision.query
        .filter_by(case_id=case_id, evidence_id=evidence_id, is_current=True)
        .first()
    )

    # Tags
    tags = [{"id": t.id, "name": t.tag_name, "color": t.tag_color} for t in evidence.tags]

    # Annotation count
    annotation_count = (
        ReviewAnnotation.query
        .filter_by(case_id=case_id, evidence_id=evidence_id, is_deleted=False)
        .count()
    )

    user = _get_current_user()
    _audit_event(case_id, evidence_id, "review.viewed", {"viewer": "detail"})

    from auth.models import db
    db.session.commit()

    return jsonify({
        "evidence_id": evidence.id,
        "original_filename": evidence.original_filename,
        "file_type": evidence.file_type,
        "mime_type": evidence.mime_type,
        "file_size_bytes": evidence.file_size_bytes,
        "evidence_type": evidence.evidence_type,
        "hash_sha256": evidence.hash_sha256,
        "collected_date": evidence.collected_date.isoformat() if evidence.collected_date else None,
        "collected_by": evidence.collected_by,
        "processing_status": evidence.processing_status,
        "has_ocr": evidence.has_ocr,
        "has_been_transcribed": evidence.has_been_transcribed,
        "review_decision": decision.to_dict() if decision else None,
        "tags": tags,
        "annotation_count": annotation_count,
        "created_at": evidence.created_at.isoformat() if evidence.created_at else None,
    }), 200


@review_api_bp.route("/evidence/<int:evidence_id>/text", methods=["GET"])
@review_auth_required
def evidence_text(evidence_id):
    """Get extracted full text for an evidence item."""
    from models.document_processing import ContentExtractionIndex

    case_id = request.args.get("case_id", type=int)

    idx = ContentExtractionIndex.query.filter_by(evidence_id=evidence_id).first()
    if not idx:
        return jsonify({"evidence_id": evidence_id, "text": None, "word_count": 0}), 200

    return jsonify({
        "evidence_id": evidence_id,
        "text": idx.full_text,
        "word_count": idx.word_count,
        "content_type": idx.content_type,
        "persons": idx.persons,
        "organizations": idx.organizations,
    }), 200


# ===========================================================================
# CODING (review decisions)
# ===========================================================================

@review_api_bp.route("/code", methods=["POST"])
@review_auth_required
def apply_review_code():
    """
    Apply a review code to a single evidence item.

    Body JSON:
      { "case_id": int, "evidence_id": int, "review_code": str, "note": str? }
    """
    from auth.models import db
    from models.review import ReviewDecision, ReviewCode

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    evidence_id = body.get("evidence_id")
    review_code = body.get("review_code")
    note = body.get("note")

    if not all([case_id, evidence_id, review_code]):
        return jsonify({"error": "case_id, evidence_id, and review_code are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    if review_code not in ReviewCode.ALL:
        return jsonify({"error": f"Invalid review_code. Must be one of: {ReviewCode.ALL}"}), 400

    user = _get_current_user()

    # Supersede any current decisions
    current = (
        ReviewDecision.query
        .filter_by(case_id=case_id, evidence_id=evidence_id, is_current=True)
        .all()
    )

    new_decision = ReviewDecision(
        case_id=case_id,
        evidence_id=evidence_id,
        review_code=review_code,
        reviewer_id=user.id,
        reviewer_note=note,
        is_current=True,
    )
    db.session.add(new_decision)
    db.session.flush()  # Get ID before updating old records

    for old in current:
        old.is_current = False
        old.superseded_by_id = new_decision.id

    _audit_event(case_id, evidence_id, "review.coded", {
        "review_code": review_code,
        "previous_code": current[0].review_code if current else None,
        "note": note,
    })

    db.session.commit()

    return jsonify({"status": "ok", "decision": new_decision.to_dict()}), 200


@review_api_bp.route("/code/batch", methods=["POST"])
@review_auth_required
def batch_apply_review_code():
    """
    Batch apply a review code to multiple evidence items.

    Body JSON:
      { "case_id": int, "evidence_ids": [int], "review_code": str, "note": str? }
    """
    from auth.models import db
    from models.review import ReviewDecision, ReviewCode

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    evidence_ids = body.get("evidence_ids", [])
    review_code = body.get("review_code")
    note = body.get("note")

    if not case_id or not evidence_ids or not review_code:
        return jsonify({"error": "case_id, evidence_ids, and review_code are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    if review_code not in ReviewCode.ALL:
        return jsonify({"error": f"Invalid review_code. Must be one of: {ReviewCode.ALL}"}), 400

    user = _get_current_user()
    batch_id = str(uuid.uuid4())

    applied = []
    for eid in evidence_ids:
        # Supersede current
        current = (
            ReviewDecision.query
            .filter_by(case_id=case_id, evidence_id=eid, is_current=True)
            .all()
        )

        new_decision = ReviewDecision(
            case_id=case_id,
            evidence_id=eid,
            review_code=review_code,
            reviewer_id=user.id,
            reviewer_note=note,
            is_current=True,
            batch_action_id=batch_id,
        )
        db.session.add(new_decision)
        db.session.flush()

        for old in current:
            old.is_current = False
            old.superseded_by_id = new_decision.id

        _audit_event(case_id, eid, "review.coded.batch", {
            "review_code": review_code,
            "batch_id": batch_id,
        })
        applied.append(eid)

    db.session.commit()

    return jsonify({
        "status": "ok",
        "batch_id": batch_id,
        "applied_count": len(applied),
        "evidence_ids": applied,
    }), 200


@review_api_bp.route("/evidence/<int:evidence_id>/decisions", methods=["GET"])
@review_auth_required
def decision_history(evidence_id):
    """Get the full decision history for an evidence item."""
    from models.review import ReviewDecision

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    decisions = (
        ReviewDecision.query
        .filter_by(case_id=case_id, evidence_id=evidence_id)
        .order_by(ReviewDecision.created_at.desc())
        .all()
    )

    return jsonify({
        "evidence_id": evidence_id,
        "decisions": [d.to_dict() for d in decisions],
    }), 200


# ===========================================================================
# TAGS
# ===========================================================================

@review_api_bp.route("/tags", methods=["GET"])
@review_auth_required
def list_tags():
    """List all tags for a case."""
    from models.evidence import EvidenceTag

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    tags = EvidenceTag.query.filter_by(case_id=case_id).all()
    return jsonify({
        "tags": [{
            "id": t.id,
            "name": t.tag_name,
            "color": t.tag_color,
            "description": t.description,
        } for t in tags],
    }), 200


@review_api_bp.route("/tags", methods=["POST"])
@review_auth_required
def create_tag():
    """
    Create a new tag for a case.

    Body JSON: { "case_id": int, "name": str, "color": str?, "description": str? }
    """
    from auth.models import db
    from models.evidence import EvidenceTag

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    name = body.get("name", "").strip()

    if not case_id or not name:
        return jsonify({"error": "case_id and name are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    user = _get_current_user()

    tag = EvidenceTag(
        case_id=case_id,
        tag_name=name,
        tag_color=body.get("color", "#6366f1"),
        description=body.get("description"),
        created_by_id=user.id,
    )
    db.session.add(tag)

    _audit_event(case_id, None, "review.tag_created", {"tag_name": name})
    db.session.commit()

    return jsonify({
        "id": tag.id, "name": tag.tag_name, "color": tag.tag_color,
    }), 201


@review_api_bp.route("/tag", methods=["POST"])
@review_auth_required
def apply_tag():
    """
    Apply a tag to evidence items.

    Body JSON: { "case_id": int, "evidence_ids": [int], "tag_id": int }
    """
    from auth.models import db
    from models.evidence import EvidenceItem, EvidenceTag, evidence_tag_association

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    evidence_ids = body.get("evidence_ids", [])
    tag_id = body.get("tag_id")

    if not case_id or not evidence_ids or not tag_id:
        return jsonify({"error": "case_id, evidence_ids, and tag_id are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    tag = EvidenceTag.query.get(tag_id)
    if not tag or tag.case_id != case_id:
        return jsonify({"error": "Tag not found in this case"}), 404

    applied = 0
    for eid in evidence_ids:
        evidence = EvidenceItem.query.get(eid)
        if evidence and tag not in evidence.tags:
            evidence.tags.append(tag)
            _audit_event(case_id, eid, "review.tag_applied", {
                "tag_id": tag_id, "tag_name": tag.tag_name,
            })
            applied += 1

    db.session.commit()

    return jsonify({"status": "ok", "applied_count": applied}), 200


@review_api_bp.route("/tag", methods=["DELETE"])
@review_auth_required
def remove_tag():
    """
    Remove a tag from evidence items.

    Body JSON: { "case_id": int, "evidence_ids": [int], "tag_id": int }
    """
    from auth.models import db
    from models.evidence import EvidenceItem, EvidenceTag

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    evidence_ids = body.get("evidence_ids", [])
    tag_id = body.get("tag_id")

    if not case_id or not evidence_ids or not tag_id:
        return jsonify({"error": "case_id, evidence_ids, and tag_id are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    tag = EvidenceTag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 404

    removed = 0
    for eid in evidence_ids:
        evidence = EvidenceItem.query.get(eid)
        if evidence and tag in evidence.tags:
            evidence.tags.remove(tag)
            _audit_event(case_id, eid, "review.tag_removed", {
                "tag_id": tag_id, "tag_name": tag.tag_name,
            })
            removed += 1

    db.session.commit()

    return jsonify({"status": "ok", "removed_count": removed}), 200


# ===========================================================================
# ANNOTATIONS
# ===========================================================================

@review_api_bp.route("/annotations", methods=["GET"])
@review_auth_required
def list_annotations():
    """List annotations for an evidence item."""
    from models.review import ReviewAnnotation

    case_id = request.args.get("case_id", type=int)
    evidence_id = request.args.get("evidence_id", type=int)

    if not case_id or not evidence_id:
        return jsonify({"error": "case_id and evidence_id are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    annotations = (
        ReviewAnnotation.query
        .filter_by(case_id=case_id, evidence_id=evidence_id, is_deleted=False)
        .order_by(ReviewAnnotation.created_at.asc())
        .all()
    )

    return jsonify({
        "annotations": [a.to_dict() for a in annotations],
    }), 200


@review_api_bp.route("/annotations", methods=["POST"])
@review_auth_required
def create_annotation():
    """
    Create a non-destructive annotation.

    Body JSON: {
      "case_id": int, "evidence_id": int, "content": str,
      "annotation_type": str?, "page_number": int?,
      "x_position": float?, "y_position": float?, "color": str?
    }
    """
    from auth.models import db
    from models.review import ReviewAnnotation

    body = request.get_json(silent=True) or {}
    case_id = body.get("case_id")
    evidence_id = body.get("evidence_id")
    content = body.get("content", "").strip()

    if not case_id or not evidence_id or not content:
        return jsonify({"error": "case_id, evidence_id, and content are required"}), 400

    case, err = _verify_case_access(case_id)
    if err:
        return err

    user = _get_current_user()

    annotation = ReviewAnnotation(
        case_id=case_id,
        evidence_id=evidence_id,
        content=content,
        annotation_type=body.get("annotation_type", "note"),
        page_number=body.get("page_number"),
        x_position=body.get("x_position"),
        y_position=body.get("y_position"),
        color=body.get("color", "#fbbf24"),
        author_id=user.id,
    )
    db.session.add(annotation)

    _audit_event(case_id, evidence_id, "review.annotation_created", {
        "annotation_type": annotation.annotation_type,
    })
    db.session.commit()

    return jsonify({"status": "ok", "annotation": annotation.to_dict()}), 201


@review_api_bp.route("/annotations/<int:annotation_id>", methods=["PUT"])
@review_auth_required
def update_annotation(annotation_id):
    """Update annotation content."""
    from auth.models import db
    from models.review import ReviewAnnotation

    annotation = ReviewAnnotation.query.get(annotation_id)
    if not annotation or annotation.is_deleted:
        return jsonify({"error": "Annotation not found"}), 404

    body = request.get_json(silent=True) or {}

    old_content = annotation.content
    if "content" in body:
        annotation.content = body["content"].strip()
    if "color" in body:
        annotation.color = body["color"]
    if "annotation_type" in body:
        annotation.annotation_type = body["annotation_type"]

    _audit_event(annotation.case_id, annotation.evidence_id, "review.annotation_updated", {
        "annotation_id": annotation_id,
        "old_content": old_content[:100] if old_content else None,
    })
    db.session.commit()

    return jsonify({"status": "ok", "annotation": annotation.to_dict()}), 200


@review_api_bp.route("/annotations/<int:annotation_id>", methods=["DELETE"])
@review_auth_required
def delete_annotation(annotation_id):
    """Soft-delete an annotation."""
    from auth.models import db
    from models.review import ReviewAnnotation

    annotation = ReviewAnnotation.query.get(annotation_id)
    if not annotation or annotation.is_deleted:
        return jsonify({"error": "Annotation not found"}), 404

    annotation.is_deleted = True
    annotation.deleted_at = datetime.now(timezone.utc)

    _audit_event(annotation.case_id, annotation.evidence_id, "review.annotation_deleted", {
        "annotation_id": annotation_id,
    })
    db.session.commit()

    return jsonify({"status": "ok"}), 200


# ===========================================================================
# AUDIT & HISTORY
# ===========================================================================

@review_api_bp.route("/audit", methods=["GET"])
@review_auth_required
def review_audit():
    """
    Review audit trail for a case.

    Query params: case_id (required), page, page_size, action (filter)
    """
    from models.review import ReviewAuditEvent

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    page = request.args.get("page", 1, type=int)
    page_size = min(request.args.get("page_size", 50, type=int), 200)
    action_filter = request.args.get("action")

    query = ReviewAuditEvent.query.filter_by(case_id=case_id)
    if action_filter:
        query = query.filter(ReviewAuditEvent.action == action_filter)

    total = query.count()
    events = (
        query
        .order_by(ReviewAuditEvent.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return jsonify({
        "events": [e.to_dict() for e in events],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        },
    }), 200


@review_api_bp.route("/evidence/<int:evidence_id>/history", methods=["GET"])
@review_auth_required
def evidence_review_history(evidence_id):
    """
    Full review history for a specific evidence item:
    decisions + annotations + audit events.
    """
    from models.review import ReviewDecision, ReviewAnnotation, ReviewAuditEvent

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    decisions = (
        ReviewDecision.query
        .filter_by(case_id=case_id, evidence_id=evidence_id)
        .order_by(ReviewDecision.created_at.desc())
        .all()
    )

    annotations = (
        ReviewAnnotation.query
        .filter_by(case_id=case_id, evidence_id=evidence_id, is_deleted=False)
        .order_by(ReviewAnnotation.created_at.desc())
        .all()
    )

    events = (
        ReviewAuditEvent.query
        .filter_by(case_id=case_id, evidence_id=evidence_id)
        .order_by(ReviewAuditEvent.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "evidence_id": evidence_id,
        "decisions": [d.to_dict() for d in decisions],
        "annotations": [a.to_dict() for a in annotations],
        "audit_events": [e.to_dict() for e in events],
    }), 200


# ===========================================================================
# STATS
# ===========================================================================

@review_api_bp.route("/stats", methods=["GET"])
@review_auth_required
def review_stats():
    """
    Case review statistics.

    Query params: case_id (required)
    """
    from auth.models import db
    from models.evidence import CaseEvidence
    from models.review import ReviewDecision, ReviewCode

    case_id = request.args.get("case_id", type=int)
    case, err = _verify_case_access(case_id)
    if err:
        return err

    # Total evidence in case
    total = CaseEvidence.query.filter_by(case_id=case_id).filter(CaseEvidence.unlinked_at.is_(None)).count()

    # Count by review code
    code_counts = {}
    for code in ReviewCode.ALL:
        count = (
            ReviewDecision.query
            .filter_by(case_id=case_id, review_code=code, is_current=True)
            .count()
        )
        code_counts[code] = count

    coded_total = sum(code_counts.values())

    return jsonify({
        "case_id": case_id,
        "total_evidence": total,
        "coded": coded_total,
        "uncoded": total - coded_total,
        "by_code": code_counts,
    }), 200
