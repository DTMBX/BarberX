# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python
"""
BWC Forensic Analyzer Web Application
Drag-and-drop interface for body-worn camera analysis
"""

import hashlib
import json
import os
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import our BWC analyzer
from .bwc_forensic_analyzer import BWCForensicAnalyzer

app = Flask(__name__)
CORS(app)


def _get_safe_report_path(upload_id: str) -> Path:
    """
    Return the resolved Path to report.json for a given upload_id,
    ensuring it stays within ANALYSIS_FOLDER to prevent path traversal.
    """
    base_dir = ANALYSIS_FOLDER.resolve()
    candidate_dir = (ANALYSIS_FOLDER / upload_id).resolve()

    # Ensure the candidate directory is inside the analysis base directory
    try:
        candidate_dir.relative_to(base_dir)
    except ValueError:
        raise ValueError("Upload ID resolves outside analysis folder")

    return candidate_dir / "report.json"


def _safe_report_path(upload_id: str) -> Path | None:
    """
    Build a safe path to report.json for the given upload_id.

    Returns a Path if upload_id is syntactically valid and resolves
    to a location under ANALYSIS_FOLDER, otherwise returns None.
    """
    # Allow only simple, directory-name-safe IDs
    import re

    if not re.fullmatch(r"[A-Za-z0-9_-]+", upload_id or ""):
        return None

    base = ANALYSIS_FOLDER.resolve()
    candidate = (ANALYSIS_FOLDER / upload_id / "report.json").resolve()

    try:
        candidate.relative_to(base)
    except ValueError:
        # candidate is not within ANALYSIS_FOLDER
        return None

    return candidate

# Configuration
UPLOAD_FOLDER = Path("./uploads/bwc_videos")
ANALYSIS_FOLDER = Path("./bwc_analysis")
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"}
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ANALYSIS_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ANALYSIS_FOLDER"] = ANALYSIS_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# Global analyzer instance
analyzer = None
analysis_status = {}  # Track analysis progress


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_hash(filepath):
    """Calculate SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


@app.route("/")
def index():
    """Serve the BWC analyzer web interface"""
    return send_file("bwc-analyzer.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Check if AI models are loaded"""
    global analyzer

    try:
        if analyzer is None:
            # Initialize analyzer on first request
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            analyzer = BWCForensicAnalyzer(whisper_model_size="base", hf_token=hf_token)

        return jsonify(
            {
                "status": "ready",
                "models": {
                    "whisper": analyzer.whisper_model is not None,
                    "pyannote": analyzer.diarization_pipeline is not None,
                    "spacy": analyzer.nlp is not None,
                },
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Handle BWC video file upload"""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return (
            jsonify({"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}),
            400,
        )

    # Secure the filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{filename}"
    filepath = UPLOAD_FOLDER / unique_filename

    # Save file
    file.save(filepath)

    # Calculate hash
    file_hash = get_file_hash(filepath)
    file_size = os.path.getsize(filepath)

    # Create upload record
    upload_id = file_hash[:16]  # Use first 16 chars of hash as ID

    analysis_status[upload_id] = {
        "status": "uploaded",
        "filename": filename,
        "filepath": str(filepath),
        "file_hash": file_hash,
        "file_size": file_size,
        "upload_time": datetime.now().isoformat(),
        "progress": 0,
    }

    return jsonify(
        {
            "upload_id": upload_id,
            "filename": filename,
            "file_hash": file_hash,
            "file_size": file_size,
            "message": "File uploaded successfully",
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze_video():
    """Start BWC video analysis"""
    global analyzer

    data = request.get_json()
    upload_id = data.get("upload_id")

    if not upload_id or upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 400

    # Get case metadata from request
    case_metadata = {
        "acquired_by": data.get("acquired_by", "Unknown"),
        "source": data.get("source", "Web Upload"),
        "case_number": data.get("case_number", ""),
        "evidence_number": data.get("evidence_number", ""),
        "known_officers": data.get("known_officers", []),
    }

    # Update status
    analysis_status[upload_id]["status"] = "analyzing"
    analysis_status[upload_id]["case_metadata"] = case_metadata
    analysis_status[upload_id]["start_time"] = datetime.now().isoformat()

    # Start analysis in background thread
    def run_analysis():
        try:
            filepath = analysis_status[upload_id]["filepath"]

            # Update progress
            analysis_status[upload_id]["progress"] = 10
            analysis_status[upload_id]["current_step"] = "Extracting audio..."

            # Run analysis
            report = analyzer.analyze_bwc_file(
                video_path=filepath,
                acquired_by=case_metadata["acquired_by"],
                source=case_metadata["source"],
                case_number=case_metadata.get("case_number"),
                evidence_number=case_metadata.get("evidence_number"),
                known_officers=case_metadata.get("known_officers"),
            )

            # Update progress
            analysis_status[upload_id]["progress"] = 90
            analysis_status[upload_id]["current_step"] = "Generating reports..."

            # Save reports
            output_dir = ANALYSIS_FOLDER / upload_id
            output_files = analyzer.export_report(
                report, output_dir=str(output_dir), formats=["json", "txt", "md"]
            )

            # Update status
            analysis_status[upload_id]["status"] = "completed"
            analysis_status[upload_id]["progress"] = 100
            analysis_status[upload_id]["current_step"] = "Analysis complete"
            analysis_status[upload_id]["end_time"] = datetime.now().isoformat()
            analysis_status[upload_id]["report_files"] = output_files
            analysis_status[upload_id]["summary"] = report.generate_summary()

            # Store key findings
            analysis_status[upload_id]["results"] = {
                "duration": report.duration,
                "total_speakers": len(report.speakers),
                "total_segments": len(report.transcript),
                "total_discrepancies": len(report.discrepancies),
                "critical_discrepancies": len(
                    [d for d in report.discrepancies if d.severity == "critical"]
                ),
                "entities": report.entities,
                "speakers": report.speakers,
            }

        except Exception as e:
            analysis_status[upload_id]["status"] = "failed"
            analysis_status[upload_id]["error"] = str(e)
            analysis_status[upload_id]["progress"] = 0

    # Start background thread
    thread = threading.Thread(target=run_analysis)
    thread.start()

    return jsonify({"upload_id": upload_id, "message": "Analysis started", "status": "analyzing"})


@app.route("/api/status/<upload_id>", methods=["GET"])
def get_status(upload_id):
    """Get analysis status and progress"""
    if upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 404

    status_data = analysis_status[upload_id].copy()

    # Don't send full filepath to client
    if "filepath" in status_data:
        status_data["filepath"] = Path(status_data["filepath"]).name

    return jsonify(status_data)


@app.route("/api/report/<upload_id>/<format>", methods=["GET"])
def download_report(upload_id, format):
    """Download analysis report in specified format"""
    if upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 404

    status = analysis_status[upload_id]

    if status["status"] != "completed":
        return jsonify({"error": "Analysis not completed"}), 400

    # Find report file
    output_dir = ANALYSIS_FOLDER / upload_id

    if format == "json":
        report_file = output_dir / "report.json"
        mimetype = "application/json"
    elif format == "txt":
        report_file = output_dir / "report.txt"
        mimetype = "text/plain"
    elif format == "md":
        report_file = output_dir / "report.md"
        mimetype = "text/markdown"
    else:
    try:
        report_file = _get_safe_report_path(upload_id)
    except ValueError:
        return jsonify({"error": "Invalid upload ID path"}), 400

    if not report_file.exists():
        return jsonify({"error": "Report file not found"}), 404

    return send_file(
        report_file,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"BWC_Analysis_{upload_id}.{format}",
    )


@app.route("/api/transcript/<upload_id>", methods=["GET"])
def get_transcript(upload_id):
    """Get full transcript with timestamps"""
    if upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 404

    status = analysis_status[upload_id]

    if status["status"] != "completed":
        return jsonify({"error": "Analysis not completed"}), 400

    # Load JSON report
    safe_upload_id = secure_filename(str(upload_id))
    report_file = ANALYSIS_FOLDER / safe_upload_id / "report.json"

    # Ensure the resolved path stays within the analysis folder
    try:
        report_file = _get_safe_report_path(upload_id)
    except ValueError:
        return jsonify({"error": "Invalid upload ID path"}), 400
        report_file_resolved = report_file.resolve()
        analysis_root_resolved = ANALYSIS_FOLDER.resolve()
    except FileNotFoundError:
        # If components in the path do not exist yet, treat as not found
        return jsonify({"error": "Report not found"}), 404

    if analysis_root_resolved not in report_file_resolved.parents and report_file_resolved != analysis_root_resolved:
        return jsonify({"error": "Invalid upload ID"}), 400

    if not report_file_resolved.exists():
        return jsonify({"error": "Report not found"}), 404

    with open(report_file_resolved, encoding="utf-8") as f:
        report_data = json.load(f)

    return jsonify(
        {
            "transcript": report_data.get("transcript", []),
            "speakers": report_data.get("speakers", {}),
            "duration": report_data.get("duration", 0),
        }
    )


    report_file = _safe_report_path(upload_id)
    if report_file is None:
        return jsonify({"error": "Invalid upload ID format"}), 400
def get_discrepancies(upload_id):
    """Get all discrepancies found"""
    if upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 404

    status = analysis_status[upload_id]

    if status["status"] != "completed":
        return jsonify({"error": "Analysis not completed"}), 400

    # Load JSON report
    report_file = ANALYSIS_FOLDER / upload_id / "report.json"

    if not report_file.exists():
    try:
        report_file = _get_safe_report_path(upload_id)
    except ValueError:
        return jsonify({"error": "Invalid upload ID path"}), 400

    with open(report_file, encoding="utf-8") as f:
        report_data = json.load(f)

    discrepancies = report_data.get("discrepancies", [])

    # Group by severity
    critical = [d for d in discrepancies if d["severity"] == "critical"]
    major = [d for d in discrepancies if d["severity"] == "major"]
    minor = [d for d in discrepancies if d["severity"] == "minor"]

    return jsonify(
        {
            "total": len(discrepancies),
            "critical": critical,
            "major": major,
            "minor": minor,
            "summary": {
                "critical_count": len(critical),
                "major_count": len(major),
                "minor_count": len(minor),
            },
        }
    )


@app.route("/api/entities/<upload_id>", methods=["GET"])
def get_entities(upload_id):
    """Get all extracted entities"""
    if upload_id not in analysis_status:
        return jsonify({"error": "Invalid upload ID"}), 404

    status = analysis_status[upload_id]

    if status["status"] != "completed":
        return jsonify({"error": "Analysis not completed"}), 400

    # Load JSON report
    report_file = ANALYSIS_FOLDER / upload_id / "report.json"

    if not report_file.exists():
        return jsonify({"error": "Report not found"}), 404

    with open(report_file, encoding="utf-8") as f:
        report_data = json.load(f)

    return jsonify(
        {
            "entities": report_data.get("entities", {}),
            "total_entities": sum(len(v) for v in report_data.get("entities", {}).values()),
        }
    )


@app.route("/api/analyses", methods=["GET"])
def list_analyses():
    """List all analysis sessions"""
    analyses = []

    for upload_id, status in analysis_status.items():
        analyses.append(
            {
                "upload_id": upload_id,
                "filename": status.get("filename"),
                "status": status.get("status"),
                "upload_time": status.get("upload_time"),
                "case_number": status.get("case_metadata", {}).get("case_number"),
                "progress": status.get("progress", 0),
                "results": status.get("results") if status.get("status") == "completed" else None,
            }
        )

    # Sort by upload time (most recent first)
    analyses.sort(key=lambda x: x["upload_time"], reverse=True)

    return jsonify({"total": len(analyses), "analyses": analyses})


if __name__ == "__main__":
    print(
        """
    ╔════════════════════════════════════════════════════════════════╗
    ║   BWC Forensic Analyzer - Web Application                     ║
    ║   Drag-and-Drop Interface for Body-Worn Camera Analysis       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    🌐 Web Interface: http://localhost:5000
    📊 API Docs: http://localhost:5000/api/health
    
    Ready to accept BWC video uploads!
    Press Ctrl+C to stop the server.
    """
    )

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
