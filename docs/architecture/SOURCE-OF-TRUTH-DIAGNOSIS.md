# Source-of-Truth Diagnosis

**Document:** Packaging Model & Split-Brain Risk Assessment  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident monorepo `apps/` workspace members vs standalone repos in `ventures/`

---

## 1. PROBLEM STATEMENT

The Evident monorepo (`evident-monorepo` v0.8.0) declares npm workspaces for
`apps/*` and `packages/*`. Four satellite apps exist **both** as workspace
members inside `apps/` and as standalone repositories in `ventures/`:

| Workspace member | Standalone repo |
|-----------------|-----------------|
| `apps/civics-hierarchy/` | `ventures/Civics Hierarchy/civics-hierarchy-main/` |
| `apps/epstein-library-evid/` | `ventures/DOJ Document Library Tool/epstein-library-evid-main/` |
| `apps/essential-goods-ledg/` | `ventures/Essential Goods Ledger/essential-goods-ledg-main/` |
| `apps/geneva-bible-study-t/` | `ventures/Geneve Bible Study/geneva-bible-study-t-main/` |

This creates a **split-brain maintenance risk**: edits can land in either copy,
causing silent divergence with no merge mechanism in place.

---

## 2. INVESTIGATION FINDINGS

### 2.1 — Workspace copy characteristics (apps/)

- **No `.git` directory** — part of the Evident monorepo, not independent repos
- **No `.evident-repo.json`** — missing project-level metadata in all 4
- **No `spark.meta.json`** — missing template tracking in all 4
- **Has `dist/` and `node_modules/`** — built and installed state (active dev)
- **Has `package-lock.json`** — local lock files
- **Two have `@evident/` scoped names**: `@evident/epstein-library`,
  `@evident/essential-goods`
- **Two keep original names**: `civics-stack`, `geneva-bible-study`
- **Dependency versions are newer** (e.g., `lucide-react: ^0.575.0` vs
  `^0.484.0`, `recharts: ^3.7.0` vs `^2.15.1`)
- **Some READMEs updated** to reflect project purpose (vs template boilerplate
  in standalone)

### 2.2 — Standalone copy characteristics (ventures/)

- **Has `.evident-repo.json`** — authoritative project metadata in all 4
- **Has `spark.meta.json`** — template provenance tracking in all 4
- **No `dist/` or `node_modules/`** — clean source state
- **Original package names** preserved (`spark-template` in 2/4, proper names
  in 2/4)
- **READMEs vary** — 2/4 have generic "Spark Template" boilerplate, 2/4 match
  workspace versions
- **Has `.gitattributes`** in some (e.g., Geneva Bible Study)

### 2.3 — Dependency version divergence

| Dependency | apps/ (workspace) | ventures/ (standalone) |
|------------|-------------------|----------------------|
| `lucide-react` | `^0.575.0` | `^0.484.0` |
| `recharts` | `^3.7.0` | `^2.15.1` |
| `react-day-picker` | `^9.14.0` | `^9.6.7` |
| `react-hook-form` | `^7.71.2` | `^7.54.2` |

Workspace copies have been upgraded through monorepo-wide `npm update` cycles.
Standalone copies retain original pinned ranges.

### 2.4 — Package name divergence

| Workspace copy | Standalone copy | Diverged? |
|---------------|----------------|-----------|
| `civics-stack` | `civics-stack` | No |
| `@evident/epstein-library` | `spark-template` | Yes — both names wrong |
| `@evident/essential-goods` | `spark-template` | Yes — standalone still placeholder |
| `geneva-bible-study` | `geneva-bible-study` | No |

---

## 3. CANONICAL SOURCE DETERMINATION

**Verdict: Standalone repos are the canonical source for all 4 pairs.**

Evidence:

1. Standalone copies have `.evident-repo.json` (workspace copies do not)
2. Standalone copies have `spark.meta.json` (workspace copies do not)
3. Workspace copies exist only because they were pulled into the monorepo for
   build coordination — they are integration copies, not sources
4. No `.gitmodules` linkage exists (submodules were never configured)
5. Workspace copies carry build artifacts (`dist/`, `node_modules/`) confirming
   they are consumption-side, not source-side

**However** — the workspace copies have received maintenance (dependency bumps,
README updates, `@evident/` scoping) that the standalone copies lack. This
creates a **reverse-drift** situation where the integration copy is ahead of the
source.

---

## 4. CLASSIFICATION TAXONOMY

Every surface in the ecosystem falls into one of these categories:

| Classification | Definition | Sync Direction | Example |
|---------------|------------|---------------|---------|
| **canonical-standalone** | The authoritative source lives in its own repo. All edits originate here. | Source → consumers | `ventures/DOJ Document Library Tool/` |
| **workspace-linked** | A copy inside `apps/` that tracks a canonical standalone. Build/test convenience only. | Standalone → workspace (pull) | `apps/epstein-library-evid/` |
| **monorepo-native** | Source of truth lives inside the Evident monorepo. No external canonical copy. | N/A — single source | `bwc/`, `packages/design-tokens` |
| **deployment-shell** | A thin wrapper that pulls content from another source for deployment. | Source → shell (build-time) |  |
| **migration-artifact** | A copy that will be removed once migration is complete. | Frozen — do not edit | `bwc/frontend/` (if `frontend_new/` is confirmed replacement) |

---

## 5. PER-SURFACE CLASSIFICATION

| # | Surface | Location | Classification | Canonical Source | Notes |
|---|---------|----------|---------------|-----------------|-------|
| 1 | **BWC Frontend** | `Evident/bwc/frontend/` | monorepo-native | `Evident/bwc/frontend/` | Active Next.js 14 app |
| 2 | **BWC Frontend New** | `Evident/bwc/frontend_new/` | migration-artifact | — | Pending migration resolution |
| 3 | **BWC Backend** | `Evident/bwc/backend/` | monorepo-native | `Evident/bwc/backend/` | FastAPI + PostgreSQL |
| 4 | **Evident Marketing** | `Evident/src/` + 11ty | monorepo-native | `Evident/` (root build) | 11ty static site |
| 5 | **Design Tokens** | `Evident/packages/design-tokens/` | monorepo-native | Same | CSS custom properties |
| 6 | **Web Builder** | `Evident/tools/web-builder/` | monorepo-native | Same | Internal admin tool |
| 7 | **Civics Hierarchy** | WS: `apps/civics-hierarchy/` / SA: `ventures/Civics Hierarchy/` | workspace-linked → canonical-standalone | `ventures/Civics Hierarchy/` | Standalone is canonical |
| 8 | **DOJ Document Library** | WS: `apps/epstein-library-evid/` / SA: `ventures/DOJ Document Library Tool/` | workspace-linked → canonical-standalone | `ventures/DOJ Document Library Tool/` | Standalone is canonical |
| 9 | **Essential Goods Ledger** | WS: `apps/essential-goods-ledg/` / SA: `ventures/Essential Goods Ledger/` | workspace-linked → canonical-standalone | `ventures/Essential Goods Ledger/` | Standalone is canonical |
| 10 | **Geneva Bible Study** | WS: `apps/geneva-bible-study-t/` / SA: `ventures/Geneve Bible Study/` | workspace-linked → canonical-standalone | `ventures/Geneve Bible Study/` | Standalone is canonical; Personal project |
| 11 | **Informed Consent** | `ventures/Informed Consent Companion/` | canonical-standalone | Same | No workspace copy — clean |
| 12 | **Founder-Hub** | `Founder-Hub/` | canonical-standalone | Same | Separate repo, no dual copy |
| 13 | **Tillerstead Site** | `ventures/Tillerstead/` | canonical-standalone | Same | Tillerstead LLC — separate business |
| 14 | **Tillerstead Toolkit** | `ventures/tillerstead-toolkit/` | canonical-standalone | Same | Tillerstead LLC — separate business |
| 15 | **Contractor Command** | `ventures/Contractor Command Center/` | canonical-standalone | Same | Tillerstead LLC satellite |
| 16 | **Sweat Equity Insurance** | `ventures/Sweat Equity Insurance/` | canonical-standalone | Same | Tillerstead Ventures LLC experiment |

---

## 6. SPLIT-BRAIN RISK ASSESSMENT

### Active risks

| Risk | Severity | Affected Pairs | Symptom |
|------|----------|---------------|---------|
| **Dependency drift** | Medium | All 4 pairs | Workspace copies have newer deps; standalone copies are stale |
| **Package name mismatch** | High | epstein-library, essential-goods | Workspace uses `@evident/*` scope; standalone uses `spark-template` |
| **README divergence** | Low | civics-hierarchy, epstein-library | Workspace has real descriptions; standalone has boilerplate |
| **Metadata gap** | Medium | All 4 workspace copies | `.evident-repo.json` and `spark.meta.json` exist only in standalone |
| **No sync mechanism** | High | All 4 pairs | No script, CI job, or documented process to sync changes in either direction |
| **Bidirectional edits** | High | All 4 pairs | Contributors could edit either copy without knowing which is canonical |

### Mitigated risks

| Risk | Status | How mitigated |
|------|--------|--------------|
| **Git identity confusion** | Mitigated | Workspace copies have no `.git` — they are clearly part of parent repo |
| **Deploy collision** | Mitigated | Standalone repos deploy independently; workspace copies only serve monorepo builds |
| **Business boundary violation** | Mitigated | BUSINESS-BOUNDARY-RULES.md and `.evident-repo.json` metadata enforced in Phase 2 |

---

## 7. RECOMMENDED RESOLUTION (Phase B — Not Executed Here)

The following recommendations are documented for future execution. **Phase A
(this document) is classification and documentation only.**

### Option A: Remove apps/ workspace copies (Recommended)

1. Remove the 4 directories from `apps/`
2. Update `package.json` workspaces to `"packages/*"` only
3. If monorepo builds need satellite outputs, add them as dev dependencies or
   use a federation script that clones/links at build time
4. All future edits happen in standalone repos only

**Pros:** Eliminates split-brain entirely. One canonical location per app.  
**Cons:** Loses monorepo-wide `npm update` coordination. Build scripts that
reference `apps/*` must be updated.

### Option B: Formalize workspace linking (Alternative)

1. Keep `apps/` but document explicitly that these are downstream copies
2. Add a sync script that pulls from canonical standalone repos
3. Forbid direct edits to `apps/` — all changes must go through standalone first
4. Add CI checks that verify workspace copies match their canonical source

**Pros:** Preserves monorepo build convenience.  
**Cons:** More tooling to maintain. Sync drift remains possible if CI is skipped.

### Recommendation

**Option A** for simplicity and integrity. The monorepo's `build:apps` script
can be replaced with a federation script that reads from standalone repos
without duplicating their source.

---

## 8. IMMEDIATE ACTIONS (Phase A — Executed)

Phase A delivers classification and documentation only. No code is moved, no
repos are merged, no deployment changes are made.

| Action | Deliverable | Status |
|--------|------------|--------|
| Deep comparison of all 4 pairs | This diagnosis document (Section 2) | Complete |
| Classification taxonomy | Section 4 | Complete |
| Per-surface classification | Section 5 | Complete |
| Split-brain risk assessment | Section 6 | Complete |
| SOURCE-OF-TRUTH-MAP.md | `docs/architecture/SOURCE-OF-TRUTH-MAP.md` | Complete |
| PACKAGING-RELATIONSHIPS.md | `docs/architecture/PACKAGING-RELATIONSHIPS.md` | Complete |
| WORKSPACE-LINKING-RULES.md | `docs/architecture/WORKSPACE-LINKING-RULES.md` | Complete |
| Metadata updates | `workspace-registry.json` v3 + `app-catalog.json` v2 | Complete |
