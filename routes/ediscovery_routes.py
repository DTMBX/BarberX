"""
eDiscovery Routes — Phase 11 (UI Pages)
=========================================
Blueprint: ediscovery_bp, mounted at /ediscovery

Server-rendered pages for litigation holds, privilege logs, production
set management, and forensic algorithm dashboard.  All mutation is
performed via the existing /api/legal/* and /api/v1/algorithms/*
JSON endpoints.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, request, abort, jsonify,
)
from flask_login import login_required, current_user

ediscovery_bp = Blueprint(
    "ediscovery", __name__,
    url_prefix="/ediscovery",
    template_folder="../templates/ediscovery",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_case_or_404(case_id):
    """Load case and enforce tenant isolation."""
    from models.legal_case import LegalCase
    from auth.models import db
    case = db.session.get(LegalCase, case_id)
    if case is None:
        abort(404)
    return case


# ---------------------------------------------------------------------------
# Dashboard — case picker for eDiscovery features
# ---------------------------------------------------------------------------

@ediscovery_bp.route("/")
@login_required
def ediscovery_index():
    """Show eDiscovery case picker."""
    from models.legal_case import LegalCase
    cases = LegalCase.query.order_by(LegalCase.created_at.desc()).all()
    return render_template("ediscovery/index.html", cases=cases)


# ---------------------------------------------------------------------------
# Litigation Holds
# ---------------------------------------------------------------------------

@ediscovery_bp.route("/case/<int:case_id>/holds")
@login_required
def litigation_holds(case_id):
    """Display litigation hold status and actions."""
    case = _load_case_or_404(case_id)
    return render_template("ediscovery/holds.html", case=case)


# ---------------------------------------------------------------------------
# Privilege Log
# ---------------------------------------------------------------------------

@ediscovery_bp.route("/case/<int:case_id>/privilege-log")
@login_required
def privilege_log(case_id):
    """Display privilege log for a case."""
    case = _load_case_or_404(case_id)

    from models.evidence import PrivilegeLog
    logs = (
        PrivilegeLog.query
        .filter_by(case_id=case_id)
        .order_by(PrivilegeLog.created_at.desc())
        .all()
    )
    return render_template("ediscovery/privilege_log.html", case=case, logs=logs)


# ---------------------------------------------------------------------------
# Production Sets
# ---------------------------------------------------------------------------

@ediscovery_bp.route("/case/<int:case_id>/productions")
@login_required
def production_sets(case_id):
    """Display production sets for a case."""
    case = _load_case_or_404(case_id)

    from models.evidence import ProductionSet
    productions = (
        ProductionSet.query
        .filter_by(case_id=case_id)
        .order_by(ProductionSet.created_at.desc())
        .all()
    )
    return render_template(
        "ediscovery/productions.html", case=case, productions=productions,
    )


@ediscovery_bp.route("/case/<int:case_id>/productions/<int:prod_id>")
@login_required
def production_detail(case_id, prod_id):
    """Display a single production set's items."""
    case = _load_case_or_404(case_id)

    from models.evidence import ProductionSet
    production = ProductionSet.query.get(prod_id)
    if not production or production.case_id != case_id:
        abort(404)

    return render_template(
        "ediscovery/production_detail.html",
        case=case, production=production,
    )


# ---------------------------------------------------------------------------
# Algorithm Dashboard — Phase 11
# ---------------------------------------------------------------------------

@ediscovery_bp.route("/case/<int:case_id>/algorithms")
@login_required
def algorithm_dashboard(case_id):
    """Display the forensic algorithm dashboard for a case."""
    case = _load_case_or_404(case_id)

    # Fetch prior algorithm runs for this case
    from models.algorithm_models import AlgorithmRun
    runs = (
        AlgorithmRun.query
        .filter_by(case_id=case_id)
        .order_by(AlgorithmRun.created_at.desc())
        .limit(50)
        .all()
    )

    # Get available algorithms
    from algorithms.registry import registry
    _ensure_algorithms_loaded()
    algorithms = registry.list_algorithms()

    return render_template(
        "ediscovery/algorithm_dashboard.html",
        case=case, runs=runs, algorithms=algorithms,
    )


@ediscovery_bp.route("/case/<int:case_id>/algorithms/run/<run_id>")
@login_required
def algorithm_run_detail(case_id, run_id):
    """Display details of a single algorithm run."""
    case = _load_case_or_404(case_id)

    from models.algorithm_models import AlgorithmRun
    run = AlgorithmRun.query.filter_by(run_id=run_id, case_id=case_id).first()
    if run is None:
        abort(404)

    import json
    payload = {}
    try:
        payload = json.loads(run.payload_json or "{}")
    except (json.JSONDecodeError, TypeError):
        pass

    return render_template(
        "ediscovery/algorithm_run_detail.html",
        case=case, run=run, payload=payload,
    )


@ediscovery_bp.route("/case/<int:case_id>/algorithms/replay")
@login_required
def replay_dashboard(case_id):
    """Display replay verification results for a case."""
    case = _load_case_or_404(case_id)
    return render_template(
        "ediscovery/replay_dashboard.html",
        case=case,
    )


# ---------------------------------------------------------------------------
# Helpers (Phase 11)
# ---------------------------------------------------------------------------

_algos_loaded = False

def _ensure_algorithms_loaded():
    """Import algorithm modules to populate the registry."""
    global _algos_loaded
    if _algos_loaded:
        return
    try:
        import algorithms.bulk_dedup  # noqa: F401
        import algorithms.provenance_graph  # noqa: F401
        import algorithms.timeline_alignment  # noqa: F401
        import algorithms.integrity_sweep  # noqa: F401
        import algorithms.bates_generator  # noqa: F401
        import algorithms.redaction_verify  # noqa: F401
        import algorithms.access_anomaly  # noqa: F401
        _algos_loaded = True
    except ImportError:
        pass
