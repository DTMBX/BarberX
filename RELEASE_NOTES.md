# Release Notes — Platform Modernization

**Version:** 0.9.0  
**Date:** 2026-02-11  
**Branch:** `modernize/platform-stabilization`

---

## Summary

Consolidation and hardening of the Evident Technologies web platform. This
release resolves design token fragmentation, eliminates duplicate CI workflows,
fixes JavaScript conflicts, and establishes a reproducible build pipeline.

No breaking changes. All existing pages render identically.

---

## Changes

### Design System

- **Unified design tokens** — Created `assets/css/tokens/evident-design-tokens.css`
  as the single source of truth for all visual primitives. Uses `--ev-*` namespace
  with backward-compatible aliases for all legacy variable names.
- **Fixed broken CSS** — `core.css` used `rgb(var(--hex))` patterns that produced
  invalid color values. Replaced with direct variable references.
- **Fixed Tailwind config** — Merged duplicate `module.exports` in
  `tailwind.config.cjs`. Restored `@tailwindcss/forms` and `@tailwindcss/typography`
  plugins that were silently dropped by the second declaration.
- **WCAG AA compliance** — All token color pairs verified for minimum 4.5:1
  contrast ratio. Annotated inline.

### JavaScript

- **Eliminated duplicate mobile navigation** — `ux-enhancements.js` duplicated
  the same toggle/escape/outside-click logic already in `navigation.js`. Disabled
  the duplicate. `navigation.js` is now the canonical handler.
- **Fixed theme toggle** — `theme.js` now sets `data-theme` attribute in addition
  to `colorScheme`, enabling CSS `[data-theme='dark']` selectors in the design
  system to function correctly.
- **Disabled conflicting sticky header** — `ux-enhancements.js` targeted a
  `#siteHeader` element that does not exist. Disabled to prevent wasted scroll
  event processing.

### CI/CD

- **Disabled 7 duplicate/vestigial workflows:**
  - `jekyll-docker.yml` — built with Jekyll but never deployed; Eleventy is the
    active system
  - `lint.yml` — duplicated `ci.yml` style-check job
  - `pylint.yml` — duplicated ruff checks in `ci.yml`
  - Previously disabled: `codeql-analysis.yml`, `dependency-review.yml`,
    `dependency_review.yml`, `dependency-scan.yml`, `security-pip-audit.yml`
- **Hardened `pages.yml`:**
  - Pinned Node.js to version 20
  - Added HTML page count verification
  - Added non-blocking broken link checker
- **Hardened `ci.yml`:**
  - Added `mkdir -p test-results` before pytest to prevent failure on first run
- **Pinned Node 20** across `.nvmrc`, `.config/.nvmrc`, and `package.json`
  `engines` field

### Verification

- **Created `scripts/verify.sh`** (Bash) and **`scripts/verify.ps1`** (PowerShell)
  — cross-platform scripts that install dependencies, lint, build, verify output,
  and optionally run Python tests. Exit non-zero on any failure.

### Documentation

- **`MODERNIZATION_FINDINGS.md`** — full audit report with findings, decisions,
  and actions taken
- **`RELEASE_NOTES.md`** — this document

---

## Incremental Commit Plan

```
Commit 1: Tooling baseline
  - assets/css/tokens/evident-design-tokens.css (new)
  - assets/css/tokens.css (modified)
  - tailwind.config.cjs (modified)
  - package.json (engines field)
  - .nvmrc, .config/.nvmrc

Commit 2: CSS + accessibility fixes
  - assets/css/core.css (fixed rgb(var()) patterns)

Commit 3: JavaScript consolidation
  - assets/js/ux-enhancements.js (disabled duplicates)
  - assets/js/theme.js (fixed data-theme)

Commit 4: CI/CD hardening
  - .github/workflows/pages.yml (hardened)
  - .github/workflows/ci.yml (mkdir fix)
  - Disabled: lint.yml, pylint.yml, jekyll-docker.yml

Commit 5: Verification + documentation
  - scripts/verify.sh, scripts/verify.ps1
  - MODERNIZATION_FINDINGS.md
  - RELEASE_NOTES.md
```

---

## Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Keep Eleventy, not Jekyll | Already deployed; `pages.yml` is the active pipeline |
| Disable rather than delete workflows | Preserves git history; easy rollback |
| Use `--ev-*` namespace with aliases | Zero-disruption migration path |
| Pin Node 20 (not 22) | LTS through April 2026; 22 not yet LTS |
| Do not remove dead JS files | Separate cleanup PR to avoid scope creep |
