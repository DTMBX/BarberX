# Main Suite Packaging Plan

> Step 5 of the Evident Ecosystem Architecture Series
>
> Principle: **Ship the product, not the repository.**

---

## 1. Current State

The Evident repository contains **seven distinct functional zones** inside a
single monorepo. Not all of them belong in the same shipping unit.

| Zone | Tech | Coupling | Deploy Target |
| --- | --- | --- | --- |
| **Root Backend** (`backend/`, `services/`, `models/`, `routes/`, `auth/`) | Python 3.12, Flask → FastAPI migration | Tight (shared ORM, shared auth DB) | Render (Gunicorn) |
| **BWC Subsystem** (`bwc/backend/`, `bwc/frontend/`) | FastAPI + Next.js 14 | Self-contained (own DB, own auth, own S3) | Not yet deployed |
| **AI Pipeline** (`src/ai/`) | Pure Python, stdlib only | Zero backend coupling | Not yet deployed |
| **Marketing Site** (`src/` 11ty templates, `www/`) | 11ty 3.1, Tailwind 4, Alpine.js | No backend coupling | GitHub Pages |
| **.NET Gateway + Mobile** (`src/Evident.Web/`, `src/Evident.Mobile/`, `maui/`) | ASP.NET Core, .NET MAUI | HTTP proxy to Flask; separate mobile pipeline | Not yet deployed |
| **Embedded Satellites** (`apps/`) | React (various) | None (separate projects) | N/A — extract |
| **Tooling** (`admin/`, `cli/`, `tools/`, `scripts/`) | Node.js, PowerShell, Python | Light references | Internal only |

### Version Drift

- `package.json`: 0.8.0
- `VERSION`: 0.7.0

These must be consolidated under a single versioning authority.

---

## 2. Suite Boundary Definition

The **Evident Main Suite** is the forensic evidence platform that ships as a
product. It comprises:

### Core (ships together, one version)

```
evident-core/
├── backend/          ← Flask/FastAPI app server
├── services/         ← 30+ forensic service modules
├── models/           ← SQLAlchemy evidence/case/legal ORM
├── routes/           ← HTTP API surface
├── auth/             ← Supabase JWT + role middleware
├── worker/           ← Celery background processors
├── pipeline/         ← Evidence ETL stage
├── migrations/       ← Alembic schema migrations
└── requirements/     ← Python dependency layers
```

These directories share `auth.models.db`, import freely across boundaries, and
assume a single PostgreSQL schema. They are **one deployable unit** and must
version, test, and release together.

### Companion (ships alongside, own cadence)

```
evident-bwc/
├── backend/          ← FastAPI (isolated DB, auth, S3)
├── frontend/         ← Next.js 14 (single API env var)
└── docs/             ← Architecture, forensic guarantees
```

BWC imports **nothing** from the root backend. It has its own `pyproject.toml`,
own migrations, own Docker Compose. It is already a self-contained product that
happens to live in the same repo.

```
evident-ai/
└── src/ai/           ← Pure Python, zero backend imports
    ├── tools/        ← Legal KB + tool registry
    ├── chat/         ← Memory store, reference manager
    └── pipeline/     ← Orchestrator, adapters, services
```

The AI layer uses only stdlib and its own dataclasses. It communicates with the
backend exclusively via HTTP or message queue. It can ship independently.

### Presentation (separate build, separate deploy)

```
evident-site/
├── src/              ← 11ty layouts, components, pages
├── src/assets/       ← CSS, images, SVG
├── package.json      ← Eleventy + Tailwind build
└── www/              ← Compiled output (GitHub Pages)
```

The marketing site has no runtime dependency on the backend. It builds with
`eleventy` and deploys to a static host. It shares branding assets but no code.

### Extract (remove from this repo)

> **Correction (Step 10):** The original table below incorrectly recommended
> deleting `apps/*` as duplicates of separate repos. Step 10 audit confirmed
> that `apps/*` are the **authoritative npm workspace members** (the source of
> truth), and the desktop `ventures/` copies are the redundant artifacts.
> See [SAFE-CONSOLIDATION.md](SAFE-CONSOLIDATION.md) §0 for full details.

| Directory | Disposition |
| --- | --- |
| `apps/civics-hierarchy/` | ~~Delete local copy.~~ **Retain — npm workspace source of truth.** |
| `apps/epstein-library-evid/` | ~~Delete local copy.~~ **Retain — npm workspace source of truth.** |
| `apps/essential-goods-ledg/` | ~~Delete local copy.~~ **Retain — npm workspace source of truth.** |
| `apps/geneva-bible-study-t/` | ~~Delete local copy.~~ **Retain — npm workspace source of truth.** |
| Desktop `ventures/` copies (4 apps) | Archive or delete. Stale copies with no `.git/`. |
| `tillerstead-toolkit/` | Extract from Evident repo. Different product family, not in npm workspaces. |

### Gateway (evaluate)

| Directory | Disposition |
| --- | --- |
| `src/Evident.Web/` | ASP.NET proxy to Flask. Useful for .NET client auth. Keep if MAUI ships. |
| `src/Evident.Mobile/` | MAUI mobile app. Needs separate CI/CD. Keep in solution, separate pipeline. |
| `src/Evident.Infrastructure/` | Placeholder (empty Class1.cs). Defer until needed. |
| `src/Evident.Shared/` | Shared .NET models. Required by Web + Mobile. Keep. |
| `maui/` | Duplicate of `src/Evident.MatterDocket.MAUI/`? Consolidate. |

---

## 3. Packaging Model

### 3.1 Monorepo with Logical Packages

The repo remains a single Git repository. Splitting into multiple repos adds
coordination overhead without clear benefit at this team size. Instead, enforce
boundaries through **build isolation** and **import discipline**.

```
evident/                          ← Git root
├── core/                         ← Renamed from scattered root dirs
│   ├── app/                      ← Flask/FastAPI entry point (from backend/)
│   ├── services/                 ← Forensic services
│   ├── models/                   ← ORM layer
│   ├── routes/                   ← HTTP API
│   ├── auth/                     ← Identity + access
│   ├── worker/                   ← Background jobs
│   ├── pipeline/                 ← Evidence ETL
│   └── migrations/               ← Schema migrations
├── bwc/                          ← BWC companion (unchanged)
│   ├── backend/
│   ├── frontend/
│   └── docs/
├── ai/                           ← AI pipeline (moved from src/ai/)
│   ├── tools/
│   ├── chat/
│   └── pipeline/
├── site/                         ← Marketing site (moved from src/ 11ty content)
│   ├── _includes/
│   ├── _data/
│   ├── assets/
│   └── pages/
├── dotnet/                       ← .NET solution (moved from src/)
│   ├── Evident.Web/
│   ├── Evident.Mobile/
│   ├── Evident.Shared/
│   └── Evident.Infrastructure/
├── admin/                        ← Admin dashboard (unchanged)
├── cli/                          ← CLI tool (unchanged)
├── tools/                        ← Internal tooling (unchanged)
├── docs/                         ← Documentation (unchanged)
├── tests/                        ← Test suites (unchanged)
├── infrastructure/               ← Deploy configs (unchanged)
└── scripts/                      ← Build/deploy scripts (unchanged)
```

### 3.2 Why This Layout

| Problem | Solution |
| --- | --- |
| Root directories are ambiguous (`src/` mixes .NET, AI, and 11ty) | Each package gets a clear top-level directory |
| Services scatter across `backend/`, `services/`, `models/` | Consolidate under `core/` |
| BWC already isolated but invisible in Render | Give it first-class directory status (already done) |
| AI pipeline buried inside `src/ai/` | Promote to top-level `ai/` |
| `apps/` contains foreign repos | Remove entirely |
| `ventures/` is not product code | Remove entirely |

### 3.3 Import Rules

Once the layout is established, enforce these boundaries:

```
core/   → imports from core/ only (+ stdlib + PyPI packages)
bwc/    → imports from bwc/ only (+ stdlib + PyPI packages)
ai/     → imports from ai/ only (+ stdlib + PyPI packages)
site/   → no Python imports (11ty/Node.js only)
dotnet/ → references dotnet/ projects only (+ NuGet)
```

Cross-package communication is HTTP or message queue only. No shared imports.

---

## 4. Release Strategy

### 4.1 Version Authority

A single `VERSION` file at the repo root governs the suite version. All
packages inherit this version unless they declare an independent version.

```
evident/VERSION           → 0.9.0 (suite version)
bwc/VERSION               → 1.0.0 (independent, BWC is further along)
ai/VERSION                → 0.1.0 (independent, new extraction)
```

`package.json` version must match `evident/VERSION` at build time. A
pre-commit hook or CI check enforces this.

### 4.2 Release Naming

Releases follow `MAJOR.MINOR.PATCH` with no pre-release suffixes in production.

| Version | Meaning |
| --- | --- |
| 0.x.y | Pre-release. Breaking changes expected. |
| 1.0.0 | First production release. API contract locked. |
| x.y.z | Standard semver after 1.0. |

Release tags:

```
evident-core@0.9.0
evident-bwc@1.0.0
evident-ai@0.1.0
evident-site@2025.07   (date-based for marketing site)
```

### 4.3 Release Cadence

| Package | Cadence | Trigger |
| --- | --- | --- |
| `core` | On demand | Backend feature or fix merged to main |
| `bwc` | On demand | BWC feature or fix merged to main |
| `ai` | On demand | AI capability change merged to main |
| `site` | Weekly or on push | Content update pushed to main |

---

## 5. Deployment Topology

### 5.1 Current (Render)

```
render.yaml
└── Evident-legal-tech (web)
    ├── rootDir: backend/
    ├── runtime: python
    └── database: Evident-db (PostgreSQL)
```

Only the root Flask backend deploys today. BWC, AI, site, and .NET are not in
the deployment manifest.

### 5.2 Target

```
render.yaml (or equivalent per platform)
├── evident-core-api (web)
│   ├── rootDir: core/
│   ├── runtime: python
│   ├── workers: 2
│   └── database: evident-core-db (PostgreSQL 16)
│
├── evident-bwc-api (web)
│   ├── rootDir: bwc/backend/
│   ├── runtime: python
│   └── database: evident-bwc-db (PostgreSQL 16)
│
├── evident-bwc-web (static)
│   ├── rootDir: bwc/frontend/
│   ├── buildCommand: npm run build
│   └── publishDir: .next/
│
├── evident-ai-service (worker)
│   ├── rootDir: ai/
│   ├── runtime: python
│   └── queue: Redis
│
└── evident-site (static)
    ├── rootDir: site/
    ├── buildCommand: npx eleventy
    └── publishDir: _site/
```

The .NET components (`dotnet/`) deploy through a separate pipeline (GitHub
Actions → Azure App Service for Web, App Store / Play Store for Mobile).

### 5.3 Domain Mapping

| Service | Domain |
| --- | --- |
| `evident-core-api` | `api.evident.icu` |
| `evident-bwc-api` | `bwc-api.evident.icu` |
| `evident-bwc-web` | `bwc.evident.icu` |
| `evident-ai-service` | Internal only (no public endpoint) |
| `evident-site` | `www.evident.icu` |
| `.NET Gateway` | `gateway.evident.icu` (if shipped) |

---

## 6. Migration Sequence

This is not a "big bang" restructure. Each step is a single PR that can be
reviewed, tested, and reverted independently.

### Phase 1: Clean Extraction (Low Risk)

1. **Delete `apps/` directory** — All four embedded repos exist independently.
   Verify each satellite repo is current, then remove local copies.
2. **Delete `ventures/` directory** — Not product code. Confirm content exists
   in appropriate satellite repos.
3. **Delete `tillerstead-toolkit/` directory** — Already a separate repo in the
   workspace.
4. **Consolidate `maui/` and `src/Evident.MatterDocket.MAUI/`** — Pick one
   location, remove the duplicate.

### Phase 2: Directory Promotion (Medium Risk)

5. **Move `src/ai/` → `ai/`** — Update any import paths. Run tests.
6. **Move 11ty content from `src/` → `site/`** — Update `_config.yml` paths.
   Rebuild. Verify output matches.
7. **Move .NET projects from `src/` → `dotnet/`** — Update `Evident.slnx`
   project paths. Rebuild solution.

### Phase 3: Core Consolidation (Higher Risk)

8. **Create `core/` directory** — Move `backend/`, `services/`, `models/`,
   `routes/`, `auth/`, `worker/`, `pipeline/`, `migrations/` under `core/`.
9. **Fix all import paths** — Update every `from models.X import Y` to
   `from core.models.X import Y` (or use relative imports within `core/`).
10. **Update `render.yaml`** — Point `rootDir` to `core/`.
11. **Consolidate ORM initialization** — All models must use the same
    `declarative_base()` or `db` instance. Eliminate the hybrid
    `auth.models.db` / standalone `declarative_base()` split.

### Phase 4: Independent Deployment

12. **Add BWC to deployment manifest** — Separate Render service (or Docker
    Compose for self-hosted).
13. **Add AI service to deployment manifest** — Worker process with queue
    integration.
14. **Add version enforcement CI** — Pre-commit or CI check that `VERSION` and
    `package.json` agree.
15. **Add import boundary linting** — CI check that `core/` does not import
    from `bwc/` or `ai/`, and vice versa.

---

## 7. ORM Consolidation (Priority Refactor)

The most significant technical debt is the **inconsistent model initialization**
in `models/`:

```python
# Pattern A (most models) — depends on Flask app context
from auth.models import db, User
class Evidence(db.Model):
    ...

# Pattern B (chat_system.py) — standalone SQLAlchemy
from sqlalchemy.orm import declarative_base
Base = declarative_base()
class ChatMessage(Base):
    ...
```

This split prevents clean testing, blocks async migration, and creates implicit
Flask coupling throughout the service layer.

### Resolution

Adopt a single `core/models/base.py`:

```python
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

class Base(DeclarativeBase):
    pass
```

All models import `Base` from this single location. Flask-SQLAlchemy's `db`
wrapper is replaced with direct SQLAlchemy 2.0 patterns, which aligns with the
FastAPI migration already underway in `bwc/`.

---

## 8. Naming Conventions

### Package Names

| Package | PyPI / npm Name | Description |
| --- | --- | --- |
| `core` | `evident-core` | Forensic evidence platform API |
| `bwc` | `evident-bwc` | Body-worn camera evidence workflow |
| `ai` | `evident-ai` | AI analysis and retrieval pipeline |
| `site` | `evident-site` | Marketing and documentation site |
| `admin` | `evident-admin` | Administrative dashboard |
| `cli` | `evident-cli` | Command-line interface |

### Docker Image Names

```
ghcr.io/evident-tech/core:0.9.0
ghcr.io/evident-tech/bwc-api:1.0.0
ghcr.io/evident-tech/bwc-web:1.0.0
ghcr.io/evident-tech/ai-service:0.1.0
```

### Branch Naming

```
main                    ← Production
develop                 ← Integration
feat/core-*             ← Core platform features
feat/bwc-*              ← BWC features
feat/ai-*               ← AI pipeline features
feat/site-*             ← Site content/design
fix/*                   ← Bug fixes (any package)
```

---

## 9. Testing Boundaries

Each package owns its own test suite:

```
tests/
├── core/               ← Backend API + services + models
├── bwc/                ← BWC backend + frontend E2E
├── ai/                 ← AI pipeline unit + integration
├── site/               ← Lighthouse + HTML validation
├── dotnet/             ← xUnit for .NET projects
└── e2e/                ← Cross-package integration (Playwright)
```

CI runs package-specific tests when only that package's files change.
Full suite runs on PRs to `main`.

---

## 10. Decision Record

| Decision | Rationale |
| --- | --- |
| Keep monorepo | Team size does not justify multi-repo coordination cost |
| Logical packages, not physical repos | Boundaries enforced by convention + CI, not Git |
| BWC ships independently | Already self-contained; different release cadence |
| AI ships independently | Zero coupling; microservice-ready |
| Site ships independently | Static build; content cadence differs from API |
| ORM consolidation is prerequisite | Cannot cleanly package `core/` without fixing model layer |
| Delete embedded satellites | Duplicates of existing repos; no unique content |
| Date-based versioning for site | Marketing content is not API-versioned |
| Import boundary linting in CI | Prevents coupling regression after restructure |

---

## References

- [ECOSYSTEM-ARCHITECTURE-MAP.md](ECOSYSTEM-ARCHITECTURE-MAP.md) — Step 1:
  Full ecosystem survey
- [SEPARATION-ANALYSIS.md](SEPARATION-ANALYSIS.md) — Prior separation analysis
- [TIER-ARCHITECTURE-STRATEGY.md](TIER-ARCHITECTURE-STRATEGY.md) — Tier model
- `.evident-repo.json` — Repo identity manifest (Step 4)
