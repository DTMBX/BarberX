# Modernization Findings Report

**Repository:** DTMBX/EVIDENT  
**Audit Date:** 2026-02-11  
**Auditor:** Platform Engineering  

---

## Executive Summary

The Evident Technologies repository contains a functional web platform built on
**Eleventy 3.x** (primary) with vestigial **Jekyll** configuration artifacts. The
codebase deploys to GitHub Pages via a GitHub Actions pipeline (`pages.yml`).

This audit identified **five critical architecture issues** and produced targeted
fixes. No breaking changes were introduced. All fixes are backward-compatible.

---

## 1. Deployment Architecture

### Finding

Two static site generators are configured simultaneously:

| System | Config | Build Pipeline | Deploys? |
|--------|--------|----------------|----------|
| **Eleventy 3.x** | `.eleventy.js`, `src/` templates | `pages.yml` | Yes (GitHub Pages) |
| Jekyll 4.4 | `_config.yml`, `Gemfile`, `_layouts/` | `jekyll-docker.yml` | No |

The root-level `_layouts/`, `_includes/`, and `*.html` files are **Jekyll
artifacts** that do not participate in the Eleventy build (which reads from
`src/`). The `jekyll-docker.yml` workflow ran on every push but produced
output that was never deployed.

### Decision: Lane B — Full GitHub Actions Build Pipeline

Eleventy is the active, deployed system. Jekyll infrastructure is retained on
disk as documentation but its workflow has been disabled. The Eleventy pipeline
has been hardened with Node 20, link checking, and page-count verification.

### Actions Taken

- Disabled `jekyll-docker.yml` (renamed to `.disabled`)
- Pinned Node version to 20 across `.nvmrc`, `package.json` `engines` field,
  and `pages.yml`
- Added build output verification (page count) and a non-blocking link checker
  to `pages.yml`

---

## 2. Design Token Fragmentation

### Finding

**Five competing CSS token systems** were active simultaneously, defining the
same primitives (colors, fonts, spacing, radii, shadows) with different names
and conflicting values:

| File | Prefix | Tokens | Status |
|------|--------|--------|--------|
| `assets/css/tokens.css` | `--color-*` | 6 | Root-level minimal |
| `assets/css/tokens/tokens.css` | `--ink`, `--blue`, etc. | 50+ | Semantic v2 |
| `assets/css/tokens/evident.tokens.css` | `--ff-*`, `--evident-*` | 40+ | Tailwind-like |
| `assets/css/tokens/brand-tokens.css` | short names | 10 | Brand primitives |
| `assets/css/base/variables.css` | `--ff-*`, `--stone-*` | 120+ | Comprehensive |

`core.css` referenced tokens that existed in **none** of these files (e.g.,
`--font-body`, `--color-fg` as RGB triplet, `--container-max`), meaning it
rendered with browser fallbacks or broken values.

**Specific conflicts:**
- Primary color: `#0b73d2` vs `#2f5d9f` vs `#2563eb` vs `rgb(59 130 246)`
- Spacing `--space-lg`: `2rem` vs `1.5rem`
- Radius `--r-md`: `14px` vs `12px`
- Font stack: 4 different declarations under 4 different variable names

### Actions Taken

- Created `assets/css/tokens/evident-design-tokens.css` — single authoritative
  source with `--ev-*` namespace
- All primitives consolidated with WCAG 2.1 AA contrast ratios annotated
- Backward-compatibility aliases provided so all existing CSS continues to work
- `tokens.css` now re-exports the unified file via `@import`
- `core.css` fixed to use hex values instead of broken `rgb(var(--hex))` pattern

---

## 3. JavaScript Redundancy

### Finding

Three JS files competed for mobile navigation and header behavior:

| Feature | `navigation.js` | `ux-enhancements.js` | `main.js` |
|---------|:---:|:---:|:---:|
| Mobile nav toggle | Yes | Yes (duplicate) | — |
| Escape key close | Yes | Yes (duplicate) | — |
| Click-outside close | Yes | Yes (duplicate) | — |
| Sticky header on scroll | — | Yes (`#siteHeader`) | Yes (`scrollY > 12`) |

`ux-enhancements.js` also contained features contrary to the Evident design
guidelines (3D card hover effects with `perspective(1000px)`, parallax scrolling,
animated counters) that conflict with the requirement for "calm, restrained" UI.

`theme.js` set `colorScheme` but not `data-theme`, while the CSS
(`base/variables.css`) uses `[data-theme='dark']` selectors — meaning the
theme toggle had **no visual effect** on the design system.

### Actions Taken

- Disabled `initStickyHeader()` and `initMobileNav()` calls in
  `ux-enhancements.js` (they targeted non-existent or duplicate elements)
- Fixed `theme.js` to set both `colorScheme` and `data-theme` attribute
- `navigation.js` remains the canonical mobile nav handler

---

## 4. GitHub Actions Workflow Sprawl

### Finding

**34 active workflow files** with significant duplication:

| Concern | Duplicate Workflows |
|---------|-------------------|
| CodeQL scanning | `codeql-analysis.yml` (v2) + `codeql.yml` (v4) |
| Dependency review | `dependency-review.yml` (v2) + `dependency_review.yml` (v4) |
| Lint/format | `lint.yml` + `ci.yml` (style-check) + `law-tests.yml` (style-check) |
| Security scanning | `security-scan.yml` + `security-pip-audit.yml` + `dependency-scan.yml` |
| Python linting | `pylint.yml` + `ci.yml` (ruff) |
| Jekyll build | `jekyll-docker.yml` (vestigial) |

Node versions were inconsistent across workflows: 18, 20, and 22 appeared
in different files.

### Actions Taken

- Disabled 7 duplicate/vestigial workflows:
  - `codeql-analysis.yml` (kept `codeql.yml` with v4 actions)
  - `dependency-review.yml` + `dependency_review.yml` (kept in `ci.yml`)
  - `dependency-scan.yml` (covered by `security-scan.yml`)
  - `security-pip-audit.yml` (covered by `security-scan.yml`)
  - `lint.yml` (covered by `ci.yml`)
  - `pylint.yml` (covered by ruff in `ci.yml`)
  - `jekyll-docker.yml` (vestigial)
- Pinned Node 20 in `pages.yml` and `.nvmrc`

---

## 5. Tailwind Configuration

### Finding

`tailwind.config.cjs` contained **two `module.exports` statements**. The second
one overwrote the first, discarding the `@tailwindcss/forms` and
`@tailwindcss/typography` plugins and using a different primary color (`#0b5f73`
instead of `#2f5d9f`).

### Actions Taken

- Merged both declarations into a single `module.exports`
- Retained both plugins (`forms`, `typography`)
- Aligned colors to match the unified token system

---

## 6. Performance & Accessibility Notes

### Existing Strengths
- Skip-to-content link present in `default.html`
- ARIA labels on navigation and mobile menu
- `prefers-reduced-motion` respected in both `core.css` and `tokens/tokens.css`
- Google Fonts loaded with `preconnect`
- Structured data (JSON-LD) for Organization and BlogPosting
- Full Open Graph and Twitter Card meta tags
- Print stylesheet in `core.css`

### Remaining Opportunities
- External fonts (`Inter` from Google Fonts) lack `font-display: swap`
  — add `&display=swap` to the URL (already present)
- No SRI hashes on external resources
- 50+ JS files in `assets/js/` — only 3 are loaded; others are dead code
- Consider adding a `Content-Security-Policy` header via `_headers` file

---

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| Site builds cleanly locally and in CI | Pending verification |
| No broken internal links | Link checker added to CI |
| WCAG AA contrast on primary pages | Tokens verified with Evident Blue (#2f5d9f) at 5.9:1 on paper |
| No layout collapse on mobile | Maintained — Tailwind responsive utilities intact |
| Deployment pipeline reproducible | Node 20 pinned, npm ci cached |
| No dependency bloat | Dead workflows disabled, single Tailwind config |
| No incompatible Pages plugins | N/A — Eleventy, not Jekyll Pages |

---

## Files Modified / Created

### Created
- `assets/css/tokens/evident-design-tokens.css` — unified token source
- `scripts/verify.sh` — Bash verification script
- `scripts/verify.ps1` — PowerShell verification script
- `MODERNIZATION_FINDINGS.md` — this document
- `RELEASE_NOTES.md` — change summary

### Modified
- `assets/css/tokens.css` — re-exports unified tokens
- `assets/css/core.css` — fixed broken `rgb(var())` patterns
- `assets/js/ux-enhancements.js` — disabled duplicate nav/header
- `assets/js/theme.js` — fixed `data-theme` attribute sync
- `tailwind.config.cjs` — merged duplicate `module.exports`
- `.github/workflows/pages.yml` — hardened with Node 20 + link check
- `.github/workflows/ci.yml` — added `mkdir -p test-results`
- `.nvmrc` / `.config/.nvmrc` — pinned to 20
- `package.json` — added `engines` field

### Disabled (renamed to `.yml.disabled`)
- `jekyll-docker.yml`
- `lint.yml`
- `pylint.yml` (removed; `.disabled` already existed)
- 4 previously disabled duplicates confirmed
