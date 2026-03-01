"""Issues / Violations routes — CRUD for structured allegations."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import IssueCreate, IssueOut
from app.core.database import get_db
from app.models.case import Case
from app.models.issue import Issue
from app.services.audit import append_audit_event

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueOut, status_code=201)
def create_issue(body: IssueCreate, db: Session = Depends(get_db)):
    """Create a new issue/violation for a case."""
    case = db.get(Case, body.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    issue = Issue(
        case_id=body.case_id,
        title=body.title,
        narrative=body.narrative,
        jurisdiction=body.jurisdiction,
        code_reference=body.code_reference,
        courtlistener_cites=body.courtlistener_cites,
        supporting_sources=body.supporting_sources,
        confidence=body.confidence,
        status=body.status,
        created_by=body.created_by,
    )
    db.add(issue)

    append_audit_event(
        db,
        case_id=body.case_id,
        event_type="issue.created",
        payload={
            "issue_title": body.title,
            "confidence": body.confidence,
        },
    )

    db.commit()
    db.refresh(issue)
    return issue


@router.get("", response_model=list[IssueOut])
def list_issues(
    case_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List issues, optionally filtered by case_id and status."""
    q = db.query(Issue).order_by(Issue.created_at.desc())
    if case_id is not None:
        q = q.filter(Issue.case_id == case_id)
    if status is not None:
        q = q.filter(Issue.status == status)
    return q.limit(200).all()


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single issue by ID."""
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.patch("/{issue_id}", response_model=IssueOut)
def update_issue(
    issue_id: uuid.UUID,
    body: dict,
    db: Session = Depends(get_db),
):
    """Partial update for an issue (status, narrative, confidence, etc.)."""
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    allowed_fields = {
        "title", "narrative", "jurisdiction", "code_reference",
        "courtlistener_cites", "supporting_sources", "confidence", "status",
    }
    for key, value in body.items():
        if key in allowed_fields:
            setattr(issue, key, value)

    append_audit_event(
        db,
        case_id=issue.case_id,
        event_type="issue.updated",
        payload={"issue_id": str(issue_id), "fields": list(body.keys())},
    )

    db.commit()
    db.refresh(issue)
    return issue
