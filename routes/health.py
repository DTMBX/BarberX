"""
Health-Check Endpoints
======================
Unauthenticated endpoints for load-balancer probes and monitoring.

  /health/live   — Liveness: process is running and can serve HTTP.
  /health/ready  — Readiness: database connection is functional.
  /health/info   — Build metadata (version, environment).

These MUST NOT require authentication.  They return JSON only.
"""

import os
import time
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/health")

_BOOT_TIME = time.monotonic()


def _read_version() -> str:
    """Read VERSION file from project root, falling back to 'unknown'."""
    try:
        version_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "VERSION"
        )
        with open(version_path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "unknown"


@health_bp.route("/live", methods=["GET"])
def liveness():
    """Liveness probe — confirms the process is running."""
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}), 200


@health_bp.route("/ready", methods=["GET"])
def readiness():
    """Readiness probe — confirms database connectivity."""
    from auth.models import db

    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
        db_error = None
    except Exception as exc:  # noqa: BLE001
        db_ok = False
        db_error = str(exc)

    status_code = 200 if db_ok else 503
    payload = {
        "status": "ok" if db_ok else "degraded",
        "checks": {
            "database": {
                "status": "ok" if db_ok else "fail",
            },
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if db_error:
        payload["checks"]["database"]["error"] = db_error

    return jsonify(payload), status_code


@health_bp.route("/info", methods=["GET"])
def info():
    """Build / runtime metadata — safe for external monitoring dashboards."""
    uptime_seconds = round(time.monotonic() - _BOOT_TIME, 1)
    return jsonify({
        "version": _read_version(),
        "environment": os.environ.get("FLASK_ENV", "development"),
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200
