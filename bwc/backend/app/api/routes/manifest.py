"""GET /cases/{case_id}/export/manifest — canonical JSON manifest + SHA-256."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import AuditEventOut, CaseOut, EvidenceOut, ManifestOut
from app.core.config import settings
from app.core.database import get_db
from app.models.audit_event import AuditEvent
from app.models.case import Case
from app.models.evidence_file import EvidenceFile
from app.services.hashing import hmac_sha256, sha256_hex_str

router = APIRouter(tags=["manifest"])


@router.get("/cases/{case_id}/export/manifest", response_model=ManifestOut)
def export_manifest(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence = (
        db.query(EvidenceFile)
        .filter(EvidenceFile.case_id == case_id)
        .order_by(EvidenceFile.uploaded_at)
        .all()
    )
    audit = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at)
        .all()
    )

    # Build serializable dicts
    case_dict = CaseOut.model_validate(case).model_dump(mode="json")
    evidence_list = [EvidenceOut.model_validate(e).model_dump(mode="json") for e in evidence]
    audit_list = [AuditEventOut.model_validate(a).model_dump(mode="json") for a in audit]

    # Canonical JSON for hashing (sorted keys, no extra whitespace)
    hashable = {
        "case": case_dict,
        "evidence": evidence_list,
        "audit": audit_list,
    }
    canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
    manifest_sha256 = sha256_hex_str(canonical)

    # ── HMAC signature (cryptographic proof of manifest integrity) ────
    manifest_hmac = hmac_sha256(settings.manifest_hmac_key, canonical)

    return ManifestOut(
        case=case_dict,
        evidence=evidence_list,
        audit=audit_list,
        manifest_sha256=manifest_sha256,
        manifest_hmac=manifest_hmac,
    )
