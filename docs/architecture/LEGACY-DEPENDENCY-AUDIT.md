# Legacy Dependency Audit

**Document:** Complete audit of all files depending on `apps/` workspace copies  
**Date:** 2026-03-07  
**Status:** Active  
**Scope:** Evident monorepo — federation cutover prerequisites  
**Phase:** 3D

---

## Summary

The `apps/` directory contains 4 workspace copies of canonical standalone repos.
Removing `apps/` requires updating or replacing every file that reads from,
builds from, or references these directories.

Root cause: `package.json` line 6 declares `"apps/*"` in the `workspaces` array.

---

## BUILD — Critical (blocks removal)

| # | File | Reference | Severity |
|---|------|-----------|----------|
| 1 | `package.json` L6 | `"apps/*"` in workspaces | ROOT CAUSE |
| 2 | `scripts/build-apps.js` | `APPS_DIR = path.resolve('..', 'apps')` | Critical |
| 3 | `package.json` L28 | `"build:apps"` calls build-apps.js | Critical |
| 4 | `package.json` L10 | `"build:all"` uses `npm -ws` | High |
| 5 | `package.json` L11 | `"test:all"` uses `npm -ws` | High |
| 6 | `.github/workflows/deploy-eleventy-pages.yml` | `npm run build` step | High |

## BUILD-AWARE — Needs update at cutover

| # | File | Reference | Severity |
|---|------|-----------|----------|
| 7 | `scripts/build-federate.ps1` | Parses `hasWorkspaceCopy` strings | Low |
| 8 | `tools/web-builder/workspace-registry.json` | 4 entries with `hasWorkspaceCopy` | Low |
| 9 | `tools/web-builder/app-catalog.json` | 4 entries with `hasWorkspaceCopy` | Low |
| 10 | `package-lock.json` | Auto-generated from workspaces | Low |

## WORKFLOW — Non-blocking

| # | File | Notes |
|---|------|-------|
| 11 | `scripts/compare-satellites.ps1` | Hardcoded stale `c:\web-dev\` paths — archived |
| 12 | `.github/workflows/github-pages.yml.disabled` | Disabled — cannot run |

## DOC — Informational only

| # | File |
|---|------|
| 13 | `docs/architecture/ECOSYSTEM-ARCHITECTURE-MAP.md` |
| 14 | `docs/architecture/DUAL-BUSINESS-DEPLOYMENT-PLAN.md` |
| 15 | `docs/architecture/WORKSPACE-AUDIT-2026-03.md` |
| 16 | `docs/architecture/SAFE-CONSOLIDATION.md` |
| 17 | `docs/architecture/MAIN-SUITE-PACKAGING-PLAN.md` |

## Confirmed Clean (zero hits)

`.eleventy.js`, `_config.yml`, `_redirects`, `_headers`,
`federation-verify.ps1`, `pages-verify.js`, all `.html` page files,
all CSS/Tailwind configs.

---

## Dependency Graph

```text
package.json L6: "apps/*"  <-- ROOT CAUSE
  |-- package-lock.json (auto-regenerates)
  |-- npm -ws commands: build:all, test:all
  |-- npm install (workspace resolution + hoisting)
  +-- build:apps -> scripts/build-apps.js
        +-- _site/apps/{slug}/ (build output)
              +-- deploy-eleventy-pages.yml (uploads _site/)
```

---

## Founder-Hub Cross-References (separate repo)

Static data files reference deployed output paths (e.g.,
`apps/civics-hierarchy` in `sites.json`, `projects.json`).
These are URL path references to `_site/apps/{slug}/` output.
The federation pipeline preserves the same output paths,
so these require no changes at cutover.
