"""Tests for CourtListener client — mocked HTTP."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import httpx
import pytest


# ── search_opinions ──────────────────────────────────────────────

class TestSearchOpinions:
    """CourtListener search_opinions with mocked HTTP."""

    @patch("app.services.courtlistener.httpx.Client")
    def test_search_returns_results(self, mock_client_cls):
        from app.services.courtlistener import search_opinions

        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "count": 2,
            "results": [
                {
                    "id": 1,
                    "absolute_url": "/opinion/1/smith-v-jones/",
                    "caseName": "Smith v. Jones",
                    "court": "Supreme Court",
                    "dateFiled": "2024-01-15",
                    "snippet": "This case involved...",
                    "citation_count": 5,
                    "cluster_id": 100,
                },
                {
                    "id": 2,
                    "absolute_url": "/opinion/2/doe-v-state/",
                    "caseName": "Doe v. State",
                    "court": "District Court",
                    "dateFiled": "2023-06-01",
                    "snippet": "Regarding excessive force...",
                    "citation_count": 12,
                    "cluster_id": 200,
                },
            ],
        }
        fake_response.raise_for_status = MagicMock()

        mock_http = MagicMock()
        mock_http.get.return_value = fake_response
        mock_http.__enter__ = lambda s: mock_http
        mock_http.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_http

        result = search_opinions("excessive force body camera")
        assert result["count"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["caseName"] == "Smith v. Jones"

    @patch("app.services.courtlistener.httpx.Client")
    def test_search_http_error_returns_empty(self, mock_client_cls):
        from app.services.courtlistener import search_opinions

        mock_http = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_resp
        )
        mock_http.get.return_value = mock_resp
        mock_http.__enter__ = lambda s: mock_http
        mock_http.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_http

        result = search_opinions("test query")
        assert "error" in result
        assert result["results"] == []


# ── search_with_cache ────────────────────────────────────────────

class TestSearchWithCache:
    """Cache layer for CourtListener searches."""

    @patch("app.services.courtlistener.search_opinions")
    def test_cache_miss_calls_api(self, mock_search, db):
        from app.services.courtlistener import search_with_cache

        mock_search.return_value = {
            "count": 1,
            "results": [{"id": 1, "caseName": "Test v. Case"}],
        }

        result = search_with_cache(db, "test query")
        assert mock_search.called
        assert result["count"] == 1

    @patch("app.services.courtlistener.search_opinions")
    def test_cache_hit_skips_api(self, mock_search, db):
        from app.services.courtlistener import search_with_cache

        # First call = cache miss
        mock_search.return_value = {
            "count": 1,
            "results": [{"id": 1, "caseName": "Test"}],
        }
        search_with_cache(db, "cached query")

        # Second call = cache hit
        mock_search.reset_mock()
        result = search_with_cache(db, "cached query")
        mock_search.assert_not_called()
        assert result["count"] == 1


# ── _query_hash ──────────────────────────────────────────────────

class TestQueryHash:
    """Deterministic hashing of search parameters."""

    def test_same_params_same_hash(self):
        from app.services.courtlistener import _query_hash

        h1 = _query_hash("test", None, None, None, 1)
        h2 = _query_hash("test", None, None, None, 1)
        assert h1 == h2

    def test_different_params_different_hash(self):
        from app.services.courtlistener import _query_hash

        h1 = _query_hash("test", None, None, None, 1)
        h2 = _query_hash("test", "nj", None, None, 1)
        assert h1 != h2
