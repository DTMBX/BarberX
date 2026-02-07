from unittest.mock import patch

from backend.tools.law.jobs.ingest import Ingestor
from backend.tools.law.sources.courtlistener.client import CourtListenerClient
from backend.tools.law.storage import init_db


def _mock_opinion():
    return {
        "id": "op-1",
        "title": "Mock Case",
        "court": "MockCourt",
        "plain_text": "This opinion cites 123 F.3d 456 and 234 U.S. 789.",
    }


def test_courtlistener_ingest_mocked(tmp_path):
    db = tmp_path / "law.db"
    ing = Ingestor(db_path=db)

    opinion = _mock_opinion()

    # Mock client's fetch_opinion_content to return bytes
    class MockClient(CourtListenerClient):
        def fetch_opinion_content(self, opinion_json):
            return opinion_json["plain_text"].encode("utf-8"), "text/plain"

    with patch("backend.tools.law.jobs.ingest.CourtListenerClient", MockClient):
        doc_id = ing.ingest_opinion(
            "courtlistener", opinion["id"], opinion, tool_versions_json='{"tool":"test"}'
        )

    # open DB and assert entries
    conn = init_db(db)
    cur = conn.cursor()
    cur.execute("SELECT title, court FROM law_documents WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    assert row[0] == "Mock Case"
    assert row[1] == "MockCourt"

    # citations should be present
    cur.execute(
        "SELECT cite_text FROM citations WHERE from_doc_id = ? ORDER BY start_offset", (doc_id,)
    )
    cites = [r[0] for r in cur.fetchall()]
    assert "123 F.3d 456" in cites
    assert "234 U.S. 789" in cites

    # FTS search
    cur.execute("SELECT doc_id FROM law_fts WHERE law_fts MATCH ?", ("Mock",))
    fts = cur.fetchone()
    assert fts and fts[0] == doc_id
