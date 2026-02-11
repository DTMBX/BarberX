"""
Algorithm Background Tasks — Celery Wrappers
===============================================
Async dispatch for long-running algorithm executions.

Follows the same pattern as tasks/processing_tasks.py:
  - dispatch_algorithm() picks async or sync based on EVIDENT_ASYNC.
  - Celery tasks wrap the synchronous algorithm run.
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _get_flask_app():
    """Import and return the Flask app for DB context."""
    from app_config import create_app
    return create_app()


def run_algorithm_sync(
    algorithm_id: str,
    version: Optional[str],
    params_dict: Dict,
) -> Dict:
    """
    Run an algorithm synchronously within a Flask app context.

    This is the core function used by both sync and async paths.
    """
    app = _get_flask_app()

    with app.app_context():
        from auth.models import db
        from services.evidence_store import EvidenceStore
        from services.audit_stream import AuditStream
        from algorithms.base import AlgorithmParams
        from algorithms.registry import registry

        # Ensure all algorithms are registered
        import algorithms.bulk_dedup  # noqa: F401
        import algorithms.provenance_graph  # noqa: F401
        import algorithms.timeline_alignment  # noqa: F401
        import algorithms.integrity_sweep  # noqa: F401
        import algorithms.bates_generator  # noqa: F401
        import algorithms.redaction_verify  # noqa: F401
        import algorithms.access_anomaly  # noqa: F401

        algo = registry.get(algorithm_id, version)
        if not algo:
            return {"success": False, "error": f"Algorithm '{algorithm_id}' not found"}

        params = AlgorithmParams(**params_dict)

        store = EvidenceStore()
        audit = AuditStream(db.session, store)
        context = {
            "db_session": db.session,
            "evidence_store": store,
            "audit_stream": audit,
        }

        result = algo.run(params, context)

        # Store run record
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
            logger.warning("Failed to store algo run %s: %s", result.run_id, exc)
            db.session.rollback()

        return result.to_dict()


# ---------------------------------------------------------------------------
# Celery task (only defined if Celery is available)
# ---------------------------------------------------------------------------

try:
    from celery_app import celery_app

    if celery_app is not None:
        @celery_app.task(
            name="tasks.algorithm_tasks.run_algorithm_task",
            bind=True,
            max_retries=1,
            soft_time_limit=540,
            time_limit=600,
        )
        def run_algorithm_task(self, algorithm_id, version, params_dict):
            """Celery task wrapper for algorithm execution."""
            try:
                return run_algorithm_sync(algorithm_id, version, params_dict)
            except Exception as exc:
                logger.error("Algorithm task failed: %s", exc, exc_info=True)
                raise self.retry(exc=exc, countdown=30)
    else:
        run_algorithm_task = None

except ImportError:
    run_algorithm_task = None


# ---------------------------------------------------------------------------
# Dispatch (async or sync)
# ---------------------------------------------------------------------------

def dispatch_algorithm(
    algorithm_id: str,
    version: Optional[str],
    params_dict: Dict,
) -> Dict:
    """
    Dispatch an algorithm run (async via Celery or sync fallback).

    Returns a dict with execution metadata.
    """
    from celery_app import ASYNC_ENABLED

    if ASYNC_ENABLED and run_algorithm_task is not None:
        result = run_algorithm_task.delay(algorithm_id, version, params_dict)
        return {
            "async": True,
            "celery_task_id": result.id,
            "algorithm_id": algorithm_id,
        }

    # Sync fallback
    sync_result = run_algorithm_sync(algorithm_id, version, params_dict)
    sync_result["async"] = False
    return sync_result
