"""
Review Search Service — Phase 10
==================================
Enhanced search with boolean operators, phrase matching, filters,
pagination, deterministic sort, and query audit logging.

Design principles:
  - Case-scoped: every search is within a single case.
  - Deterministic: same query + filters → same result order.
  - Audited: every search query is logged.
  - No AI interpretation of evidence content.
"""

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from flask import request as flask_request
from sqlalchemy import and_, or_, func, desc, asc

logger = logging.getLogger(__name__)


class ReviewSearchService:
    """
    Full-text search across evidence items indexed in ContentExtractionIndex.

    Supports:
      - Exact phrase matching (quoted strings)
      - AND/OR boolean operators
      - Filters: date_from, date_to, file_type, has_ocr, custodian/sender
      - Pagination with deterministic sort
      - Query audit logging
    """

    # Maximum results per page
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 50

    def __init__(self, db_session):
        self._db = db_session

    def search(
        self,
        case_id: int,
        query_text: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        sort_by: str = "relevance",
        sort_order: str = "desc",
        actor_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a search query against case evidence.

        Args:
            case_id: Case to search within.
            query_text: Search query string (supports phrases + boolean).
            filters: Dict of filters (date_from, date_to, file_type, has_ocr, custodian).
            page: 1-indexed page number.
            page_size: Results per page (max 100).
            sort_by: 'relevance', 'date', 'filename', 'file_type'.
            sort_order: 'asc' or 'desc'.
            actor_id: User performing the search (for audit).

        Returns:
            Dict with results, pagination, and search metadata.
        """
        from models.document_processing import ContentExtractionIndex
        from models.evidence import EvidenceItem, CaseEvidence
        from models.review import ReviewDecision

        filters = filters or {}
        page_size = min(max(page_size, 1), self.MAX_PAGE_SIZE)
        page = max(page, 1)

        # ---- Build base query: evidence items linked to this case ----
        base_query = (
            self._db.query(
                EvidenceItem,
                ContentExtractionIndex,
            )
            .outerjoin(
                ContentExtractionIndex,
                ContentExtractionIndex.evidence_id == EvidenceItem.id,
            )
            .join(
                CaseEvidence,
                and_(
                    CaseEvidence.evidence_id == EvidenceItem.id,
                    CaseEvidence.case_id == case_id,
                    CaseEvidence.unlinked_at.is_(None),
                ),
            )
        )

        # ---- Apply text search ----
        if query_text and query_text.strip():
            text_conditions = self._parse_query(query_text, ContentExtractionIndex)
            if text_conditions is not None:
                base_query = base_query.filter(text_conditions)

        # ---- Apply filters ----
        base_query = self._apply_filters(base_query, filters, EvidenceItem, ContentExtractionIndex)

        # ---- Count total results (before pagination) ----
        total_count = base_query.count()

        # ---- Apply sort ----
        base_query = self._apply_sort(base_query, sort_by, sort_order, EvidenceItem, ContentExtractionIndex)

        # ---- Apply pagination ----
        offset = (page - 1) * page_size
        results = base_query.offset(offset).limit(page_size).all()

        # ---- Fetch current review decisions for these evidence items ----
        evidence_ids = [ev.id for ev, _ in results]
        current_decisions = {}
        if evidence_ids:
            decisions = (
                ReviewDecision.query
                .filter(
                    ReviewDecision.case_id == case_id,
                    ReviewDecision.evidence_id.in_(evidence_ids),
                    ReviewDecision.is_current.is_(True),
                )
                .all()
            )
            for d in decisions:
                current_decisions[d.evidence_id] = d.to_dict()

        # ---- Format response ----
        items = []
        for evidence, content_idx in results:
            snippet = ""
            if query_text and content_idx and content_idx.full_text:
                snippet = self._extract_snippet(content_idx.full_text, query_text)

            item = {
                "evidence_id": evidence.id,
                "original_filename": evidence.original_filename,
                "file_type": evidence.file_type,
                "mime_type": evidence.mime_type,
                "file_size_bytes": evidence.file_size_bytes,
                "evidence_type": evidence.evidence_type,
                "collected_date": evidence.collected_date.isoformat() if evidence.collected_date else None,
                "collected_by": evidence.collected_by,
                "processing_status": evidence.processing_status,
                "has_ocr": evidence.has_ocr,
                "has_text": bool(content_idx and content_idx.full_text),
                "word_count": content_idx.word_count if content_idx else None,
                "snippet": snippet,
                "created_at": evidence.created_at.isoformat() if evidence.created_at else None,
                "review_decision": current_decisions.get(evidence.id),
            }
            items.append(item)

        # ---- Audit log the search ----
        self._log_search(
            case_id=case_id,
            actor_id=actor_id,
            query_text=query_text,
            filters=filters,
            total_results=total_count,
        )

        total_pages = max(1, (total_count + page_size - 1) // page_size)

        return {
            "query": query_text,
            "filters": filters,
            "results": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_results": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            "sort": {"sort_by": sort_by, "sort_order": sort_order},
        }

    # ------------------------------------------------------------------
    # Query parsing (boolean + phrase)
    # ------------------------------------------------------------------

    def _parse_query(self, query_text: str, IndexModel):
        """
        Parse a search query string into SQLAlchemy filter conditions.

        Supports:
          - Quoted phrases: "exact phrase"
          - AND operator (explicit or implicit between terms)
          - OR operator (explicit)
          - Simple terms

        Returns a SQLAlchemy condition or None.
        """
        query_text = query_text.strip()
        if not query_text:
            return None

        # Extract quoted phrases
        phrases = re.findall(r'"([^"]+)"', query_text)
        # Remove quoted phrases from query to get remaining terms
        remaining = re.sub(r'"[^"]*"', " ", query_text).strip()

        # Split remaining by OR (case-insensitive)
        or_groups = re.split(r"\bOR\b", remaining, flags=re.IGNORECASE)

        all_conditions = []

        # Add phrase conditions (AND with everything)
        for phrase in phrases:
            phrase = phrase.strip()
            if phrase:
                all_conditions.append(self._text_match(IndexModel, phrase))

        # Process OR groups
        if len(or_groups) > 1:
            or_conditions = []
            for group in or_groups:
                terms = self._extract_terms(group)
                if terms:
                    group_conds = [self._text_match(IndexModel, t) for t in terms]
                    or_conditions.append(and_(*group_conds) if len(group_conds) > 1 else group_conds[0])
            if or_conditions:
                all_conditions.append(or_(*or_conditions))
        else:
            # No OR — treat as AND between all terms
            terms = self._extract_terms(remaining)
            for term in terms:
                all_conditions.append(self._text_match(IndexModel, term))

        if not all_conditions:
            return None

        return and_(*all_conditions) if len(all_conditions) > 1 else all_conditions[0]

    def _extract_terms(self, text: str) -> List[str]:
        """Extract individual search terms, ignoring AND keyword."""
        words = text.split()
        return [w for w in words if w.upper() != "AND" and w.strip()]

    def _text_match(self, IndexModel, term: str):
        """Generate ILIKE condition across all searchable fields."""
        pattern = f"%{term}%"
        return or_(
            IndexModel.full_text.ilike(pattern),
            IndexModel.persons.ilike(pattern),
            IndexModel.organizations.ilike(pattern),
            IndexModel.email_addresses.ilike(pattern),
            IndexModel.phone_numbers.ilike(pattern),
            IndexModel.key_phrases.ilike(pattern),
        )

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def _apply_filters(self, query, filters, EvidModel, IndexModel):
        """Apply structured filters to the query."""

        # Date range (collected_date)
        if filters.get("date_from"):
            try:
                dt = datetime.fromisoformat(filters["date_from"])
                query = query.filter(EvidModel.collected_date >= dt)
            except (ValueError, TypeError):
                pass

        if filters.get("date_to"):
            try:
                dt = datetime.fromisoformat(filters["date_to"])
                query = query.filter(EvidModel.collected_date <= dt)
            except (ValueError, TypeError):
                pass

        # File type filter
        if filters.get("file_type"):
            file_types = filters["file_type"]
            if isinstance(file_types, str):
                file_types = [ft.strip() for ft in file_types.split(",")]
            query = query.filter(EvidModel.file_type.in_(file_types))

        # Has OCR
        if filters.get("has_ocr") is not None:
            has_ocr = filters["has_ocr"]
            if isinstance(has_ocr, str):
                has_ocr = has_ocr.lower() in ("true", "1", "yes")
            query = query.filter(EvidModel.has_ocr == has_ocr)

        # Custodian / collected_by
        if filters.get("custodian"):
            pattern = f"%{filters['custodian']}%"
            query = query.filter(EvidModel.collected_by.ilike(pattern))

        # Evidence type
        if filters.get("evidence_type"):
            query = query.filter(EvidModel.evidence_type == filters["evidence_type"])

        # Processing status
        if filters.get("processing_status"):
            query = query.filter(EvidModel.processing_status == filters["processing_status"])

        # Review code (current decision)
        if filters.get("review_code"):
            from models.review import ReviewDecision
            subq = (
                self._db.query(ReviewDecision.evidence_id)
                .filter(
                    ReviewDecision.is_current.is_(True),
                    ReviewDecision.review_code == filters["review_code"],
                )
                .subquery()
            )
            query = query.filter(EvidModel.id.in_(subq))

        # Uncoded only
        if filters.get("uncoded"):
            from models.review import ReviewDecision
            coded_subq = (
                self._db.query(ReviewDecision.evidence_id)
                .filter(ReviewDecision.is_current.is_(True))
                .subquery()
            )
            query = query.filter(~EvidModel.id.in_(coded_subq))

        return query

    # ------------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------------

    def _apply_sort(self, query, sort_by, sort_order, EvidModel, IndexModel):
        """Apply deterministic sort to results."""
        direction = desc if sort_order == "desc" else asc

        if sort_by == "date":
            query = query.order_by(direction(EvidModel.collected_date), EvidModel.id)
        elif sort_by == "filename":
            query = query.order_by(direction(EvidModel.original_filename), EvidModel.id)
        elif sort_by == "file_type":
            query = query.order_by(direction(EvidModel.file_type), EvidModel.id)
        elif sort_by == "size":
            query = query.order_by(direction(EvidModel.file_size_bytes), EvidModel.id)
        else:
            # Default: created_at descending, then id for determinism
            query = query.order_by(desc(EvidModel.created_at), EvidModel.id)

        return query

    # ------------------------------------------------------------------
    # Snippets
    # ------------------------------------------------------------------

    def _extract_snippet(self, text: str, query: str, context_chars: int = 150) -> str:
        """Extract a snippet around the first match of any query term."""
        if not text or not query:
            return ""

        # Try first quoted phrase, then first term
        phrases = re.findall(r'"([^"]+)"', query)
        terms = phrases if phrases else [t for t in query.split() if t.upper() not in ("AND", "OR")]

        lower_text = text.lower()
        for term in terms:
            pos = lower_text.find(term.lower())
            if pos != -1:
                start = max(0, pos - context_chars)
                end = min(len(text), pos + len(term) + context_chars)
                snippet = text[start:end]
                if start > 0:
                    snippet = "…" + snippet
                if end < len(text):
                    snippet = snippet + "…"
                return snippet

        # Fallback: first N characters
        limit = context_chars * 2
        return text[:limit] + ("…" if len(text) > limit else "")

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------
    # Audit sensitivity constants
    # ------------------------------------------------------------------
    _QUERY_LOG_MAX_CHARS = 120   # Truncate search text in audit log
    _SAFE_FILTER_KEYS = frozenset({
        "file_type", "date_from", "date_to", "has_ocr",
        "evidence_type", "processing_status", "review_code", "uncoded",
    })
    # 'custodian' is omitted — may contain PII (names). Log presence only.

    # ------------------------------------------------------------------

    def _log_search(
        self,
        case_id: int,
        actor_id: Optional[int],
        query_text: Optional[str],
        filters: Dict,
        total_results: int,
    ):
        """Log search query to review audit events.

        Audit sensitivity rules:
          - Query text is truncated to _QUERY_LOG_MAX_CHARS.
          - PII-bearing filter values (e.g. custodian) are logged as
            presence indicators ("***") rather than verbatim values.
        """
        if not actor_id:
            return

        try:
            from models.review import ReviewAuditEvent

            ip = None
            try:
                ip = flask_request.remote_addr
            except RuntimeError:
                pass

            # Truncate query text
            safe_query = None
            if query_text:
                if len(query_text) > self._QUERY_LOG_MAX_CHARS:
                    safe_query = query_text[: self._QUERY_LOG_MAX_CHARS] + "…"
                else:
                    safe_query = query_text

            # Redact PII-bearing filter values
            safe_filters = {}
            for key, val in (filters or {}).items():
                if key in self._SAFE_FILTER_KEYS:
                    safe_filters[key] = val
                else:
                    # Log presence but redact the value
                    safe_filters[key] = "***"

            event = ReviewAuditEvent(
                case_id=case_id,
                evidence_id=None,
                action="review.search",
                actor_id=actor_id,
                details_json=json.dumps({
                    "query": safe_query,
                    "filters": safe_filters,
                    "total_results": total_results,
                }, default=str),
                ip_address=ip,
            )
            self._db.add(event)
            self._db.commit()
        except Exception as exc:
            logger.warning("Failed to log search audit: %s", exc)
            self._db.rollback()
