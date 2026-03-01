"""Pytest configuration — in-memory SQLite test database & FastAPI TestClient."""

from __future__ import annotations

import os
import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# Override env BEFORE importing app modules so Settings picks up test values.
os.environ.update(
    {
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
        "S3_ENDPOINT_URL": "http://localhost:9000",
        "S3_ACCESS_KEY": "test",
        "S3_SECRET_KEY": "test",
        "S3_BUCKET": "test-evidence",
        "MANIFEST_HMAC_KEY": "test-hmac-key-for-pytest",
        "LLM_PROVIDER": "disabled",
        "EVIDENT_SAFE_MODE": "false",
        "COURTLISTENER_API_TOKEN": "",
        "APP_ENV": "test",
    }
)

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# ── Force all models to register on Base.metadata ──────────────────
import app.models  # noqa: E402, F401

# ── In-memory SQLite engine ────────────────────────────────────────

_engine = create_engine("sqlite:///:memory:", echo=False)

# SQLite doesn't enforce FK by default
@event.listens_for(_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_TestSession = sessionmaker(bind=_engine, class_=Session, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _create_tables():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Yield a test DB session."""
    session = _TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to in-memory DB, with S3 mocked."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    # Mock S3 operations globally for tests
    with (
        patch("app.services.s3.ensure_bucket"),
        patch("app.services.s3.presigned_put_url", return_value="https://minio.test/presigned"),
        patch("app.services.s3.get_s3_client", return_value=MagicMock()),
    ):
        with TestClient(app, raise_server_exceptions=False) as tc:
            yield tc

    app.dependency_overrides.clear()


@pytest.fixture()
def sample_case_id(db: Session) -> str:
    """Create a sample case and return its ID."""
    from app.models.case import Case

    case_id = str(uuid.uuid4())
    case = Case(id=case_id, title="Test Case", status="open", created_by="pytest")
    db.add(case)
    db.commit()
    return case_id


@pytest.fixture()
def sample_evidence(db: Session, sample_case_id: str):
    """Create a sample evidence file row."""
    from app.models.evidence_file import EvidenceFile

    eid = uuid.uuid4()
    ef = EvidenceFile(
        id=eid,
        case_id=sample_case_id,
        original_filename="test-video.mp4",
        content_type="video/mp4",
        size_bytes=1024,
        sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        minio_object_key=f"originals/{sample_case_id}/{eid}/test-video.mp4",
    )
    db.add(ef)
    db.commit()
    db.refresh(ef)
    return ef
