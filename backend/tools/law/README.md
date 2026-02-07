Law ingestion utilities for Evident

Layout
- `storage.py` — initializes SQLite schema and returns connections.
- `blobs.py` — immutable blob store under `backend/tools/law/blobs/{raw,canonical,json}` storing files by SHA-256.
- `normalize.py` — deterministic canonicalizer for HTML/text producing canonical bytes and canonical text.
- `citations.py` — extracts citations; prefers `eyecite` if installed, otherwise uses a conservative regex fallback.
- `sources/courtlistener/client.py` — minimal client intended for test mocking; stores raw JSON responses immutably.
- `jobs/ingest.py` — orchestrates ingest: fetch -> blob raw -> canonicalize -> blob canonical -> upsert documents -> update FTS -> extract citations -> append provenance.

Dependency note
--------------
- We recommend pinning `eyecite` for robust citation parsing. This repo does not add it to global requirements automatically; to enable eyecite install a pinned version, e.g. in a virtualenv:

```bash
pip install eyecite==0.17.0
```

Tests
-----
All network calls are mocked in tests under `backend/tests/`. To run the law tests:

```bash
python -m pytest backend/tests/test_courtlistener_ingest_mocked.py -q
```
