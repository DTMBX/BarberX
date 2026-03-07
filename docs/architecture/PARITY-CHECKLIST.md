# Parity Checklist

**Document:** Federation vs legacy build output comparison requirements  
**Date:** 2026-03-07  
**Status:** Active  
**Scope:** Evident monorepo — satellite app build output  
**Phase:** 3D

---

## Purpose

Before replacing `build:apps` with `build-federate.ps1`, the federation
pipeline must produce output-equivalent results. This document defines
what "equivalent" means and how to verify it.

---

## Must Match Exactly (Blocking)

| Check | Method | Status |
|-------|--------|--------|
| Output directory structure | `_site/apps/{slug}/` exists with same 4 slugs | PENDING |
| File count per app | File counts match within each slug directory | PENDING |
| `index.html` presence | Each `_site/apps/{slug}/index.html` exists | PENDING |
| Asset hash filenames | Vite-generated filenames match (same source = same hash) | PENDING |
| No extra files | Federation does not inject files legacy does not produce | PENDING |
| No missing files | Every legacy output file exists in federation output | PENDING |

## Acceptable Differences (Not Blocking)

| Difference | Reason |
|------------|--------|
| Build timestamps in HTML comments | Non-functional metadata |
| Source map paths containing `.federation-cache/` vs `apps/` | Dev-only, not deployed |
| `node_modules/` internal paths | Not in build output |
| Whitespace-only differences in minified files | Compression normalizes |

## Blocking Differences (Must Investigate)

| Difference | Reason |
|------------|--------|
| Missing routes or pages in SPA | Functional regression |
| Different JS bundle contents (beyond path strings) | Code divergence |
| Missing assets (images, fonts) | Visual regression |
| Different `package.json` version field | Repo divergence indicator |

---

## Expected Divergence

The canonical repos may have diverged from the workspace copies in `apps/`.
If the parity diff shows differences, the canonical repo version is
authoritative. Differences indicate the workspace copy is stale, not that
the federation pipeline is wrong.

---

## Verification Procedure

1. Run legacy build: `node scripts/build-apps.js`
2. Copy output: `_site/apps/` to `_site-legacy/apps/`
3. Run federation build: `pwsh scripts/build-federate.ps1`
4. Copy output: `_site/apps/` to `_site-federation/apps/`
5. Compare trees: file list, file sizes, binary comparison
6. Report: exact matches, size mismatches, missing, extra files
7. Mark blocking checks as PASS or FAIL

---

## Results

| Slug | Legacy Files | Federation Files | Match | Notes |
|------|-------------|-----------------|-------|-------|
| civics-hierarchy | — | — | PENDING | |
| epstein-library | — | — | PENDING | |
| essential-goods | — | — | PENDING | |
| geneva-bible-study | — | — | PENDING | |
