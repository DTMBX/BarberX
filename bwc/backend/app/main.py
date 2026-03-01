"""Evident Discovery Suite — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    artifacts_router,
    cases_router,
    chat_router,
    evidence_router,
    issues_router,
    jobs_router,
    legal_router,
    manifest_router,
    projects_router,
    timeline_router,
    verify_router,
)
from app.core.config import settings
from app.services.s3 import ensure_bucket

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    """Apply pending Alembic migrations on startup."""
    try:
        from alembic import command
        from alembic.config import Config as AlembicConfig

        cfg = AlembicConfig("alembic.ini")
        command.upgrade(cfg, "head")
        logger.info("Alembic migrations applied.")
    except Exception as exc:
        logger.warning("Alembic migration skipped: %s", exc)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle hook."""
    import asyncio
    # Run DB migrations (with timeout to avoid hanging on bad connection)
    try:
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, _run_migrations),
            timeout=15,
        )
    except Exception as exc:
        logger.warning("DB migration skipped: %s", exc)
    # Ensure MinIO bucket exists (non-blocking — skip on failure)
    try:
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, ensure_bucket),
            timeout=10,
        )
    except Exception as exc:
        logger.warning("MinIO bucket check failed (will retry on first use): %s", exc)
    yield


app = FastAPI(title="Evident Discovery Suite", version="0.0.1", lifespan=lifespan)

# ── CORS ─────────────────────────────────────────────────────────────
# Allow frontend dev server (localhost:3000) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",  # Docker compose service name
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────
app.include_router(projects_router)
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(artifacts_router)
app.include_router(jobs_router)
app.include_router(issues_router)
app.include_router(manifest_router)
app.include_router(verify_router)
app.include_router(timeline_router)
app.include_router(chat_router)
app.include_router(legal_router)


@app.get("/health")
def health():
    """Health check with service status details."""
    from redis import Redis
    from sqlalchemy import text
    from app.core.database import engine
    from app.services.s3 import get_s3_client

    result = {
        "status": "healthy",
        "version": "0.0.1",
        "database": "disconnected",
        "redis": "disconnected",
        "minio": "disconnected",
    }

    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        result["database"] = "connected"
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        result["status"] = "degraded"

    # Check Redis
    try:
        r = Redis.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        result["redis"] = "connected"
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        result["status"] = "degraded"

    # Check MinIO
    try:
        s3 = get_s3_client()
        s3.head_bucket(Bucket=settings.s3_bucket)
        result["minio"] = "connected"
    except Exception as exc:
        logger.warning("MinIO health check failed: %s", exc)
        result["status"] = "degraded"

    return result
