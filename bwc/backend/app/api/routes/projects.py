"""Projects API — top-level grouping for cases."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ProjectCreate, ProjectOut
from app.core.database import get_db
from app.models.project import Project
from app.services.audit import append_audit_event

import uuid

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=body.name,
        description=body.description,
        created_by=body.created_by,
    )
    db.add(project)
    db.flush()

    append_audit_event(
        db,
        case_id=None,
        event_type="project.created",
        payload={
            "project_id": str(project.id),
            "name": project.name,
            "created_by": project.created_by,
        },
    )

    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
