from unittest.mock import patch

from backend.tools.law.jobs.ingest import Ingestor
from backend.tools.law.sources.courtlistener.client import CourtListenerClient
from backend.tools.law.storage import init_db


def _mock_opinion():
    return {
        "id": "op-2",
        "title": "Idempotent Case",
        "court": "MockCourt",
        "plain_text": "Idempotent opinion text.",
    }


def test_webhook_idempotency(tmp_path):
    db = tmp_path / "law.db"
    ing = Ingestor(db_path=db)

    opinion = _mock_opinion()

    class MockClient(CourtListenerClient):
        def fetch_opinion_content(self, opinion_json):
            return opinion_json["plain_text"].encode("utf-8"), "text/plain"

    with patch("backend.tools.law.jobs.ingest.CourtListenerClient", MockClient):
        id1 = ing.ingest_opinion(
            "courtlistener",
            opinion["id"],
            opinion,
            tool_versions_json='{"tool":"test"}',
            idempotency_key="k1",
        )
        id2 = ing.ingest_opinion(
            "courtlistener",
            opinion["id"],
            opinion,
            tool_versions_json='{"tool":"test"}',
            idempotency_key="k1",
        )

    assert id1 == id2
    conn = init_db(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM provenance_events WHERE doc_id = ?", (id1,))
    cnt = cur.fetchone()[0]
    # Expect at least one provenance event; idempotency should avoid duplicate ingest events
    assert cnt == 1
