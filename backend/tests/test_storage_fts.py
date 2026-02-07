from backend.tools.law.storage import init_db


def test_storage_fts(tmp_path):
    db = tmp_path / "law.db"
    conn = init_db(db)
    cur = conn.cursor()
    # insert a document and FTS entry
    cur.execute(
        "INSERT INTO law_documents(source, source_key, title, court) VALUES (?, ?, ?, ?)",
        ("test", "k1", "Alpha Case", "SupremeCourt"),
    )
    doc_id = cur.lastrowid
    cur.execute(
        "INSERT INTO law_fts(doc_id, title, court, canonical_text) VALUES (?, ?, ?, ?)",
        (doc_id, "Alpha Case", "SupremeCourt", "This is the text of Alpha Case."),
    )
    conn.commit()
    # search via FTS5
    q = conn.execute("SELECT doc_id FROM law_fts WHERE law_fts MATCH ?", ("Alpha",)).fetchall()
    assert q and q[0][0] == doc_id
