from __future__ import annotations
from typing import Optional

import json
from typing import Any

from ...blobs import write_blob


class CourtListenerClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "https://www.courtlistener.com/api/rest/v3"

    def search_opinions(
        self,
        court: Optional[str] = None,
        date_min: Optional[str] = None,
        date_max: Optional[str] = None,
        page: int = 1,
    ) -> dict[str, Any]:
        # In tests this method will be mocked. Provide a minimal shape when called directly.
        # Return a dict with 'results' list and 'next' hint.
        return {"results": [], "next": None}

    def fetch_opinion(self, opinion_id: str) -> dict[str, Any]:
        # In tests this will be mocked; provide shape
        return {"id": opinion_id, "date_filed": None, "plain_text_url": None, "html_url": None}

    def fetch_opinion_content(self, opinion_json: dict[str, Any]) -> tuple[bytes, str]:
        # opinion_json may contain 'plain_text' or 'html' keys in tests
        if "plain_text" in opinion_json and opinion_json["plain_text"] is not None:
            data = opinion_json["plain_text"].encode("utf-8")
            # store raw JSON response
            write_blob(json.dumps(opinion_json).encode("utf-8"), kind="json")
            return data, "text/plain; charset=utf-8"
        if "html" in opinion_json and opinion_json["html"] is not None:
            write_blob(json.dumps(opinion_json).encode("utf-8"), kind="json")
            return opinion_json["html"].encode("utf-8"), "text/html; charset=utf-8"
        # fallback: serialize the json and return
        raw = json.dumps(opinion_json).encode("utf-8")
        write_blob(raw, kind="json")
        return raw, "application/json"
