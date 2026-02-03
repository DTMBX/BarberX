"""
Unified Batch Upload Handler
Accepts mixed PDFs and BWC videos, separates them, and processes in parallel
"""

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

# Create blueprint
batch_upload_bp = Blueprint("batch_upload", __name__)

# Allowed extensions
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}

# File type categories
FILE_CATEGORIES = {
    "video": ALLOWED_VIDEO_EXTENSIONS,
    "pdf": ALLOWED_PDF_EXTENSIONS,
    "image": ALLOWED_IMAGE_EXTENSIONS,
}


def categorize_file(filename):
    """Determine file category based on extension"""
    ext = Path(filename).suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category

    return "unknown"


def calculate_file_hash(filepath, chunk_size=8192):
    """Calculate SHA-256 hash of file using streaming to avoid loading entire file into memory"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_video_file(file, user_id=None):
    """Process BWC video file"""
    try:
        # Import here to avoid circular imports
        from app import Analysis, db

        original_filename = file.filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        unique_filename = f"{user_id or 'anon'}_{timestamp}_{filename}"

        # Create upload directory
        upload_dir = Path("./uploads/bwc_videos")
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / unique_filename

        # Save file
        file.save(filepath)

        # Get file info
        file_size = os.path.getsize(filepath)
        file_hash = calculate_file_hash(filepath)

        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            filename=original_filename,
            file_hash=file_hash,
            file_size=file_size,
            file_path=str(filepath),
            status="uploaded",
        )
        analysis.generate_id()

        db.session.add(analysis)
        db.session.commit()

        return {
            "success": True,
            "type": "video",
            "upload_id": analysis.id,
            "filename": original_filename,
            "file_size": file_size,
            "file_hash": file_hash,
        }

    except Exception as e:
        return {"success": False, "type": "video", "filename": file.filename, "error": str(e)}


def process_pdf_file(file, user_id=None):
    """Process PDF document file"""
    try:
        # Import here to avoid circular imports
        from app import PDFUpload, db

        original_filename = file.filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        unique_filename = f"{timestamp}_{filename}"

        # Create upload directory
        upload_dir = Path("./uploads/pdfs")
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / unique_filename

        # Save file
        file.save(filepath)

        # Get file info
        file_size = os.path.getsize(filepath)
        file_hash = calculate_file_hash(filepath)

        # Create PDF upload record
        pdf_upload = PDFUpload(
            user_id=user_id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=str(filepath),
            file_size=file_size,
            status="uploaded",
        )
        pdf_upload.file_hash = file_hash

        db.session.add(pdf_upload)
        db.session.commit()

        return {
            "success": True,
            "type": "pdf",
            "upload_id": pdf_upload.id,
            "filename": original_filename,
            "file_size": file_size,
            "file_hash": file_hash,
        }

    except Exception as e:
        return {"success": False, "type": "pdf", "filename": file.filename, "error": str(e)}


def process_image_file(file, user_id=None):
    """Process image file"""
    try:
        original_filename = file.filename
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        unique_filename = f"{timestamp}_{filename}"

        # Create upload directory
        upload_dir = Path("./uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)

        filepath = upload_dir / unique_filename

        # Save file
        file.save(filepath)

        # Get file info
        file_size = os.path.getsize(filepath)
        file_hash = calculate_file_hash(filepath)

        return {
            "success": True,
            "type": "image",
            "filename": original_filename,
            "file_size": file_size,
            "file_hash": file_hash,
            "file_path": str(filepath),
        }

    except Exception as e:
        return {"success": False, "type": "image", "filename": file.filename, "error": str(e)}


@batch_upload_bp.route("/api/upload/batch", methods=["POST"])
@login_required
def unified_batch_upload():
    """
    Unified batch upload endpoint - handles PDFs, BWC videos, and images
    Automatically categorizes and processes files in parallel
    """

    # Get files
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files selected"}), 400

    # Check user limits
    if not current_user.can_analyze():
        return jsonify({"error": "Monthly upload limit reached. Please upgrade your plan."}), 403

    # Categorize files
    categorized_files = {"video": [], "pdf": [], "image": [], "unknown": []}

    for file in files:
        if file.filename == "":
            continue

        category = categorize_file(file.filename)
        categorized_files[category].append(file)

    # Results structure
    results = {
        "total": len(files),
        "categorized": {
            "videos": len(categorized_files["video"]),
            "pdfs": len(categorized_files["pdf"]),
            "images": len(categorized_files["image"]),
            "unknown": len(categorized_files["unknown"]),
        },
        "successful": {"video": [], "pdf": [], "image": []},
        "failed": [],
    }

    # Process files in parallel using ThreadPoolExecutor
    user_id = current_user.id

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        # Submit video processing tasks
        for file in categorized_files["video"]:
            futures.append(executor.submit(process_video_file, file, user_id))

        # Submit PDF processing tasks
        for file in categorized_files["pdf"]:
            futures.append(executor.submit(process_pdf_file, file, user_id))

        # Submit image processing tasks
        for file in categorized_files["image"]:
            futures.append(executor.submit(process_image_file, file, user_id))

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                if result["success"]:
                    file_type = result["type"]
                    results["successful"][file_type].append(result)
                else:
                    results["failed"].append(result)
            except Exception as e:
                results["failed"].append(
                    {"filename": "unknown", "error": str(e), "type": "unknown"}
                )

    # Handle unknown file types
    for file in categorized_files["unknown"]:
        results["failed"].append(
            {"filename": file.filename, "error": "Unsupported file type", "type": "unknown"}
        )

    # Update user storage usage
    total_size = 0
    for category in results["successful"].values():
        total_size += sum(item.get("file_size", 0) for item in category)

    current_user.storage_used_mb += total_size / (1024 * 1024)

    from app import db

    db.session.commit()

    # Log audit
    from app import AuditLog

    AuditLog.log(
        "batch_upload",
        "upload",
        None,
        {
            "total_files": results["total"],
            "videos": len(results["successful"]["video"]),
            "pdfs": len(results["successful"]["pdf"]),
            "images": len(results["successful"]["image"]),
            "failed": len(results["failed"]),
        },
    )

    return jsonify(
        {
            "success": True,
            "results": results,
            "summary": {
                "total_files": results["total"],
                "total_successful": (
                    len(results["successful"]["video"])
                    + len(results["successful"]["pdf"])
                    + len(results["successful"]["image"])
                ),
                "total_failed": len(results["failed"]),
                "breakdown": {
                    "videos": {
                        "successful": len(results["successful"]["video"]),
                        "failed": sum(1 for f in results["failed"] if f.get("type") == "video"),
                    },
                    "pdfs": {
                        "successful": len(results["successful"]["pdf"]),
                        "failed": sum(1 for f in results["failed"] if f.get("type") == "pdf"),
                    },
                    "images": {
                        "successful": len(results["successful"]["image"]),
                        "failed": sum(1 for f in results["failed"] if f.get("type") == "image"),
                    },
                },
            },
        }
    )


# Register blueprint in app.py:
# from batch_upload_handler import batch_upload_bp
# app.register_blueprint(batch_upload_bp)
