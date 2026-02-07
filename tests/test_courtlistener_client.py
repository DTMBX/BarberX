import os
from unittest.mock import MagicMock

import pytest
import requests

from backend.src import verified_legal_sources as vls_mod


class DummyDoc:
    def __init__(self, citation="CIT-1"):
        self.citation = citation
        self.id = 123
        self.verified = False
        self.source = None


def test_import_from_courtlistener_sets_verified_and_source(monkeypatch):
    svc = vls_mod.VerifiedLegalSources()

    # mock library.ingest_from_courtlistener
    dummy = DummyDoc(citation="SAMPLE")
    svc.library.ingest_from_courtlistener = MagicMock(return_value=dummy)

    # patch db.session.commit to avoid DB side effects
    monkeypatch.setattr(vls_mod, "db", MagicMock(session=MagicMock(commit=MagicMock())))

    doc = svc.import_from_courtlistener("SAMPLE")
    assert doc is not None
    assert doc.verified is True
    assert doc.source == "courtlistener"


def test_verify_citation_authenticity_uses_api_key(monkeypatch):
    svc = vls_mod.VerifiedLegalSources()

    called = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        called["headers"] = headers

        class R:
            status_code = 200

            def json(self):
                return {"count": 1}

        return R()

    monkeypatch.setenv("COURTLISTENER_API_KEY", "TOK-XYZ")
    # Patch the requests.get used by the module
    monkeypatch.setattr(requests, "get", fake_get)

    res = svc.verify_citation_authenticity("SAMPLE", "courtlistener")
    assert res["authentic"] is True
    # ensure we passed Authorization header when API key is set
    assert called.get("headers") and "Authorization" in called["headers"]
