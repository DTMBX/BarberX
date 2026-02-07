# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Flask API Routes for BWC Chunk-Level Analysis
Integrates enhanced analyzer with frontend
"""

import json

# Import our enhanced analyzer
import sys
from datetime import datetime
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, stream_with_context
from werkzeug.utils import secure_filename

sys.path.insert(0, str(Path(__file__).parent / "barber-cam" / "py"))
from bwc_enhanced_analyzer import EnhancedBWCAnalyzer

# Create blueprint
bwc_routes = Blueprint("bwc", __name__, url_prefix="/api/bwc")

# Initialize analyzer (should be singleton in production)
analyzer = None


def get_analyzer():
    """Get or create analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = EnhancedBWCAnalyzer(
            whisper_model_size="base",
            chunk_duration=45.0,
            default_tier="PROFESSIONAL",
            default_mode="balanced",
        )
    return analyzer


@bwc_routes.route("/analyze-chunked", methods=["POST"])
def analyze_chunked():
    """
    Analyze BWC video with chunk-level routing
    Returns Server-Sent Events stream for real-time progress
    """

    # Get uploaded file
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Get parameters
    tier = request.form.get("tier", "PROFESSIONAL")
    processing_mode = request.form.get("processing_mode", "balanced")
    acquired_by = request.form.get("acquired_by", "API User")
    source = request.form.get("source", "Upload")
    case_number = request.form.get("case_number")

    # Save uploaded file
    upload_dir = Path("uploads/bwc")
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = secure_filename(video_file.filename)
    video_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    video_file.save(str(video_path))

    def generate_progress():
        """Generator function for streaming progress"""
        try:
            # Get analyzer
            analyzer = get_analyzer()

            # Start analysis (in production, would stream chunk results)
            # For now, analyze and then stream cached results
            report = analyzer.analyze_bwc_file_chunked(
                video_path=str(video_path),
                acquired_by=acquired_by,
                source=source,
                tier=tier,
                processing_mode=processing_mode,
                case_number=case_number,
            )

            # Stream chunk results
            total_chunks = len(report.chunk_results)
            for i, chunk_result in enumerate(report.chunk_results, 1):
                chunk_data = {
                    "type": "chunk_complete",
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "chunk_data": chunk_result.to_dict(),
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            # Send completion message
            completion_data = {
                "type": "complete",
                "analysis": report.to_dict(),
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e),
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return Response(
        stream_with_context(generate_progress()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@bwc_routes.route("/upgrade-chunk", methods=["POST"])
def upgrade_chunk():
    """Upgrade a specific chunk to premium model"""

    data = request.json
    analysis_id = data.get("analysis_id")
    chunk_index = data.get("chunk_index")
    target_model = data.get("target_model", "claude_opus")

    if analysis_id is None or chunk_index is None:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # In production, retrieve analysis from database by ID
        # For now, simulate

        # Get analyzer
        analyzer = get_analyzer()

        # Simulate loading report (in production, load from DB)
        # report = load_analysis_report(analysis_id)

        # For demo, return simulated upgrade result
        old_cost = 0.04  # Example: Deepgram + Haiku
        new_cost = 1.13  # Example: AssemblyAI + Opus

        updated_chunk = {
            "chunk_index": chunk_index,
            "reasoning_model": target_model,
            "cost": new_cost,
            "user_upgraded": True,
            "upgraded_at": datetime.now().isoformat(),
        }

        return jsonify(
            {
                "success": True,
                "updated_chunk": updated_chunk,
                "old_cost": old_cost,
                "new_cost": new_cost,
                "new_total_cost": 2.13 - old_cost + new_cost,  # Example
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bwc_routes.route("/export/<analysis_id>", methods=["GET"])
def export_analysis(analysis_id):
    """Export analysis report as JSON"""

    try:
        # In production, retrieve analysis from database
        # report = load_analysis_report(analysis_id)

        # For demo, return sample data
        sample_report = {
            "id": analysis_id,
            "file_name": "traffic_stop_2024.mp4",
            "analysis_date": datetime.now().isoformat(),
            "total_cost": 2.13,
            "tier": "PROFESSIONAL",
            "processing_mode": "balanced",
            "chunks": [],  # Would include all chunk data
        }

        return jsonify(sample_report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bwc_routes.route("/budget-status", methods=["GET"])
def budget_status():
    """Get current budget usage status"""

    try:
        # In production, get from database/cost governor
        # user = get_current_user()
        # usage = get_monthly_usage(user)

        # For demo, return sample data
        sample_data = {
            "tier": "PROFESSIONAL",
            "monthly_limit": 50.00,
            "current_usage": 41.20,
            "usage_percent": 82.4,
            "videos_processed": 23,
            "videos_remaining": 2,
            "days_until_reset": 12,
        }

        return jsonify(sample_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bwc_routes.route("/user-upgrades", methods=["GET"])
def get_user_upgrades():
    """Get user upgrade history for ML training"""

    try:
        analyzer = get_analyzer()
        upgrades = analyzer.get_ml_training_data()

        return jsonify(
            {
                "upgrades": upgrades,
                "count": len(upgrades),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bwc_routes.route("/mark-critical", methods=["POST"])
def mark_critical_section():
    """User marks a time range as critical"""

    data = request.json
    video_id = data.get("video_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if not all([video_id, start_time is not None, end_time is not None]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Store critical marking in database
        # Would be used for future processing of this video

        marking = {
            "video_id": video_id,
            "start_time": start_time,
            "end_time": end_time,
            "marked_at": datetime.now().isoformat(),
            "marked_by": "current_user",  # Get from auth
        }

        # Save to database
        # db.critical_markings.insert(marking)

        return jsonify(
            {
                "success": True,
                "marking": marking,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Register blueprint in main app
def register_bwc_routes(app):
    """Register BWC routes with Flask app"""
    app.register_blueprint(bwc_routes)
    print("✅ BWC chunk analysis routes registered")


# Example: Add to app.py
"""
from bwc_api_routes import register_bwc_routes

# After creating Flask app
register_bwc_routes(app)
"""
