"""CourtListener API client — search opinions with caching."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TIMEOUT = 15.0


def _query_hash(query: str, court: str | None, date_after: str | None, date_before: str | None, page: int) -> str:
    """Deterministic hash of search params for caching."""
    key = f"{query}|{court}|{date_after}|{date_before}|{page}"
    return hashlib.sha256(key.encode()).hexdigest()


def search_opinions(
    query: str,
    court: str | None = None,
    date_after: str | None = None,
    date_before: str | None = None,
    page: int = 1,
) -> dict:
    """
    Search CourtListener opinions API.
    Returns the raw JSON response dict.
    """
    params: dict = {"q": query, "page": page, "order_by": "score desc"}
    if court:
        params["court"] = court
    if date_after:
        params["filed_after"] = date_after
    if date_before:
        params["filed_before"] = date_before

    headers: dict = {"Accept": "application/json"}
    if settings.courtlistener_api_token:
        headers["Authorization"] = f"Token {settings.courtlistener_api_token}"

    url = f"{settings.courtlistener_base_url}/search/"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error("CourtListener search failed: %s %s", exc.response.status_code, exc.response.text[:500])
        return {"error": str(exc), "results": []}
    except Exception as exc:
        logger.error("CourtListener search error: %s", exc)
        return {"error": str(exc), "results": []}


def get_opinion(opinion_id: int) -> dict:
    """Fetch a single opinion by ID."""
    headers: dict = {"Accept": "application/json"}
    if settings.courtlistener_api_token:
        headers["Authorization"] = f"Token {settings.courtlistener_api_token}"

    url = f"{settings.courtlistener_base_url}/opinions/{opinion_id}/"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.error("CourtListener get_opinion(%s) error: %s", opinion_id, exc)
        return {"error": str(exc)}


def get_cluster(cluster_id: int) -> dict:
    """Fetch an opinion cluster by ID."""
    headers: dict = {"Accept": "application/json"}
    if settings.courtlistener_api_token:
        headers["Authorization"] = f"Token {settings.courtlistener_api_token}"

    url = f"{settings.courtlistener_base_url}/clusters/{cluster_id}/"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.error("CourtListener get_cluster(%s) error: %s", cluster_id, exc)
        return {"error": str(exc)}


def search_with_cache(
    db_session,
    query: str,
    court: str | None = None,
    date_after: str | None = None,
    date_before: str | None = None,
    page: int = 1,
    cache_ttl_hours: int = 24,
) -> dict:
    """Search with Postgres cache layer."""
    from app.models.courtlistener_cache import CourtListenerCache

    qh = _query_hash(query, court, date_after, date_before, page)

    # Check cache
    cached = db_session.query(CourtListenerCache).filter_by(query_hash=qh).first()
    if cached:
        age = (datetime.now(timezone.utc) - cached.created_at).total_seconds() / 3600
        if age < cache_ttl_hours:
            logger.info("CourtListener cache HIT for query hash %s", qh[:12])
            return cached.result_json

    # Cache miss — fetch from API
    result = search_opinions(query, court, date_after, date_before, page)

    # Store in cache
    if "error" not in result:
        try:
            if cached:
                cached.result_json = result
                cached.result_count = len(result.get("results", []))
                cached.created_at = datetime.now(timezone.utc)
            else:
                entry = CourtListenerCache(
                    query_hash=qh,
                    query_text=query,
                    result_json=result,
                    result_count=len(result.get("results", [])),
                )
                db_session.add(entry)
            db_session.commit()
        except Exception as exc:
            logger.warning("Failed to cache CourtListener result: %s", exc)
            db_session.rollback()

    return result
