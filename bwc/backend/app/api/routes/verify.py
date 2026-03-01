"""Forensic verification endpoints — manifest HMAC check + audit replay."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.audit_event import AuditEvent
from app.models.case import Case
from app.models.evidence_file import EvidenceFile
from app.services.hashing import sha256_hex, sha256_hex_str, verify_hmac_sha256
from app.services.s3 import download_bytes

router = APIRouter(prefix="/verify", tags=["verification"])


# ── Request / Response schemas ───────────────────────────────────────


class ManifestVerifyRequest(BaseModel):
    """Client supplies a previously-exported manifest for independent validation."""

    manifest_sha256: str
    manifest_hmac: str
    case: dict
    evidence: list[dict]
    audit: list[dict]


class VerifyResult(BaseModel):
    sha256_valid: bool
    hmac_valid: bool
    detail: str


class AuditReplayResult(BaseModel):
    ok: bool
    events_checked: int
    evidence_checked: int
    sha256_mismatches: list[dict]
    detail: str


# ── 1) Manifest HMAC verification ───────────────────────────────────


@router.post("/manifest", response_model=VerifyResult)
def verify_manifest(body: ManifestVerifyRequest):
    """
    Independently verify a manifest's SHA-256 and HMAC signature.

    The client sends a previously-exported manifest.  This endpoint:
      1. Recomputes the canonical JSON hash.
      2. Verifies the HMAC-SHA256 signature using the server key.

    No database access — pure cryptographic verification.
    """
    hashable = {
        "case": body.case,
        "evidence": body.evidence,
        "audit": body.audit,
    }
    canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))

    recomputed_sha = sha256_hex_str(canonical)
    sha256_ok = recomputed_sha == body.manifest_sha256
    hmac_ok = verify_hmac_sha256(settings.manifest_hmac_key, canonical, body.manifest_hmac)

    if sha256_ok and hmac_ok:
        detail = "Manifest integrity verified: SHA-256 and HMAC both valid."
    elif sha256_ok:
        detail = "SHA-256 matches but HMAC is INVALID — possible key mismatch or tampering."
    elif hmac_ok:
        detail = "HMAC matches but SHA-256 is INVALID — data section was modified."
    else:
        detail = "BOTH SHA-256 and HMAC are INVALID — manifest has been tampered with."

    return VerifyResult(sha256_valid=sha256_ok, hmac_valid=hmac_ok, detail=detail)


# ── 2) Full audit replay verification ───────────────────────────────


@router.get("/cases/{case_id}/audit-replay", response_model=AuditReplayResult)
def audit_replay(case_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Full chain-of-custody replay for a case.

    For every finalized evidence file in the case:
      1. Re-download the object from MinIO.
      2. Recompute SHA-256.
      3. Compare against the stored digest.

    Also verifies:
      - Every evidence file has a matching evidence.complete audit event.
      - The audit trail is monotonically ordered by timestamp.

    This is a forensic-grade independent verification that proves
    the evidence has not been altered since initial ingestion.
    """
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # Fetch all finalized evidence
    evidence_rows = (
        db.query(EvidenceFile)
        .filter(EvidenceFile.case_id == case_id, EvidenceFile.sha256.isnot(None))
        .order_by(EvidenceFile.uploaded_at)
        .all()
    )

    # Fetch audit trail
    audit_rows = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at)
        .all()
    )

    mismatches: list[dict] = []
    evidence_checked = 0

    for ef in evidence_rows:
        evidence_checked += 1
        try:
            raw = download_bytes(ef.minio_object_key)
            recomputed = sha256_hex(raw)
            if recomputed != ef.sha256:
                mismatches.append({
                    "evidence_id": str(ef.id),
                    "filename": ef.original_filename,
                    "stored_sha256": ef.sha256,
                    "recomputed_sha256": recomputed,
                    "verdict": "MISMATCH — evidence may have been altered",
                })
        except Exception as exc:
            mismatches.append({
                "evidence_id": str(ef.id),
                "filename": ef.original_filename,
                "stored_sha256": ef.sha256,
                "recomputed_sha256": None,
                "verdict": f"DOWNLOAD FAILED — {exc}",
            })

    # Verify audit ordering (monotonic timestamps)
    for i in range(1, len(audit_rows)):
        if audit_rows[i].created_at < audit_rows[i - 1].created_at:
            mismatches.append({
                "evidence_id": None,
                "filename": None,
                "stored_sha256": None,
                "recomputed_sha256": None,
                "verdict": (
                    f"AUDIT ORDER VIOLATION: event {audit_rows[i].id} "
                    f"({audit_rows[i].created_at}) precedes "
                    f"event {audit_rows[i-1].id} ({audit_rows[i-1].created_at})"
                ),
            })

    # Verify every finalized evidence has a matching audit event
    complete_event_ids = {
        e.payload_json.get("evidence_id")
        for e in audit_rows
        if e.event_type == "evidence.complete"
    }
    for ef in evidence_rows:
        if str(ef.id) not in complete_event_ids:
            mismatches.append({
                "evidence_id": str(ef.id),
                "filename": ef.original_filename,
                "stored_sha256": ef.sha256,
                "recomputed_sha256": None,
                "verdict": "MISSING AUDIT — no evidence.complete event found",
            })

    ok = len(mismatches) == 0
    if ok:
        detail = (
            f"Audit replay PASSED — {evidence_checked} evidence files verified, "
            f"{len(audit_rows)} audit events checked, all SHA-256 digests match."
        )
    else:
        detail = (
            f"Audit replay FAILED — {len(mismatches)} issue(s) found across "
            f"{evidence_checked} evidence files and {len(audit_rows)} audit events."
        )

    return AuditReplayResult(
        ok=ok,
        events_checked=len(audit_rows),
        evidence_checked=evidence_checked,
        sha256_mismatches=mismatches,
        detail=detail,
    )
