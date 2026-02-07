# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
INTEGRATION EXAMPLE - How to Add Backend Optimization to app.py

This file shows how to integrate all new backend components into app.py
Copy these sections into your app.py at the appropriate locations
"""

# ============================================================================
# SECTION 1: Imports (add to top of app.py after existing imports)
# ============================================================================

from .api_middleware import (
    api_endpoint,
    rate_limit,
)
from .backend_integration import (
    error_response,
    event_bus,
    service_registry,
    success_response,
)
from .config_manager import ConfigManager, DatabaseBackup, DatabaseOptimizer
from .unified_evidence_service import EvidenceReportGenerator, UnifiedEvidenceProcessor

# ============================================================================
# SECTION 2: Configuration (replace existing config section)
# ============================================================================

# Initialize configuration manager
config_mgr = ConfigManager()

# Apply configuration to Flask
app.config.update(config_mgr.get_sqlalchemy_config())
app.config["SECRET_KEY"] = config_mgr.config.secret_key
app.config["UPLOAD_FOLDER"] = config_mgr.config.upload_folder
app.config["MAX_CONTENT_LENGTH"] = config_mgr.config.max_upload_size

# Initialize database (after db = SQLAlchemy(app))
with app.app_context():
    db.create_all()

    # Optimize database
    optimizer = DatabaseOptimizer(db)
    optimizer.create_indexes()
    optimizer.analyze_tables()

    logger.info("✓ Database optimized with indexes")


# ============================================================================
# SECTION 3: Initialize Services (add after database initialization)
# ============================================================================

# Initialize evidence processor
evidence_processor = UnifiedEvidenceProcessor()
report_generator = EvidenceReportGenerator()
logger.info("✓ Evidence processor initialized")


# Subscribe to events (optional - for monitoring)
def on_evidence_processed(event):
    """Handle evidence processed event"""
    evidence_id = event.data.get("evidence_id")
    logger.info(f"Evidence {evidence_id} processing complete")
    # Could send email, update UI, etc.


event_bus.subscribe("evidence.processed", on_evidence_processed)
event_bus.subscribe(
    "evidence.processing_failed", lambda e: logger.error(f"Processing failed: {e.data}")
)


# ============================================================================
# SECTION 4: API Routes - Evidence Processing (add to routes section)
# ============================================================================


@app.route("/api/evidence/process", methods=["POST"])
@api_endpoint(
    db,
    require_auth=True,
    min_tier="professional",
    validation_schema={
        "required": ["case_number"],
        "optional": ["evidence_type", "tags", "description"],
        "types": {"case_number": str, "evidence_type": str},
    },
)
def api_process_evidence():
    """
    Process evidence through complete pipeline

    Requires:
    - Authentication (API key or session)
    - Professional tier or higher
    - File upload
    - Case number

    Returns:
    - Complete analysis results
    - Violation scan
    - Compliance check
    - Recommended motions
    """
    # Get uploaded file
    if "file" not in request.files:
        return error_response("No file uploaded", error_code="NO_FILE"), 400

    file = request.files["file"]
    if file.filename == "":
        return error_response("Empty filename", error_code="INVALID_FILE"), 400

    # Save file
    from werkzeug.utils import secure_filename

    filename = secure_filename(file.filename)
    filepath = Path(app.config["UPLOAD_FOLDER"]) / str(g.user.id) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    file.save(filepath)

    # Determine evidence type
    evidence_type = request.validated_data.get("evidence_type")
    if not evidence_type:
        ext = filename.rsplit(".", 1)[-1].lower()
        type_map = {
            "mp4": "video",
            "avi": "video",
            "mov": "video",
            "mp3": "audio",
            "wav": "audio",
            "pdf": "document",
            "docx": "document",
            "jpg": "image",
            "png": "image",
        }
        evidence_type = type_map.get(ext, "document")

    # Process evidence
    try:
        results = evidence_processor.process_evidence(
            evidence_file=filepath,
            evidence_type=evidence_type,
            context={
                "evidence_id": f"EVID-{g.user.id}-{int(time.time())}",
                "case_number": request.validated_data["case_number"],
                "user_id": g.user.id,
                "tags": request.validated_data.get("tags", []),
                "description": request.validated_data.get("description"),
            },
        )

        return success_response(
            "Evidence processed successfully",
            {
                "evidence_id": results["evidence_id"],
                "summary": results["summary"],
                "violations_found": results.get("violations", {}).get("total_violations", 0),
                "compliance_status": results.get("compliance", {}).get("overall_status"),
                "recommended_motions": len(results.get("motions_to_file", [])),
                "full_results": results,
            },
        )

    except Exception as e:
        logger.exception("Evidence processing error")
        return error_response(f"Processing failed: {str(e)}", error_code="PROCESSING_ERROR"), 500


@app.route("/api/evidence/<evidence_id>/report", methods=["GET"])
@api_endpoint(db, require_auth=True)
def api_get_evidence_report(evidence_id):
    """
    Generate report for processed evidence

    Query params:
    - format: markdown (default), html, pdf
    """
    # Get analysis results from database (implement based on your schema)
    # For demo, returning cached results
    from backend_integration import cache

    results = cache.get(f"evidence_results_{evidence_id}")
    if not results:
        return error_response("Evidence not found", error_code="NOT_FOUND"), 404

    # Generate report
    report_format = request.args.get("format", "markdown")
    report = report_generator.generate_report(results, format=report_format)

    # Return appropriate response
    if report_format == "html":
        return report, 200, {"Content-Type": "text/html"}
    elif report_format == "pdf":
        return report, 200, {"Content-Type": "application/pdf"}
    else:
        return report, 200, {"Content-Type": "text/markdown"}


@app.route("/api/evidence/batch", methods=["POST"])
@api_endpoint(
    db, require_auth=True, min_tier="enterprise", validation_schema={"required": ["case_number"]}
)
def api_batch_process_evidence():
    """
    Batch process multiple evidence files

    Requires:
    - Enterprise tier
    - Multiple file uploads

    Returns:
    - Batch job ID
    """
    from backend_integration import task_queue

    files = request.files.getlist("files")
    if not files:
        return error_response("No files uploaded", error_code="NO_FILES"), 400

    # Queue each file for processing
    job_ids = []
    for file in files:
        job_id = task_queue.submit(
            evidence_processor.process_evidence,
            file_path=file.filename,
            evidence_type="auto",
            context={"case_number": request.validated_data["case_number"], "user_id": g.user.id},
        )
        job_ids.append(job_id)

    return success_response(
        f"Queued {len(job_ids)} files for processing",
        {"job_ids": job_ids, "total_files": len(job_ids)},
    )


# ============================================================================
# SECTION 5: Admin Routes - System Monitoring (add to admin section)
# ============================================================================


@app.route("/admin/system/performance")
@login_required
@admin_required
def admin_performance_metrics():
    """View system performance metrics"""
    from backend_integration import performance_monitor

    stats = performance_monitor.get_stats()

    return render_template(
        "admin/performance.html", metrics=stats, service_registry=service_registry.list_services()
    )


@app.route("/admin/system/optimize", methods=["POST"])
@login_required
@admin_required
def admin_optimize_database():
    """Run database optimization"""
    optimizer = DatabaseOptimizer(db)

    # Create indexes
    optimizer.create_indexes()

    # Analyze tables
    optimizer.analyze_tables()

    # Vacuum (if supported)
    optimizer.vacuum_database()

    flash("Database optimized successfully", "success")
    return redirect(url_for("admin_performance_metrics"))


@app.route("/admin/system/backup", methods=["POST"])
@login_required
@admin_required
def admin_backup_database():
    """Create database backup"""
    backup = DatabaseBackup(db)

    backup_file = backup.backup()

    if backup_file:
        flash(f"Backup created: {backup_file.name}", "success")
    else:
        flash("Backup failed", "error")

    return redirect(url_for("admin_performance_metrics"))


# ============================================================================
# SECTION 6: Rate Limit Info Endpoint (add to API section)
# ============================================================================


@app.route("/api/rate-limit/status")
@rate_limit()
def api_rate_limit_status():
    """Get current rate limit status for user"""
    from api_middleware import rate_limiter

    if hasattr(g, "user"):
        identifier = str(g.user.id)
        tier = g.user.tier
    else:
        identifier = request.remote_addr
        tier = "free"

    remaining = rate_limiter.get_remaining(identifier, tier)
    limit = rate_limiter.tier_limits[tier]

    return success_response(
        "Rate limit status",
        {"tier": tier, "limit_per_minute": limit, "remaining": remaining, "reset_in_seconds": 60},
    )


# ============================================================================
# SECTION 7: Health Check Endpoint (add to API section)
# ============================================================================


@app.route("/health")
def health_check():
    """System health check endpoint"""
    from backend_integration import performance_monitor

    # Check database
    db_healthy = True
    try:
        db.session.execute("SELECT 1")
    except Exception:
        db_healthy = False

    # Check services
    services = service_registry.list_services()
    services_healthy = all(s["status"] == "active" for s in services)

    # Get performance stats
    stats = performance_monitor.get_stats()

    health_status = {
        "status": "healthy" if (db_healthy and services_healthy) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "up" if db_healthy else "down",
            "services": "up" if services_healthy else "degraded",
        },
        "metrics": {
            "total_requests": sum(s.get("call_count", 0) for s in stats.values()),
            "registered_services": len(services),
        },
    }

    status_code = 200 if health_status["status"] == "healthy" else 503

    return jsonify(health_status), status_code


# ============================================================================
# SECTION 8: Error Handlers (add after routes)
# ============================================================================


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors"""
    return (
        jsonify(
            error_response(
                "Rate limit exceeded. Please try again later.", error_code="RATE_LIMIT_EXCEEDED"
            )
        ),
        429,
    )


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.exception("Internal server error")
    return jsonify(error_response("Internal server error", error_code="INTERNAL_ERROR")), 500


# ============================================================================
# SECTION 9: Startup Tasks (add before app.run())
# ============================================================================


def initialize_backend():
    """Initialize backend services on startup"""
    with app.app_context():
        logger.info("=" * 80)
        logger.info("Evident Backend Initialization")
        logger.info("=" * 80)

        # 1. Create indexes
        optimizer = DatabaseOptimizer(db)
        optimizer.create_indexes()
        logger.info("✓ Database indexes created")

        # 2. Register services
        logger.info(f"✓ {len(service_registry.list_services())} services registered")

        # 3. Setup backups (optional)
        backup = DatabaseBackup(db)
        backup.cleanup_old_backups(keep_days=30)
        logger.info("✓ Old backups cleaned up")

        # 4. Log configuration
        logger.info(f"✓ Environment: {config_mgr.config.environment}")
        logger.info(f"✓ Database: {config_mgr.get_database_uri()}")
        logger.info(f"✓ Upload folder: {config_mgr.config.upload_folder}")

        logger.info("=" * 80)
        logger.info("Backend ready for requests")
        logger.info("=" * 80)


# Run initialization
initialize_backend()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# Example 1: Simple protected endpoint with rate limiting
@app.route('/api/simple')
@rate_limit()
@log_request()
def simple_api():
    return success_response("Hello", {"message": "World"})


# Example 2: Authenticated endpoint with tier requirement
@app.route('/api/premium')
@require_api_key(db)
@require_tier('professional')
@rate_limit()
def premium_api():
    return success_response("Premium access", {"user_id": g.user.id})


# Example 3: All-in-one protected endpoint
@app.route('/api/endpoint', methods=['POST'])
@api_endpoint(
    db,
    require_auth=True,
    min_tier='professional',
    validation_schema={
        'required': ['field1', 'field2'],
        'types': {'field1': str, 'field2': int}
    }
)
def protected_api():
    # Auto-handled: auth, rate limit, tier check, validation, logging, errors
    data = request.validated_data
    return success_response("Success", data)


# Example 4: Process evidence with full pipeline
results = evidence_processor.process_evidence(
    evidence_file=Path("evidence.mp4"),
    evidence_type="video",
    context={
        'evidence_id': 'EVID-001',
        'case_number': 'CR-2024-001',
        'user_id': user.id
    }
)

# results includes:
# - transcript (if video/audio)
# - violations found (constitutional)
# - compliance issues (statutory)
# - recommended motions
# - case law citations
# - executive summary


# Example 5: Generate report
report = report_generator.generate_report(results, format='markdown')
html_report = report_generator.generate_report(results, format='html')


# Example 6: Monitor performance
from .backend_integration import performance_monitor
stats = performance_monitor.get_stats()
print(f"Average processing time: {stats['evidence.process_full']['avg_duration']:.2f}s")
"""


# ============================================================================
# END OF INTEGRATION EXAMPLE
# ============================================================================

print("Integration example ready!")
print("\nTo integrate:")
print("1. Copy relevant sections from this file into app.py")
print("2. Adjust imports and variable names as needed")
print("3. Run database optimizer: optimizer.create_indexes()")
print("4. Test endpoints with rate limiting")
print("5. Deploy!")
