"""Evident Discovery Suite — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import cases_router, evidence_router, manifest_router
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
    # Run DB migrations
    _run_migrations()
    # Ensure MinIO bucket exists
    try:
        ensure_bucket()
    except Exception as exc:
        logger.warning("MinIO bucket check failed (will retry on first use): %s", exc)
    yield


app = FastAPI(title="Evident Discovery Suite", version="0.0.1", lifespan=lifespan)

# ── Routers ──────────────────────────────────────────────────────────
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(manifest_router)


@app.get("/health")
def health():
    return {"status": "ok"}
