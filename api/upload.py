# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Upload API Endpoints
Handles PDF and video file uploads with tier-based restrictions
"""

import os
from datetime import datetime
from pathlib import Path

from flask import current_app, jsonify, request
from tier_gating import check_tier_access, get_tier_limits
from werkzeug.utils import secure_filename

from api import upload_api
from api.auth import jwt_required

# Allowed file extensions
ALLOWED_PDF_EXTENSIONS = {"pdf"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}


def allowed_file(filename, allowed_extensions):
    """Check if filename has allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@upload_api.route("/pdf", methods=["POST"])
@jwt_required
def upload_pdf():
    """
    Upload PDF file

    POST /api/v1/upload/pdf
    Headers: Authorization: Bearer <token>
    Body: multipart/form-data with "file" field
    Returns: {"file_id": 123, "filename": "document.pdf", "size": 12345}
    """
    user = request.current_user

    # Check tier access
    if not check_tier_access(user.tier, "pdf_upload"):
        return jsonify({"error": "PDF upload not available on your tier"}), 403

    # Check if file is in request
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    if not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Check file size limits based on tier
    tier_limits = get_tier_limits(user.tier)
    max_file_size = tier_limits.get("max_file_size_mb", 10) * 1024 * 1024  # Convert to bytes

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > max_file_size:
        return (
            jsonify(
                {
                    "error": f"File size exceeds {tier_limits.get('max_file_size_mb')}MB limit for {user.tier} tier"
                }
            ),
            413,
        )

    # Secure filename and save
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{user.id}_{timestamp}_{filename}"

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"]) / "pdfs"
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / unique_filename
    file.save(str(file_path))

    # TODO: Save file metadata to database
    # For now, return mock response
    return (
        jsonify(
            {
                "file_id": 123,  # Replace with actual DB ID
                "filename": filename,
                "original_filename": file.filename,
                "size": file_size,
                "uploaded_at": datetime.utcnow().isoformat(),
                "path": str(file_path),
            }
        ),
        201,
    )


@upload_api.route("/video", methods=["POST"])
@jwt_required
def upload_video():
    """
    Upload video file (BWC footage)

    POST /api/v1/upload/video
    Headers: Authorization: Bearer <token>
    Body: multipart/form-data with "file" field
    Returns: {"file_id": 123, "filename": "footage.mp4", "size": 123456789}
    """
    user = request.current_user

    # Check tier access (video upload typically requires PRO+)
    if not check_tier_access(user.tier, "video_upload"):
        return jsonify({"error": "Video upload requires PRO tier or higher"}), 403

    # Check if file is in request
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file extension
    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({"error": "Invalid video format. Allowed: mp4, mov, avi, mkv, webm"}), 400

    # Check file size limits
    tier_limits = get_tier_limits(user.tier)
    max_file_size = tier_limits.get("max_video_size_gb", 1) * 1024 * 1024 * 1024  # Convert to bytes

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > max_file_size:
        return (
            jsonify(
                {
                    "error": f"Video size exceeds {tier_limits.get('max_video_size_gb')}GB limit for {user.tier} tier"
                }
            ),
            413,
        )

    # Secure filename and save
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{user.id}_{timestamp}_{filename}"

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"]) / "videos"
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / unique_filename
    file.save(str(file_path))

    # TODO: Save file metadata to database and queue for transcription
    return (
        jsonify(
            {
                "file_id": 456,  # Replace with actual DB ID
                "filename": filename,
                "original_filename": file.filename,
                "size": file_size,
                "uploaded_at": datetime.utcnow().isoformat(),
                "path": str(file_path),
                "status": "queued_for_transcription",
            }
        ),
        201,
    )


@upload_api.route("/status/<int:file_id>", methods=["GET"])
@jwt_required
def upload_status(file_id):
    """
    Get upload/processing status

    GET /api/v1/upload/status/<file_id>
    Headers: Authorization: Bearer <token>
    Returns: {"file_id": 123, "status": "processing", "progress": 45}
    """
    user = request.current_user

    # TODO: Query database for file status
    # Mock response for now
    return (
        jsonify(
            {
                "file_id": file_id,
                "status": "completed",
                "progress": 100,
                "message": "Upload completed successfully",
            }
        ),
        200,
    )
