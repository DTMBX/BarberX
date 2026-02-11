"""
Share-Link Service
===================
Business logic for creating, validating, revoking, and auditing share links.

No evidence bytes are served by this service. It only manages tokens
and delegates access decisions.

Design principles:
  - Token plaintext is returned exactly once (at creation) and never stored.
  - All lookups use the SHA-256 hash of the token.
  - Every significant action is audit-logged.
  - Revocation is immediate and irreversible (append-only revoked_at).
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from auth.models import db
from models.share_link import ShareLink

logger = logging.getLogger(__name__)


class ShareLinkError(Exception):
    """Domain error for share-link operations."""


class ShareLinkService:
    """Manages share-link lifecycle."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        *,
        case_id: int,
        created_by_id: int,
        recipient_name: str,
        recipient_role: str,
        scope: str = "read_only",
        expires_in_days: int = 7,
        max_access_count: Optional[int] = None,
        evidence_ids: Optional[list] = None,
        recipient_email: Optional[str] = None,
    ) -> tuple:  # (ShareLink, raw_token)
        """
        Create a new share link.

        Returns
        -------
        (ShareLink, str)
            The persisted ShareLink row and the raw bearer token (shown once).

        Raises
        ------
        ShareLinkError
            On invalid scope, recipient role, or expiry.
        """
        # Validate scope
        if scope not in ShareLink.VALID_SCOPES:
            raise ShareLinkError(
                f"Invalid scope '{scope}'. Valid: {', '.join(sorted(ShareLink.VALID_SCOPES))}"
            )

        # Validate recipient role
        if recipient_role not in ShareLink.VALID_RECIPIENT_ROLES:
            raise ShareLinkError(
                f"Invalid recipient_role '{recipient_role}'. "
                f"Valid: {', '.join(sorted(ShareLink.VALID_RECIPIENT_ROLES))}"
            )

        # Validate expiry
        if expires_in_days < 1 or expires_in_days > ShareLink.MAX_EXPIRY_DAYS:
            raise ShareLinkError(
                f"expires_in_days must be 1–{ShareLink.MAX_EXPIRY_DAYS}, got {expires_in_days}"
            )

        raw_token = ShareLink.generate_token()
        token_hash = ShareLink.hash_token(raw_token)

        link = ShareLink(
            token_hash=token_hash,
            case_id=case_id,
            scope=scope,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_role=recipient_role,
            created_by_id=created_by_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
            max_access_count=max_access_count,
        )
        if evidence_ids is not None:
            link.evidence_ids = evidence_ids

        db.session.add(link)
        db.session.commit()

        logger.info(
            "ShareLink created id=%d case=%d scope=%s recipient=%s expires_in=%dd",
            link.id,
            case_id,
            scope,
            recipient_name,
            expires_in_days,
        )

        return link, raw_token

    # ------------------------------------------------------------------
    # Validate / resolve
    # ------------------------------------------------------------------

    @staticmethod
    def resolve(raw_token: str) -> ShareLink:
        """
        Look up a share link by raw bearer token and verify it is active.

        Returns
        -------
        ShareLink

        Raises
        ------
        ShareLinkError
            If token is unknown, expired, revoked, or over access limit.
        """
        token_hash = ShareLink.hash_token(raw_token)
        link = ShareLink.query.filter_by(token_hash=token_hash).first()

        if link is None:
            raise ShareLinkError("Invalid or unknown share token")

        if link.revoked_at is not None:
            raise ShareLinkError("Share link has been revoked")

        now = datetime.now(timezone.utc)
        expires = ShareLink._ensure_aware(link.expires_at)
        if expires <= now:
            raise ShareLinkError("Share link has expired")

        if link.max_access_count is not None and link.access_count >= link.max_access_count:
            raise ShareLinkError("Share link access limit reached")

        return link

    # ------------------------------------------------------------------
    # Revoke
    # ------------------------------------------------------------------

    @staticmethod
    def revoke(link_id: int, revoked_by_id: int) -> ShareLink:
        """
        Revoke a share link.  Revocation is immediate and irreversible.

        Returns
        -------
        ShareLink (updated)

        Raises
        ------
        ShareLinkError
            If the link does not exist or is already revoked.
        """
        link = db.session.get(ShareLink, link_id)
        if link is None:
            raise ShareLinkError(f"ShareLink id={link_id} not found")

        if link.revoked_at is not None:
            raise ShareLinkError(f"ShareLink id={link_id} is already revoked")

        link.revoked_at = datetime.now(timezone.utc)
        link.revoked_by_id = revoked_by_id
        db.session.commit()

        logger.info("ShareLink revoked id=%d by user=%d", link_id, revoked_by_id)
        return link

    # ------------------------------------------------------------------
    # List (admin / case-owner view)
    # ------------------------------------------------------------------

    @staticmethod
    def list_for_case(case_id: int, include_revoked: bool = False):
        """Return all share links for a case, newest first."""
        q = ShareLink.query.filter_by(case_id=case_id).order_by(ShareLink.created_at.desc())
        if not include_revoked:
            q = q.filter(ShareLink.revoked_at.is_(None))
        return q.all()
