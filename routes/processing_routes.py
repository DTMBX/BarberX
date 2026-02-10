"""
Processing Routes — API endpoints for evidence processing and search.
======================================================================
Blueprint: processing_bp, mounted at /api/v1/ (shares prefix with api_v1_bp).

Endpoints:
  POST /api/v1/evidence/<id>/process   — Trigger processing for evidence item
  GET  /api/v1/evidence/<id>/text      — Get extracted text for evidence
  GET  /api/v1/tasks/<id>              — Poll processing task status
  POST /api/v1/cases/<id>/process-all  — Batch-process all evidence in a case
  GET  /api/v1/batches/<id>            — Poll batch status
  GET  /api/v1/search                  — Full-text search across case evidence

All endpoints require Bearer token authentication.
"""

import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from auth.api_auth import api_token_required

processing_bp = Blueprint("processing", __name__, url_prefix="/api/v1")


# ---------------------------------------------------------------------------
# POST /api/v1/evidence/<id>/process
# ---------------------------------------------------------------------------

@processing_bp.route("/evidence/<int:evidence_id>/process", methods=["POST"])
@api_token_required
def trigger_processing(evidence_id):
    """
    Trigger processing for a single evidence item.

    Body (optional JSON):
      { "generate_proxy": false }

    Returns 202 with task info on success.
    """
    from models.evidence import EvidenceItem

    evidence = EvidenceItem.query.get(evidence_id)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404

    body = request.get_json(silent=True) or {}
    generate_proxy = body.get("generate_proxy", False)

    from tasks.processing_tasks import dispatch_process_evidence

    result = dispatch_process_evidence(
        evidence_id=evidence_id,
        user_id=g.api_user.id,
        generate_proxy=generate_proxy,
    )

    if result.get("async"):
        return jsonify({
            "status": "queued",
            "celery_task_id": result.get("celery_task_id"),
            "message": "Processing queued for async execution",
        }), 202

    if result.get("success"):
        return jsonify({
            "status": "completed",
            "task_id": result.get("task_id"),
            "task_uuid": result.get("task_uuid"),
            "task_type": result.get("task_type"),
            "summary": result.get("summary"),
            "processing_seconds": result.get("processing_seconds"),
        }), 200
    else:
        status_code = 422 if "unsupported" in (result.get("task_type") or "") else 500
        return jsonify({
            "status": "failed",
            "task_id": result.get("task_id"),
            "error": result.get("error"),
        }), status_code


# ---------------------------------------------------------------------------
# GET /api/v1/evidence/<id>/text
# ---------------------------------------------------------------------------

@processing_bp.route("/evidence/<int:evidence_id>/text", methods=["GET"])
@api_token_required
def get_evidence_text(evidence_id):
    """
    Return extracted text and metadata for an evidence item.

    Returns JSON with full_text, word_count, page_count, etc.
    """
    from models.evidence import EvidenceItem
    from models.document_processing import ContentExtractionIndex, OCRResult

    evidence = EvidenceItem.query.get(evidence_id)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404

    # Check ContentExtractionIndex first
    index = ContentExtractionIndex.query.filter_by(evidence_id=evidence_id).first()

    if not index:
        # Check if evidence has inline text
        if evidence.text_content:
            return jsonify({
                "evidence_id": evidence_id,
                "full_text": evidence.text_content,
                "word_count": len(evidence.text_content.split()),
                "source": "evidence_item",
                "processing_status": evidence.processing_status,
            }), 200

        return jsonify({
            "evidence_id": evidence_id,
            "processing_status": evidence.processing_status or "pending",
            "message": "No extracted text available. Trigger processing first.",
        }), 404

    response = {
        "evidence_id": evidence_id,
        "content_type": index.content_type,
        "full_text": index.full_text,
        "word_count": index.word_count,
        "character_count": index.character_count,
        "page_count": index.line_count,
        "email_addresses": index.email_addresses.split(",") if index.email_addresses else [],
        "phone_numbers": index.phone_numbers.split(",") if index.phone_numbers else [],
        "is_indexed": index.is_indexed,
        "processing_status": evidence.processing_status,
    }

    # Include OCR confidence if available
    ocr = OCRResult.query.filter_by(evidence_id=evidence_id).first()
    if ocr:
        response["ocr_confidence"] = ocr.average_confidence

    return jsonify(response), 200


# ---------------------------------------------------------------------------
# GET /api/v1/tasks/<id>
# ---------------------------------------------------------------------------

@processing_bp.route("/tasks/<int:task_id>", methods=["GET"])
@api_token_required
def get_task_status(task_id):
    """
    Poll processing task status.

    Returns JSON with status, progress, and error details.
    """
    from models.document_processing import DocumentProcessingTask

    task = DocumentProcessingTask.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    response = {
        "task_id": task.id,
        "task_uuid": task.task_uuid,
        "task_type": task.task_type,
        "status": task.status,
        "evidence_id": task.evidence_id,
        "case_id": task.case_id,
        "processing_engine": task.processing_engine,
        "error_message": task.error_message,
        "processing_time_seconds": task.processing_time_seconds,
        "queued_at": task.queued_at.isoformat() if task.queued_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }

    return jsonify(response), 200


# ---------------------------------------------------------------------------
# POST /api/v1/cases/<id>/process-all
# ---------------------------------------------------------------------------

@processing_bp.route("/cases/<int:case_id>/process-all", methods=["POST"])
@api_token_required
def trigger_batch_processing(case_id):
    """
    Batch-process all unprocessed evidence in a case.

    Returns 202 with batch info.
    """
    from models.legal_case import LegalCase

    case = LegalCase.query.get(case_id)
    if not case:
        return jsonify({"error": "Case not found"}), 404

    from tasks.processing_tasks import dispatch_process_case

    result = dispatch_process_case(
        case_id=case_id,
        user_id=g.api_user.id,
    )

    if result.get("async"):
        return jsonify({
            "status": "queued",
            "celery_task_id": result.get("celery_task_id"),
            "message": "Batch processing queued",
        }), 202

    if result.get("success"):
        return jsonify({
            "status": "completed",
            "batch_id": result.get("batch_id"),
            "batch_uuid": result.get("batch_uuid"),
            "total": result.get("total"),
            "completed": result.get("completed"),
            "failed": result.get("failed"),
        }), 200
    else:
        return jsonify({
            "status": "failed",
            "error": result.get("error"),
        }), 500


# ---------------------------------------------------------------------------
# GET /api/v1/batches/<id>
# ---------------------------------------------------------------------------

@processing_bp.route("/batches/<int:batch_id>", methods=["GET"])
@api_token_required
def get_batch_status(batch_id):
    """
    Poll batch processing status.
    """
    from models.document_processing import BatchProcessingQueue

    batch = BatchProcessingQueue.query.get(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    return jsonify({
        "batch_id": batch.id,
        "batch_uuid": batch.batch_uuid,
        "batch_name": batch.batch_name,
        "status": batch.status,
        "progress_percentage": batch.progress_percentage,
        "document_count": batch.document_count,
        "successful_count": batch.successful_count,
        "failed_count": batch.failed_count,
        "started_at": batch.started_at.isoformat() if batch.started_at else None,
        "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
    }), 200


# ---------------------------------------------------------------------------
# GET /api/v1/search
# ---------------------------------------------------------------------------

@processing_bp.route("/search", methods=["GET"])
@api_token_required
def search_evidence():
    """
    Full-text search across indexed evidence in a case.

    Query params:
      q        — search term (required)
      case_id  — case to search within (required)
      limit    — max results (default 50, max 100)

    Returns JSON with matching evidence IDs and text snippets.
    """
    query_text = request.args.get("q", "").strip()
    case_id = request.args.get("case_id", type=int)
    limit = min(request.args.get("limit", 50, type=int), 100)

    if not query_text:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    if not case_id:
        return jsonify({"error": "Query parameter 'case_id' is required"}), 400

    from models.document_processing import ContentExtractionIndex
    from models.evidence import EvidenceItem

    # ILIKE search across full_text, persons, organizations
    keyword_filter = f"%{query_text}%"
    results = ContentExtractionIndex.query.filter(
        ContentExtractionIndex.case_id == case_id,
        (
            ContentExtractionIndex.full_text.ilike(keyword_filter) |
            ContentExtractionIndex.persons.ilike(keyword_filter) |
            ContentExtractionIndex.organizations.ilike(keyword_filter) |
            ContentExtractionIndex.email_addresses.ilike(keyword_filter) |
            ContentExtractionIndex.phone_numbers.ilike(keyword_filter)
        ),
    ).limit(limit).all()

    matches = []
    for idx in results:
        evidence = EvidenceItem.query.get(idx.evidence_id)
        if not evidence:
            continue

        # Generate snippet around the search term
        snippet = _extract_snippet(idx.full_text or "", query_text)

        matches.append({
            "evidence_id": idx.evidence_id,
            "original_filename": evidence.original_filename,
            "content_type": idx.content_type,
            "word_count": idx.word_count,
            "snippet": snippet,
        })

    return jsonify({
        "query": query_text,
        "case_id": case_id,
        "total_results": len(matches),
        "results": matches,
    }), 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_snippet(text: str, query: str, context_chars: int = 150) -> str:
    """
    Extract a snippet of text around the first occurrence of the query term.
    """
    if not text or not query:
        return ""

    lower_text = text.lower()
    lower_query = query.lower()
    pos = lower_text.find(lower_query)

    if pos == -1:
        # Return first N characters as fallback
        return text[:context_chars * 2] + ("..." if len(text) > context_chars * 2 else "")

    start = max(0, pos - context_chars)
    end = min(len(text), pos + len(query) + context_chars)

    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet
