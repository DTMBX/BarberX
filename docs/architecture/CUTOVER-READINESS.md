# Cutover Readiness — Migration Gate Checklist

**Document:** Federation cutover gate tracking  
**Date:** 2026-03-07  
**Status:** In Progress  
**Scope:** Evident monorepo — legacy `apps/` removal readiness  
**Phase:** 3D — Cutover Planning and Validation

---

## Gate Status

| Gate | Requirement | Status | Last Verified | Notes |
|------|------------|--------|---------------|-------|
| G1 | Tagged release with `releaseChannel: "release"` for ≥1 target | **FAIL** | 2026-03-07 | All 4 targets: `tag: null`, `releaseChannel: "dev"` |
| G2 | `test-federation-reproducibility.ps1` passes on a real build | **FAIL** | 2026-03-07 | Never executed against real build output |
| G3 | `federation-manifest.json` committed and reviewed | **FAIL** | 2026-03-07 | File does not exist — no live build has run |
| G4 | Federation output diffed against legacy `build:apps` with no functional divergence | **FAIL** | 2026-03-07 | No parity comparison performed |
| G5 | No `pin: "HEAD"` entries in the release manifest | **FAIL** | 2026-03-07 | All targets: `pin: "HEAD"` |

---

## Prerequisites for Phase D3 (Staged Cutover)

All of the following must be true before replacing `build:apps`:

- [ ] G2 passes (reproducibility test)
- [ ] G3 satisfied (manifest committed)
- [ ] G4 satisfied (parity diff clean)
- [ ] `build-federate.ps1` has been executed successfully at least once

## Prerequisites for Phase D4 (Removal)

All of the following must be true before deleting `apps/`:

- [ ] G1 satisfied (tagged release)
- [ ] G2 satisfied (reproducibility test)
- [ ] G3 satisfied (manifest committed)
- [ ] G4 satisfied (parity diff clean)
- [ ] G5 satisfied (no HEAD in release)
- [ ] D3 cutover has been live for ≥1 successful deployment cycle

---

## Verdicts

| Phase | Verdict | Date |
|-------|---------|------|
| D3 — Staged Cutover | NOT READY | 2026-03-07 |
| D4 — Removal | NOT READY | 2026-03-07 |

---

## Signoff

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Repo Owner | | | |
| Reviewer | | | |
