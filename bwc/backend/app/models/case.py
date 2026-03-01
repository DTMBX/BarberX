"""Case model — top-level entity for an investigation."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CaseStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    created_by: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status", create_constraint=True),
        default=CaseStatus.open,
        server_default="open",
    )

    # Relationships
    project = relationship("Project", back_populates="cases")
    evidence_files = relationship("EvidenceFile", back_populates="case", lazy="selectin")
    artifacts = relationship("EvidenceArtifact", back_populates="case", lazy="selectin")
    audit_events = relationship("AuditEvent", back_populates="case", lazy="selectin")
    jobs = relationship("Job", back_populates="case", lazy="selectin")
    issues = relationship("Issue", back_populates="case", lazy="selectin")
