"""Issue / Violation model — structured allegations with evidence pointers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Issue(Base):
    """
    Represents a structured allegation or identified violation within a case.

    Each issue captures:
    - A narrative description of the violation/allegation
    - Jurisdiction and optional legal code reference
    - Optional CourtListener citation IDs
    - Supporting source pointers (evidence_id, artifact_id, timecode, page, quote)
    - Confidence level and status tracking
    """

    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(
        String(512), nullable=False,
    )
    narrative: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Plain-language description of the alleged violation.",
    )
    jurisdiction: Mapped[str | None] = mapped_column(
        String(128), nullable=True,
        comment="State, federal, or other jurisdiction identifier.",
    )
    code_reference: Mapped[str | None] = mapped_column(
        String(512), nullable=True,
        comment="Statute, regulation, or policy reference (user-supplied, not invented).",
    )
    courtlistener_cites: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, default=list,
        comment="Array of CourtListener opinion/cluster IDs that support this issue.",
    )
    supporting_sources: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb"),
        comment=(
            "Array of source pointers: "
            '[{"evidence_id":"...","artifact_id":"...","timecode":"00:01:23","page":2,"quote":"..."}]'
        ),
    )
    confidence: Mapped[str] = mapped_column(
        String(32), nullable=False, default="medium",
        server_default="medium",
        comment="Confidence level: high, medium, low, unverified.",
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="open",
        server_default="open",
        comment="Status: open, confirmed, dismissed, resolved.",
    )
    created_by: Mapped[str] = mapped_column(
        String(256), nullable=False, default="system",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    case = relationship("Case", back_populates="issues")
