# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evidence API Endpoints
Handles evidence management, transcription, OCR processing
"""

from datetime import datetime

from flask import jsonify, request
from tier_gating import check_tier_access

from api import evidence_api
from api.auth import jwt_required


@evidence_api.route("/list", methods=["GET"])
@jwt_required
def list_evidence():
    """
    List all evidence files for current user

    GET /api/v1/evidence/list?page=1&limit=20
    Headers: Authorization: Bearer <token>
    Returns: {"evidence": [...], "total": 10}
    """
    user = request.current_user
    page = int(request.args.get("page", 1))
    limit = min(int(request.args.get("limit", 20)), 100)

    # TODO: Query database
    return jsonify({"evidence": [], "total": 0, "page": page, "limit": limit}), 200


@evidence_api.route("/<int:evidence_id>", methods=["GET"])
@jwt_required
def get_evidence(evidence_id):
    """
    Get evidence details

    GET /api/v1/evidence/<evidence_id>
    Headers: Authorization: Bearer <token>
    Returns: {"evidence": {...}}
    """
    user = request.current_user

    # TODO: Fetch from database, verify ownership
    return (
        jsonify(
            {
                "evidence": {
                    "id": evidence_id,
                    "type": "video",
                    "filename": "footage.mp4",
                    "size": 12345678,
                    "status": "processed",
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
            }
        ),
        200,
    )


@evidence_api.route("/<int:evidence_id>/transcribe", methods=["POST"])
@jwt_required
def transcribe_evidence(evidence_id):
    """
    Start transcription for video evidence

    POST /api/v1/evidence/<evidence_id>/transcribe
    Headers: Authorization: Bearer <token>
    Returns: {"job_id": "trans_123", "status": "queued"}
    """
    user = request.current_user

    if not check_tier_access(user.tier, "transcription"):
        return jsonify({"error": "Transcription requires PRO tier or higher"}), 403

    # TODO: Queue transcription job
    return (
        jsonify(
            {
                "job_id": f"trans_{evidence_id}",
                "evidence_id": evidence_id,
                "status": "queued",
                "started_at": datetime.utcnow().isoformat(),
            }
        ),
        202,
    )


@evidence_api.route("/<int:evidence_id>/ocr", methods=["POST"])
@jwt_required
def ocr_evidence(evidence_id):
    """
    Start OCR processing for PDF evidence

    POST /api/v1/evidence/<evidence_id>/ocr
    Headers: Authorization: Bearer <token>
    Returns: {"job_id": "ocr_123", "status": "queued"}
    """
    user = request.current_user

    if not check_tier_access(user.tier, "ocr"):
        return jsonify({"error": "OCR requires PRO tier or higher"}), 403

    # TODO: Queue OCR job
    return (
        jsonify(
            {
                "job_id": f"ocr_{evidence_id}",
                "evidence_id": evidence_id,
                "status": "queued",
                "started_at": datetime.utcnow().isoformat(),
            }
        ),
        202,
    )


@evidence_api.route("/<int:evidence_id>", methods=["DELETE"])
@jwt_required
def delete_evidence(evidence_id):
    """
    Delete evidence file

    DELETE /api/v1/evidence/<evidence_id>
    Headers: Authorization: Bearer <token>
    Returns: {"message": "Evidence deleted"}
    """
    user = request.current_user

    # TODO: Verify ownership and delete from storage + database
    return jsonify({"message": "Evidence deleted successfully"}), 200
