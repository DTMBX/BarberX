"""
Celery Application Configuration
==================================
Async task queue for evidence processing with sync fallback.

Environment variables:
  EVIDENT_ASYNC       — '1' (default) for Celery, '0' for synchronous execution
  CELERY_BROKER_URL   — Redis URL (default: redis://localhost:6379/0)
  CELERY_RESULT_URL   — Result backend URL (default: same as broker)

Usage:
  # Start worker:
  celery -A celery_app worker --loglevel=info --pool=solo

  # Sync mode (no Redis required):
  set EVIDENT_ASYNC=0
"""

import os
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ASYNC_ENABLED = os.environ.get("EVIDENT_ASYNC", "1") == "1"
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_URL = os.environ.get("CELERY_RESULT_URL", BROKER_URL)


# ---------------------------------------------------------------------------
# Celery app (lazy — only created if async mode is on)
# ---------------------------------------------------------------------------

celery_app = None

if ASYNC_ENABLED:
    try:
        from celery import Celery

        celery_app = Celery(
            "evident",
            broker=BROKER_URL,
            backend=RESULT_URL,
        )

        celery_app.conf.update(
            # Serialization
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],

            # Timeouts & retries
            task_time_limit=600,        # 10 min hard kill
            task_soft_time_limit=540,   # 9 min soft limit (raises SoftTimeLimitExceeded)
            task_acks_late=True,        # ACK only after task completes (at-least-once)
            worker_prefetch_multiplier=1,  # One task at a time per worker

            # Result expiry
            result_expires=3600,  # 1 hour

            # Task discovery
            include=["tasks.processing_tasks"],

            # Retry policy for broker connection
            broker_connection_retry_on_startup=True,
        )

        logger.info("Celery configured: broker=%s, backend=%s", BROKER_URL, RESULT_URL)

    except ImportError:
        logger.warning("Celery not installed — falling back to synchronous mode")
        ASYNC_ENABLED = False
        celery_app = None

    except Exception as exc:
        logger.warning("Celery init failed (%s) — falling back to synchronous mode", exc)
        ASYNC_ENABLED = False
        celery_app = None

else:
    logger.info("Synchronous mode enabled (EVIDENT_ASYNC=0)")


def is_async() -> bool:
    """Return True if async task execution is available."""
    return ASYNC_ENABLED and celery_app is not None
