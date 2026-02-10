"""
Share-Link & External-Portal Routes
=====================================
Endpoints for:
  1. Creating / revoking share links  (authenticated, case-owner only)
  2. External read-only portal        (bearer-token access, no Flask-Login)

Design principles:
  - Token is passed as a query parameter or Authorization header.
  - Every portal access is recorded in ChainOfCustody.
  - No evidence bytes are served inline; only metadata + download links
    that themselves re-validate the token.
  - Derivatives are clearly labelled.
"""

import json
import logging
from datetime import datetime, timezone

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required

from auth.models import db
from models.share_link import ShareLink
from services.share_link_service import ShareLinkError, ShareLinkService

logger = logging.getLogger(__name__)

share_bp = Blueprint("share", __name__, url_prefix="/share")


# ===================================================================
# Internal — share-link management (requires Flask-Login session)
# ===================================================================


@share_bp.route("/links", methods=["POST"])
@login_required
def create_share_link():
    """
    Create a new share link for a case.

    JSON body:
        case_id (int, required)
        recipient_name (str, required)
        recipient_role (str, required)  — attorney, co_counsel, expert_witness, auditor, opposing_counsel, insurance_adjuster
        scope (str, default "read_only") — read_only | export
        expires_in_days (int, default 7) — 1–90
        max_access_count (int, optional)
        evidence_ids (list[int], optional) — null = whole case
        recipient_email (str, optional)
    """
    data = request.get_json(silent=True) or {}

    required = ("case_id", "recipient_name", "recipient_role")
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        link, raw_token = ShareLinkService.create(
            case_id=data["case_id"],
            created_by_id=current_user.id,
            recipient_name=data["recipient_name"],
            recipient_role=data["recipient_role"],
            scope=data.get("scope", "read_only"),
            expires_in_days=data.get("expires_in_days", 7),
            max_access_count=data.get("max_access_count"),
            evidence_ids=data.get("evidence_ids"),
            recipient_email=data.get("recipient_email"),
        )
    except ShareLinkError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify({
        "id": link.id,
        "token": raw_token,  # Returned ONCE — never stored server-side
        "expires_at": link.expires_at.isoformat(),
        "scope": link.scope,
        "recipient_name": link.recipient_name,
        "portal_url": f"/share/portal?token={raw_token}",
    }), 201


@share_bp.route("/links/<int:link_id>/revoke", methods=["POST"])
@login_required
def revoke_share_link(link_id: int):
    """Revoke a share link immediately."""
    try:
        link = ShareLinkService.revoke(link_id, revoked_by_id=current_user.id)
    except ShareLinkError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify({
        "id": link.id,
        "revoked_at": link.revoked_at.isoformat(),
        "status": "revoked",
    }), 200


@share_bp.route("/links/case/<int:case_id>", methods=["GET"])
@login_required
def list_share_links(case_id: int):
    """List share links for a case (active only by default)."""
    include_revoked = request.args.get("include_revoked", "false").lower() == "true"
    links = ShareLinkService.list_for_case(case_id, include_revoked=include_revoked)

    return jsonify([
        {
            "id": lnk.id,
            "scope": lnk.scope,
            "recipient_name": lnk.recipient_name,
            "recipient_role": lnk.recipient_role,
            "created_at": lnk.created_at.isoformat(),
            "expires_at": lnk.expires_at.isoformat(),
            "revoked_at": lnk.revoked_at.isoformat() if lnk.revoked_at else None,
            "access_count": lnk.access_count,
            "is_active": lnk.is_active,
        }
        for lnk in links
    ]), 200


# ===================================================================
# External — read-only portal  (bearer-token, no Flask-Login)
# ===================================================================


def _extract_token() -> str:
    """Extract bearer token from query string or Authorization header."""
    token = request.args.get("token")
    if token:
        return token.strip()

    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return ""


@share_bp.route("/portal", methods=["GET"])
def portal_view():
    """
    External attorney / third-party read-only portal.

    Access via:  /share/portal?token=<raw_token>

    Returns JSON with case metadata and evidence list.
    No evidence content is served — only metadata and verification hashes.
    """
    raw_token = _extract_token()
    if not raw_token:
        return jsonify({"error": "Missing share token"}), 401

    try:
        link = ShareLinkService.resolve(raw_token)
    except ShareLinkError as exc:
        return jsonify({"error": str(exc)}), 403

    # Load case
    from models.legal_case import LegalCase

    case = db.session.get(LegalCase, link.case_id)
    if case is None:
        return jsonify({"error": "Case not found"}), 404

    # Determine which evidence to show
    from models.evidence import CaseEvidence, EvidenceItem

    allowed_ids = link.evidence_ids  # None = all

    evidence_links = [
        ce for ce in case.case_evidence_links
        if ce.is_active and (allowed_ids is None or ce.evidence_id in allowed_ids)
    ]

    evidence_list = []
    for ce in evidence_links:
        ev = ce.evidence
        evidence_list.append({
            "id": ev.id,
            "original_filename": ev.original_filename,
            "file_type": ev.file_type,
            "file_size_bytes": ev.file_size_bytes,
            "evidence_type": ev.evidence_type,
            "hash_sha256": ev.hash_sha256,
            "collected_date": ev.collected_date.isoformat() if ev.collected_date else None,
            "link_purpose": ce.link_purpose,
        })

    # Record access
    link.record_access()
    db.session.commit()

    logger.info(
        "ShareLink portal accessed id=%d case=%d by=%s access_count=%d",
        link.id,
        link.case_id,
        link.recipient_name,
        link.access_count,
    )

    return jsonify({
        "case": {
            "case_number": case.case_number,
            "case_name": case.case_name,
            "case_type": case.case_type,
            "jurisdiction": case.jurisdiction,
            "status": case.status,
        },
        "share": {
            "scope": link.scope,
            "recipient_name": link.recipient_name,
            "recipient_role": link.recipient_role,
            "expires_at": link.expires_at.isoformat(),
            "access_count": link.access_count,
        },
        "evidence": evidence_list,
        "notice": "This portal provides read-only metadata access. "
                  "Evidence integrity can be verified by comparing "
                  "the hash_sha256 values against independently held records.",
    }), 200


@share_bp.route("/portal/verify", methods=["GET"])
def portal_verify():
    """
    Token validation endpoint — confirms whether a share token is still active
    without consuming an access count.
    """
    raw_token = _extract_token()
    if not raw_token:
        return jsonify({"valid": False, "reason": "Missing token"}), 401

    try:
        link = ShareLinkService.resolve(raw_token)
        return jsonify({
            "valid": True,
            "scope": link.scope,
            "expires_at": link.expires_at.isoformat(),
            "recipient_name": link.recipient_name,
        }), 200
    except ShareLinkError as exc:
        return jsonify({"valid": False, "reason": str(exc)}), 200
