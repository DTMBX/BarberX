import sys
import types
from unittest.mock import MagicMock

# Provide test-time mocks for optional production modules
legal_lib_mod = types.ModuleType("legal_library")
legal_lib_mod.LegalDocument = type("LegalDocument", (), {})


class _DummyLibrary:
    def __init__(self):
        pass

    def ingest_from_courtlistener(self, citation: str):
        # return a simple object with fields used by tests
        o = types.SimpleNamespace(citation=citation, id=1, verified=False, source=None)
        return o

    def search_library(self, query: str, limit: int = 1):
        return []


legal_lib_mod.LegalLibraryService = _DummyLibrary

models_auth_mod = types.ModuleType("models_auth")
models_auth_mod.db = MagicMock()

sys.modules["legal_library"] = legal_lib_mod
sys.modules["models_auth"] = models_auth_mod

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
