"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central config — every value has a sensible Docker-Compose default."""

    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Postgres
    database_url: str = Field(
        default="postgresql+psycopg://evident:evident@postgres:5432/evident"
    )

    # Redis / Celery
    redis_url: str = Field(default="redis://redis:6379/0")

    # S3-compatible (MinIO)
    s3_endpoint_url: str = Field(default="http://minio:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket: str = Field(default="evidence")
    s3_region: str = Field(default="us-east-1")

    # Audit
    audit_log_path: str = Field(default="/var/log/bwc/audit.jsonl")
    evidence_originals_prefix: str = Field(default="originals/")

    # Forensic signing — HMAC key for manifest signatures
    manifest_hmac_key: str = Field(
        default="CHANGE_ME_MANIFEST_HMAC_SECRET",
        description="HMAC-SHA256 key used to sign exported manifests.",
    )

    # S3 immutability — enable WORM-like write-once policy
    s3_immutable_policy: bool = Field(
        default=True,
        description="Apply deny-delete bucket policy on startup (WORM-like).",
    )

    # CourtListener API
    courtlistener_base_url: str = Field(
        default="https://www.courtlistener.com/api/rest/v4",
        description="CourtListener API base URL.",
    )
    courtlistener_api_token: str = Field(
        default="",
        description="CourtListener auth token (optional; empty = unauthenticated).",
    )

    # LLM provider for chat
    llm_provider: str = Field(
        default="disabled",
        description="LLM provider: openai | anthropic | local | disabled",
    )
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")

    # Safe mode — disables destructive endpoints
    evident_safe_mode: bool = Field(
        default=False,
        description="When true, DELETE endpoints are disabled.",
    )

    # Paths — resolved at import time so they work inside containers
    suite_root: str = Field(
        default_factory=lambda: os.getenv(
            "BWC_SUITE_ROOT",
            str(Path(__file__).resolve().parents[3]),  # bwc/
        )
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
