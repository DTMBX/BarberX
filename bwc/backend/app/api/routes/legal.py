"""Legal search routes — CourtListener integration endpoint."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas import CourtListenerOpinionResult, CourtListenerSearchRequest
from app.core.database import get_db
from app.services.courtlistener import search_with_cache

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/search", response_model=list[CourtListenerOpinionResult])
def legal_search(
    q: str = Query(..., min_length=1, max_length=1024, description="Search query"),
    jurisdiction: Optional[str] = Query(None, description="Court/jurisdiction filter"),
    court: Optional[str] = Query(None, description="Specific court slug"),
    date_from: Optional[str] = Query(None, description="Date filed after (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Date filed before (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Search CourtListener for opinions matching the query.

    Results are cached in Postgres for 24h to avoid repeated API calls.
    All results come from CourtListener — no invented citations.
    """
    result = search_with_cache(
        db_session=db,
        query=q,
        court=court or jurisdiction,
        date_after=date_from,
        date_before=date_to,
        page=page,
    )

    # Normalize CourtListener response into our opinion result schema
    opinions = []
    for item in result.get("results", []):
        opinions.append(
            CourtListenerOpinionResult(
                id=item.get("id", 0),
                absolute_url=item.get("absolute_url"),
                case_name=item.get("caseName") or item.get("case_name"),
                court=item.get("court"),
                date_filed=item.get("dateFiled") or item.get("date_filed"),
                snippet=item.get("snippet"),
                citation_count=item.get("citeCount") or item.get("citation_count"),
                cluster_id=item.get("cluster_id"),
            )
        )
    return opinions
