"""Artifacts routes — list derived artifacts for a case or evidence file."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas import EvidenceArtifactOut
from app.core.database import get_db
from app.models.evidence_artifact import EvidenceArtifact

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=list[EvidenceArtifactOut])
def list_artifacts(
    case_id: Optional[uuid.UUID] = Query(None),
    evidence_id: Optional[uuid.UUID] = Query(None),
    artifact_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List artifacts, optionally filtered by case_id, evidence_id, or type."""
    q = db.query(EvidenceArtifact).order_by(EvidenceArtifact.created_at.desc())
    if case_id is not None:
        q = q.filter(EvidenceArtifact.case_id == case_id)
    if evidence_id is not None:
        q = q.filter(EvidenceArtifact.evidence_id == evidence_id)
    if artifact_type is not None:
        q = q.filter(EvidenceArtifact.artifact_type == artifact_type)
    return q.limit(500).all()
