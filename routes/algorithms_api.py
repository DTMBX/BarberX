"""
Algorithms API Routes — /api/v1/algorithms/*
==============================================
REST endpoints for running, listing, and querying court-defensible algorithms.

All endpoints:
  - Require Bearer-token authentication (@api_token_required).
  - Enforce tenant isolation via organization_id.
  - Return JSON responses.
  - Emit audit events for every algorithm run.
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from auth.api_auth import api_token_required
from auth.models import db

logger = logging.getLogger(__name__)

algorithms_api_bp = Blueprint("algorithms_api", __name__, url_prefix="/api/v1/algorithms")


def _get_algorithm_context(tenant_id=None):
    """Build the standard context dict for algorithm execution."""
    from services.evidence_store import EvidenceStore
    from services.audit_stream import AuditStream

    store = EvidenceStore()
    audit = AuditStream(db.session, store)
    return {
        "db_session": db.session,
        "evidence_store": store,
        "audit_stream": audit,
    }


def _get_tenant_id():
    """Extract tenant (organization) ID from the authenticated user."""
    user = getattr(g, "api_user", None) or getattr(g, "current_user", None)
    if user:
        return getattr(user, "organization_id", 1) or 1
    return 1


def _get_actor_info():
    """Extract actor ID and name from the authenticated user."""
    user = getattr(g, "api_user", None) or getattr(g, "current_user", None)
    if user:
        return getattr(user, "id", None), getattr(user, "display_name", None) or getattr(user, "email", "system")
    return None, "system"


# ===================================================================
# List available algorithms
# ===================================================================

@algorithms_api_bp.route("/", methods=["GET"])
@api_token_required
def list_algorithms():
    """List all registered algorithms with metadata."""
    from algorithms.registry import registry

    # Ensure all algorithm modules are imported
    _ensure_algorithms_loaded()

    return jsonify({
        "algorithms": registry.list_algorithms(),
        "count": len(registry.list_algorithms()),
    })


# ===================================================================
# Run an algorithm
# ===================================================================

@algorithms_api_bp.route("/run", methods=["POST"])
@api_token_required
def run_algorithm():
    """
    Run a specified algorithm on a case.

    JSON body:
        algorithm_id (str, required): Algorithm to run.
        case_id (int, required): Target case.
        version (str, optional): Specific algorithm version.
        params (dict, optional): Algorithm-specific parameters.
        async (bool, optional): Run as background task (default false).
    """
    from algorithms.registry import registry
    from algorithms.base import AlgorithmParams

    _ensure_algorithms_loaded()

    data = request.get_json(force=True) if request.is_json else {}
    algorithm_id = data.get("algorithm_id")
    case_id = data.get("case_id")
    version = data.get("version")
    extra_params = data.get("params", {})
    run_async = data.get("async", False)

    if not algorithm_id:
        return jsonify({"error": "algorithm_id is required"}), 400
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    algo = registry.get(algorithm_id, version)
    if not algo:
        return jsonify({"error": f"Algorithm '{algorithm_id}' not found"}), 404

    tenant_id = _get_tenant_id()
    actor_id, actor_name = _get_actor_info()

    params = AlgorithmParams(
        case_id=int(case_id),
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_name=actor_name,
        extra=extra_params,
    )

    if run_async:
        # Dispatch to Celery
        from tasks.algorithm_tasks import dispatch_algorithm
        task_info = dispatch_algorithm(algorithm_id, version, params.to_dict())
        return jsonify({"status": "dispatched", **task_info}), 202

    # Synchronous execution
    context = _get_algorithm_context(tenant_id)
    result = algo.run(params, context)

    # Store run record
    _store_algorithm_run(result, params)

    return jsonify(result.to_dict()), 200 if result.success else 500


# ===================================================================
# Get algorithm run history
# ===================================================================

@algorithms_api_bp.route("/runs", methods=["GET"])
@api_token_required
def list_runs():
    """
    List algorithm run records for a case.

    Query params:
        case_id (int, required)
        algorithm_id (str, optional)
        page, per_page
    """
    from models.algorithm_models import AlgorithmRun

    case_id = request.args.get("case_id", type=int)
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    query = AlgorithmRun.query.filter_by(case_id=case_id)

    algorithm_id = request.args.get("algorithm_id")
    if algorithm_id:
        query = query.filter_by(algorithm_id=algorithm_id)

    query = query.order_by(AlgorithmRun.created_at.desc())

    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, max(1, request.args.get("per_page", 25, type=int)))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    runs = []
    for run in pagination.items:
        runs.append({
            "id": run.id,
            "run_id": run.run_id,
            "algorithm_id": run.algorithm_id,
            "algorithm_version": run.algorithm_version,
            "case_id": run.case_id,
            "success": run.success,
            "duration_seconds": run.duration_seconds,
            "result_hash": run.result_hash,
            "integrity_check": run.integrity_check,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        })

    return jsonify({
        "runs": runs,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    })


# ===================================================================
# Get a specific run result
# ===================================================================

@algorithms_api_bp.route("/runs/<run_id>", methods=["GET"])
@api_token_required
def get_run(run_id):
    """Get full details of a specific algorithm run."""
    from models.algorithm_models import AlgorithmRun
    import json

    run = AlgorithmRun.query.filter_by(run_id=run_id).first()
    if not run:
        return jsonify({"error": "Run not found"}), 404

    data = {
        "id": run.id,
        "run_id": run.run_id,
        "algorithm_id": run.algorithm_id,
        "algorithm_version": run.algorithm_version,
        "case_id": run.case_id,
        "tenant_id": run.tenant_id,
        "success": run.success,
        "error": run.error_message,
        "duration_seconds": run.duration_seconds,
        "result_hash": run.result_hash,
        "params_hash": run.params_hash,
        "integrity_check": run.integrity_check,
        "input_hashes": json.loads(run.input_hashes_json) if run.input_hashes_json else [],
        "output_hashes": json.loads(run.output_hashes_json) if run.output_hashes_json else [],
        "payload": json.loads(run.payload_json) if run.payload_json else {},
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }
    return jsonify(data)


# ===================================================================
# Convenience endpoints
# ===================================================================

@algorithms_api_bp.route("/integrity-sweep", methods=["POST"])
@api_token_required
def api_integrity_sweep():
    """Run an integrity sweep on a case. Shorthand for run with algorithm_id=integrity_sweep."""
    data = request.get_json(force=True) if request.is_json else {}
    data["algorithm_id"] = "integrity_sweep"
    # Re-dispatch to run_algorithm via internal call
    return _run_algorithm_shorthand(data)


@algorithms_api_bp.route("/timeline", methods=["POST"])
@api_token_required
def api_timeline():
    """Run timeline alignment on a case."""
    data = request.get_json(force=True) if request.is_json else {}
    data["algorithm_id"] = "timeline_alignment"
    return _run_algorithm_shorthand(data)


@algorithms_api_bp.route("/court-package", methods=["POST"])
@api_token_required
def api_court_package():
    """
    Generate a court package for a case.

    Runs provenance graph + integrity sweep + bates generator,
    then bundles into a court package export.
    """
    from algorithms.registry import registry
    from algorithms.base import AlgorithmParams

    _ensure_algorithms_loaded()

    data = request.get_json(force=True) if request.is_json else {}
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    tenant_id = _get_tenant_id()
    actor_id, actor_name = _get_actor_info()

    params = AlgorithmParams(
        case_id=int(case_id),
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_name=actor_name,
        extra=data.get("params", {}),
    )
    context = _get_algorithm_context(tenant_id)

    results = {}
    for algo_id in ["integrity_sweep", "provenance_graph", "timeline_alignment", "bates_generator"]:
        algo = registry.get(algo_id)
        if algo:
            result = algo.run(params, context)
            results[algo_id] = result.to_dict()
            _store_algorithm_run(result, params)

    # Build combined court package hash
    from algorithms.base import hash_json
    package_hash = hash_json(results)

    return jsonify({
        "court_package": {
            "case_id": case_id,
            "algorithms_run": list(results.keys()),
            "results": results,
            "package_hash": package_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    })


@algorithms_api_bp.route("/replay", methods=["POST"])
@api_token_required
def replay_case():
    """Re-run all recorded algorithm runs for a case and verify reproducibility.

    POST /api/v1/algorithms/replay
    Body: {"case_id": <int>}
    Returns: ReplayReport with per-run verdicts showing match/mismatch.
    """
    _ensure_algorithms_loaded()

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    tenant_id = _get_tenant_id()
    context = _get_algorithm_context(tenant_id)

    from algorithms.replay import ReplayEngine

    engine = ReplayEngine()
    report = engine.replay_case(
        case_id=int(case_id),
        tenant_id=tenant_id,
        db_session=context["db_session"],
        evidence_store=context["evidence_store"],
        audit_stream=context["audit_stream"],
    )

    return jsonify(report.to_dict()), 200 if report.all_reproducible else 409


@algorithms_api_bp.route("/sealed-package", methods=["POST"])
@api_token_required
def sealed_package():
    """Generate an integrity-sealed court package for a case.

    POST /api/v1/algorithms/sealed-package
    Body: {"case_id": <int>, "output_dir": "<path>"}
    Returns: SealedPackageResult with seal hash and manifest.
    """
    _ensure_algorithms_loaded()

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    tenant_id = _get_tenant_id()
    actor_id, actor_name = _get_actor_info()
    context = _get_algorithm_context(tenant_id)

    from algorithms.sealed_export import SealedCourtPackageBuilder

    output_dir = data.get("output_dir", "exports/sealed")
    builder = SealedCourtPackageBuilder(export_base=output_dir)
    result = builder.build(
        case_id=int(case_id),
        tenant_id=tenant_id,
        db_session=context["db_session"],
        evidence_store=context["evidence_store"],
        audit_stream=context["audit_stream"],
        actor_name=actor_name or f"api:user:{actor_id}",
    )

    status = 200 if result.success else 500
    return jsonify(result.to_dict()), status


# ===================================================================
# Helpers
# ===================================================================

def _run_algorithm_shorthand(data):
    """Internal helper for convenience endpoints."""
    from algorithms.registry import registry
    from algorithms.base import AlgorithmParams

    _ensure_algorithms_loaded()

    algorithm_id = data.get("algorithm_id")
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    algo = registry.get(algorithm_id)
    if not algo:
        return jsonify({"error": f"Algorithm '{algorithm_id}' not found"}), 404

    tenant_id = _get_tenant_id()
    actor_id, actor_name = _get_actor_info()

    params = AlgorithmParams(
        case_id=int(case_id),
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_name=actor_name,
        extra=data.get("params", {}),
    )
    context = _get_algorithm_context(tenant_id)
    result = algo.run(params, context)
    _store_algorithm_run(result, params)

    return jsonify(result.to_dict()), 200 if result.success else 500


def _store_algorithm_run(result, params):
    """Persist an algorithm run record to the database."""
    import json
    try:
        from models.algorithm_models import AlgorithmRun

        run = AlgorithmRun(
            run_id=result.run_id,
            algorithm_id=result.algorithm_id,
            algorithm_version=result.algorithm_version,
            case_id=params.case_id,
            tenant_id=params.tenant_id,
            actor_id=params.actor_id,
            success=result.success,
            error_message=result.error,
            duration_seconds=result.duration_seconds,
            params_hash=result.params_hash,
            result_hash=result.result_hash,
            integrity_check=result.integrity_check,
            input_hashes_json=json.dumps(result.input_hashes),
            output_hashes_json=json.dumps(result.output_hashes),
            payload_json=json.dumps(result.payload, default=str),
        )
        db.session.add(run)
        db.session.commit()
    except Exception as exc:
        logger.warning("Failed to store algorithm run %s: %s", result.run_id, exc)
        db.session.rollback()


_algorithms_loaded = False

def _ensure_algorithms_loaded():
    """Import all algorithm modules to trigger registration."""
    global _algorithms_loaded
    if _algorithms_loaded:
        return
    import algorithms.bulk_dedup  # noqa: F401
    import algorithms.provenance_graph  # noqa: F401
    import algorithms.timeline_alignment  # noqa: F401
    import algorithms.integrity_sweep  # noqa: F401
    import algorithms.bates_generator  # noqa: F401
    import algorithms.redaction_verify  # noqa: F401
    import algorithms.access_anomaly  # noqa: F401
    _algorithms_loaded = True
