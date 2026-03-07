# Packaging Relationships

**Document:** How each surface should be packaged, built, and consumed  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident monorepo and all satellite repos

---

## Purpose

This document defines how each codebase surface is **packaged** (built,
bundled, or consumed) and the relationships between packages. It prevents
confusion about which build system owns which output and how dependencies
flow between surfaces.

---

## Packaging Model Overview

```
┌──────────────────────────────────────────────────────────┐
│  Evident Monorepo (evident-monorepo v0.8.0)              │
│                                                          │
│  ┌─────────────────────────────┐                         │
│  │  Root build (11ty + CSS)    │──→ _site/ (marketing)   │
│  └─────────────────────────────┘                         │
│                                                          │
│  ┌─────────────────────────────┐                         │
│  │  bwc/backend/ (FastAPI)     │──→ Render deploy        │
│  └─────────────────────────────┘                         │
│                                                          │
│  ┌─────────────────────────────┐                         │
│  │  bwc/frontend/ (Next.js)    │──→ Vercel / Render      │
│  └─────────────────────────────┘                         │
│                                                          │
│  ┌─────────────────────────────┐                         │
│  │  packages/design-tokens/    │──→ CSS import (local)   │
│  └─────────────────────────────┘                         │
│                                                          │
│  ┌─────────────────────────────┐                         │
│  │  apps/* (workspace copies)  │──→ Federation builds    │
│  │  [Non-canonical — see note] │    (monorepo convenience│
│  └─────────────────────────────┘    only)                │
└──────────────────────────────────────────────────────────┘

┌────────────────────────────────────┐
│  Satellite Repos (canonical)       │
│                                    │
│  ventures/Civics Hierarchy/        │──→ GitHub Pages
│  ventures/DOJ Document Library/    │──→ GitHub Pages
│  ventures/Essential Goods Ledger/  │──→ GitHub Pages
│  ventures/Informed Consent/        │──→ GitHub Pages
│  ventures/Geneve Bible Study/      │──→ GitHub Pages
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Founder-Hub (ops-hub)             │──→ GitHub Pages
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Tillerstead LLC (separate)        │
│                                    │
│  ventures/Tillerstead/             │──→ Netlify
│  ventures/tillerstead-toolkit/     │──→ Railway
│  ventures/Contractor Command/      │──→ GitHub Pages
│  ventures/Sweat Equity Insurance/  │──→ Not deployed
└────────────────────────────────────┘
```

---

## Per-Surface Packaging Details

### Evident Monorepo — Native Surfaces

| Surface | Build system | Output | Deploy target | Consumed by |
| ------- | ----------- | ------ | ------------- | ----------- |
| Marketing site | 11ty + PostCSS + Tailwind | `_site/` | GitHub Pages | Public visitors |
| BWC Backend | FastAPI (uvicorn) | Python runtime | Render | BWC Frontend, CLI |
| BWC Frontend | Next.js 14 | `.next/` static export | Render / Vercel | Browser clients |
| BWC Frontend New | Next.js (migration) | Not built | Not deployed | — |
| Design Tokens | CSS files | `tokens.css` | npm workspace import | Any monorepo surface |
| Web Builder | Static HTML/JS | Served as-is | Internal only | Developers |

### Evident Monorepo — apps/ Federation

| Workspace member | Package name | Builds via | Built output |
| ---------------- | ------------ | ---------- | ------------ |
| `apps/civics-hierarchy/` | `civics-stack` | Vite | `dist/` |
| `apps/epstein-library-evid/` | `@evident/epstein-library` | Vite | `dist/` |
| `apps/essential-goods-ledg/` | `@evident/essential-goods` | Vite | `dist/` |
| `apps/geneva-bible-study-t/` | `geneva-bible-study` | Vite | `dist/` |

**Note:** These workspace members exist for monorepo build
convenience (`npm run build:apps`). Their canonical source is the
corresponding standalone repo. See SOURCE-OF-TRUTH-MAP.md.

The `build:apps` script (`scripts/build-apps.js`) iterates through
`apps/*` and runs each app's build. This output may be used for
federation into the main `_site/` or for verification purposes.

### Satellite Repos — Independent Builds

| Repo | Build system | Output | Deploy target |
| ---- | ----------- | ------ | ------------- |
| Civics Hierarchy | Vite | `dist/` | GitHub Pages |
| DOJ Document Library | Vite + Docker | `dist/` or container | GitHub Pages / Docker |
| Essential Goods Ledger | Vite | `dist/` | GitHub Pages |
| Informed Consent | Vite | `dist/` | GitHub Pages |
| Geneva Bible Study | Vite | `dist/` | GitHub Pages + App Stores |

### Founder-Hub

| Surface | Build system | Output | Deploy target |
| ------- | ----------- | ------ | ------------- |
| Ops portal | Vite (React 19) | `dist/` | GitHub Pages → devon-tyler.com |

### Tillerstead LLC

| Surface | Build system | Output | Deploy target |
| ------- | ----------- | ------ | ------------- |
| Marketing site | Jekyll | `_site/` | Netlify → tillerstead.com |
| Toolkit API | FastAPI (uvicorn) | Python runtime | Railway |
| Contractor Command | Vite | `dist/` | GitHub Pages |
| Sweat Equity Insurance | Static HTML | Served as-is | Not deployed |

---

## Dependency Flow

### Runtime dependencies

```
BWC Frontend ──→ BWC Backend API (REST/WebSocket)
Tillerstead Site ──→ Tillerstead Toolkit API (iframe + postMessage)
Founder-Hub ──→ No runtime API dependency (reads static catalog)
Satellite apps ──→ No shared runtime dependency
```

### Build-time dependencies

```
Evident root build
  ├── PostCSS / Tailwind → _site/assets/css/
  ├── 11ty templates → _site/*.html
  ├── scripts/build-apps.js → apps/*/dist/
  └── packages/design-tokens/ → CSS import
       (consumed by any surface that imports tokens.css)
```

### Package registry

No packages are published to npm. All dependencies are:

- Workspace-local (`"workspaces": ["apps/*", "packages/*"]`)
- Installed from npm public registry (third-party libs)

---

## What Is NOT a Package

| Item | Why it is not a package |
| ---- | ---------------------- |
| `bwc/` | Subsystem within monorepo — not independently versioned |
| `tools/web-builder/` | Internal HTML tool — no package.json build |
| `cli/evident.py` | Python CLI — not distributed as package |
| `.github/workflows/` | CI config — not a consumable surface |
| `docs/` | Documentation — not a build output |

---

## Future Packaging Recommendations

These are documented for Phase B consideration:

1. **Remove `apps/` workspace copies** — Federation can be
   achieved without duplicating source code. Use a build script
   that clones or links canonical repos at build time.
2. **Formalize design-tokens** — If design tokens are shared
   across businesses, publish to a private registry or use
   git-based installation.
3. **Version satellite apps independently** — Each satellite
   should maintain its own semver in its own repo.
4. **Fix `spark-template` placeholder names** — Two standalone
   repos (`epstein-library-evid`, `essential-goods-ledg`) still
   have `spark-template` as their package name.
