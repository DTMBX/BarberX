"""Pydantic request / response schemas for the API layer."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Projects ─────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)
    description: str | None = None
    created_by: str = Field(..., min_length=1, max_length=256)


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Cases ────────────────────────────────────────────────────────────


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    created_by: str = Field(..., min_length=1, max_length=256)
    project_id: uuid.UUID | None = None


class CaseOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID | None = None
    title: str
    created_by: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Evidence ─────────────────────────────────────────────────────────


class EvidenceInitRequest(BaseModel):
    case_id: uuid.UUID
    filename: str = Field(..., min_length=1, max_length=1024)
    content_type: str = Field(..., min_length=1, max_length=256)
    size_bytes: int = Field(..., gt=0)


class EvidenceInitResponse(BaseModel):
    evidence_id: uuid.UUID
    upload_url: str


class EvidenceBatchFileInfo(BaseModel):
    filename: str = Field(..., min_length=1, max_length=1024)
    content_type: str = Field(..., min_length=1, max_length=256)
    size_bytes: int = Field(..., gt=0)


class EvidenceBatchInitRequest(BaseModel):
    case_id: uuid.UUID
    files: list[EvidenceBatchFileInfo]


class EvidenceBatchInitResponse(BaseModel):
    items: list[EvidenceInitResponse]


class EvidenceCompleteRequest(BaseModel):
    evidence_id: uuid.UUID


class EvidenceOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    original_filename: str
    content_type: str
    size_bytes: int
    sha256: str | None
    minio_object_key: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ── Evidence Artifacts ───────────────────────────────────────────────


class EvidenceArtifactOut(BaseModel):
    id: uuid.UUID
    evidence_id: uuid.UUID
    case_id: uuid.UUID
    artifact_type: str
    minio_object_key: str
    sha256: str | None
    content_preview: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Jobs ─────────────────────────────────────────────────────────────


class JobEnqueueRequest(BaseModel):
    evidence_ids: list[uuid.UUID]
    tasks: list[str] = Field(
        default=["ocr", "transcribe", "metadata"],
        description="Task types to run: ocr, transcribe, metadata",
    )


class JobOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    evidence_id: uuid.UUID
    task_type: str | None = None
    status: str
    error_detail: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Issues / Violations ──────────────────────────────────────────────


class IssueCreate(BaseModel):
    case_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=512)
    narrative: str = Field(..., min_length=1)
    jurisdiction: str | None = None
    code_reference: str | None = None
    courtlistener_cites: list | None = None
    supporting_sources: list = Field(default_factory=list)
    confidence: str = Field(default="medium")
    status: str = Field(default="open")
    created_by: str = Field(default="user")


class IssueOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    title: str
    narrative: str
    jurisdiction: str | None
    code_reference: str | None
    courtlistener_cites: list | None
    supporting_sources: list
    confidence: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Timeline ─────────────────────────────────────────────────────────


class TimelineEvent(BaseModel):
    timestamp: datetime
    event_type: str
    description: str
    evidence_id: uuid.UUID | None = None
    metadata: dict | None = None


# ── Audit ────────────────────────────────────────────────────────────


class AuditEventOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID | None
    event_type: str
    payload_json: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ── Manifest ─────────────────────────────────────────────────────────


class ManifestOut(BaseModel):
    case: CaseOut
    evidence: list[EvidenceOut]
    audit: list[AuditEventOut]
    manifest_sha256: str
    manifest_hmac: str


# ── Chat ─────────────────────────────────────────────────────────────


class ChatAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4096)
    scope: str = Field(default="global")  # global, project, case
    project_id: uuid.UUID | None = None
    case_id: uuid.UUID | None = None


class ChatCitation(BaseModel):
    source_type: str  # internal, courtlistener, rag_context
    source_id: str | None = None
    url: str | None = None
    title: str | None = None
    snippet: str | None = None
    court: str | None = None
    date: str | None = None
    verification_status: str = "needs_verification"


class ChatAskResponse(BaseModel):
    message_id: uuid.UUID
    answer: str
    citations: list[ChatCitation]
    verification_status: str


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    scope: str
    project_id: uuid.UUID | None
    case_id: uuid.UUID | None
    role: str
    content: str
    citations: list | None
    verification_status: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ── CourtListener ────────────────────────────────────────────────────


class CourtListenerSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1024)
    court: str | None = None
    date_after: str | None = None
    date_before: str | None = None
    page: int = 1


class CourtListenerOpinionResult(BaseModel):
    id: int
    absolute_url: str | None = None
    case_name: str | None = None
    court: str | None = None
    date_filed: str | None = None
    snippet: str | None = None
    citation_count: int | None = None
    cluster_id: int | None = None
