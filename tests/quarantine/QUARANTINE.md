# Quarantined Test Suites

These test files are **excluded from default pytest collection** because the
source modules they import no longer exist on the `main` branch.

This is a packaging/layout issue, not a test-logic issue.

## Quarantined Files

| File | Missing Module | Root Cause | Deadline |
|------|---------------|------------|----------|
| `test_cli_end_to_end.py` | `backend.tools.cli.cli` | `backend/` package deleted from `main` | Phase 11 or remove |
| `test_courtlistener_client.py` | `backend.src.verified_legal_sources` | `VerifiedLegalSources` class removed entirely | Phase 11 or remove |
| `test_manifest.py` | `backend.tools.cli.hashing`, `backend.tools.cli.manifest` | Functions partially in `scripts/generate-checksums.py` (different signatures) | Phase 11 or remove |

## Resolution Path

1. **Re-implement** the `backend.tools.cli` module with hash/manifest commands, or
2. **Port** the test expectations to the current `scripts/generate-checksums.py` signatures, or
3. **Remove** these files permanently if the functionality is no longer planned.

## How Quarantine Works

`pytest.ini` lists `quarantine` in `norecursedirs`, so `py -m pytest tests/`
will never attempt to collect these files. To run them deliberately:

```sh
py -m pytest tests/quarantine/ -v --no-header
```
