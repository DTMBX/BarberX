"""Cases API — CRUD endpoints for investigation cases."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import CaseCreate, CaseOut
from app.core.database import get_db
from app.models.case import Case
from app.services.audit import append_audit_event

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut, status_code=201)
def create_case(body: CaseCreate, db: Session = Depends(get_db)):
    case = Case(
        title=body.title,
        created_by=body.created_by,
        project_id=body.project_id,
    )
    db.add(case)
    db.flush()

    append_audit_event(
        db,
        case_id=case.id,
        event_type="case.created",
        payload={"title": case.title, "created_by": case.created_by},
    )

    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=list[CaseOut])
def list_cases(
    project_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Case).order_by(Case.created_at.desc())
    if project_id is not None:
        q = q.filter(Case.project_id == project_id)
    return q.all()


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
