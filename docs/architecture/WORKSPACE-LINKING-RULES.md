# Workspace Linking Rules

**Document:** Rules for apps/ workspace members vs standalone repos  
**Date:** 2026-03-06  
**Status:** Active — apps/ copies deprecated  
**Scope:** Evident monorepo `apps/*` workspace members

---

## Purpose

The Evident monorepo declares `"workspaces": ["apps/*", "packages/*"]`
in its root `package.json`. This document governs how the four satellite
apps inside `apps/` relate to their canonical standalone repos and what
operations are permitted on each.

---

## Current State

> **DEPRECATION NOTICE (Phase 3B):** The four `apps/` workspace copies
> listed below are classified as `deprecatedIntegrationCopy: true`. They
> must not receive new edits. A federation pipeline
> (`build-federate.ps1`) is being introduced to replace them with
> deterministic clones from canonical repos. See BUILD-FEDERATION-SPEC.md
> and FEDERATION-STRATEGY.md for the migration plan.

Four satellite apps exist as workspace members inside `apps/`:

| Workspace path | Canonical standalone | Status |
| -------------- | -------------------- | ------ |
| `apps/civics-hierarchy/` | `ventures/Civics Hierarchy/civics-hierarchy-main/` | Deprecated copy |
| `apps/epstein-library-evid/` | `ventures/DOJ Document Library Tool/epstein-library-evid-main/` | Deprecated copy |
| `apps/essential-goods-ledg/` | `ventures/Essential Goods Ledger/essential-goods-ledg-main/` | Deprecated copy |
| `apps/geneva-bible-study-t/` | `ventures/Geneve Bible Study/geneva-bible-study-t-main/` | Deprecated copy |

These workspace copies are **not** the source of truth. The standalone
repos are canonical (see SOURCE-OF-TRUTH-MAP.md).

---

## Rules

### Rule 1 — Canonical source governs

All original development — features, fixes, documentation — must happen
in the standalone repo first. The `apps/` copy is a downstream consumer.

### Rule 2 — No direct feature edits in apps/

Contributors must not add features, write documentation, or create new
files directly in `apps/`. If a workspace copy has drifted ahead of its
canonical source (as is currently the case with dependency versions and
README updates), that content must be back-ported to the standalone repo
to restore correctness.

### Rule 3 — Permitted operations in apps/

The following changes are permitted directly in `apps/` workspace copies:

| Operation | Permitted | Reason |
| --------- | --------- | ------ |
| Monorepo-wide `npm update` | Yes | Keeps workspace deps consistent |
| `@evident/` package name scoping | Yes | Monorepo integration convention |
| Build config adjustments (`vite.config`, `tsconfig`) | Yes | Workspace compatibility |
| Adding workspace-only dev dependencies | Yes | Build tooling |
| Feature development | **No** | Must happen in standalone first |
| README or documentation edits | **No** | Back-port from standalone |
| New source files | **No** | Must originate in standalone |

### Rule 4 — Sync direction is one-way

```text
Standalone repo (canonical)  ──→  apps/ workspace copy
         source                      consumer
```

Changes flow from standalone to workspace, never the reverse. If the
workspace copy has changes that the standalone lacks, those changes must
be extracted and committed to the standalone repo.

### Rule 5 — Sync mechanism (current)

There is currently **no automated sync mechanism**. Syncing is manual.
Until a sync script or CI check is implemented:

1. Before editing an `apps/` surface, check the standalone repo for
   the latest version.
2. After a monorepo-wide dependency update, document which deps were
   bumped so they can be back-ported.
3. Periodically compare `apps/` copies against their canonical source
   to detect drift.

### Rule 6 — Build integration

The monorepo's `build:apps` script (`scripts/build-apps.js`) builds
all `apps/*` members. This is the primary reason workspace copies exist.

If `apps/` copies are removed in a future phase (recommended in
SOURCE-OF-TRUTH-DIAGNOSIS.md Section 7), the build script must be
updated to:

- Clone or symlink canonical repos at build time, or
- Reference pre-built outputs from satellite CI pipelines, or
- Remove the federation build entirely if satellites deploy independently

### Rule 7 — Package naming convention

| Pattern | Meaning |
| ------- | ------- |
| `@evident/{name}` | Monorepo-scoped integration name (workspace copy) |
| Original name (e.g., `civics-stack`) | Canonical package name (standalone) |
| `spark-template` | Placeholder name — must be fixed in standalone |

When both copies exist, the standalone's package name is authoritative.
The `@evident/` scope exists only for npm workspace resolution within
the monorepo.

### Rule 8 — Metadata files

| File | Must exist in standalone | Must exist in apps/ |
| ---- | ----------------------- | ------------------- |
| `.evident-repo.json` | Yes — authoritative metadata | No — not needed |
| `spark.meta.json` | Yes — template provenance | No — not needed |
| `package.json` | Yes — with canonical name | Yes — may have scoped name |
| `README.md` | Yes — with real content | Optional — may mirror |
| `dist/` | No — clean source | Yes — build artifact |
| `node_modules/` | No — clean source | Yes — workspace install |

### Rule 9 — Deprecation status

As of Phase 3B, all four `apps/` workspace copies carry the
classification `deprecatedIntegrationCopy: true`. This means:

- **No new features, fixes, or documentation** may be added to these
  directories.
- **Monorepo-wide dependency updates** may still touch them, but only
  until the federation pipeline replaces them.
- **The federation pipeline** (`build-federate.ps1`) will produce
  equivalent output from canonical repos. Once parity is confirmed
  (Phase 3C), these directories will be removed (Phase 3D).
- **Direct edits are forbidden.** Any change to an `apps/` copy must
  instead be made in the canonical standalone repo.

---

## Known Violations (Current State)

These violations of the above rules exist today and should be resolved
in Phase 3C/3D:

| Violation | Affected | Resolution |
| --------- | -------- | ---------- |
| Workspace copies have newer deps than standalone | All 4 pairs | Back-port version bumps to standalone |
| Workspace READMEs differ from standalone | civics-hierarchy, epstein-library | Copy workspace README to standalone |
| Two standalone repos use `spark-template` name | epstein-library, essential-goods | Set proper names in standalone |
| No sync script exists | All 4 pairs | Federation pipeline replaces manual sync |
| apps/ copies still present after deprecation | All 4 | Remove in Phase 3D after parity confirmed |

---

## Decision Record

| Decision | Date | Rationale |
| -------- | ---- | --------- |
| Standalone repos are canonical | 2026-03-06 | `.evident-repo.json` and `spark.meta.json` exist only in standalone |
| Workspace copies are downstream | 2026-03-06 | No `.git`, have build artifacts, were pulled in for workspace integration |
| Recommended future action: remove apps/ | 2026-03-06 | Eliminates split-brain risk entirely |
| Phase A: document only, no code moves | 2026-03-06 | Establish clarity before making structural changes |
| Phase 3B: apps/ copies deprecated | 2026-03-06 | Federation pipeline replaces manual workspace copies |
| Phase 3B: shallow clone chosen over submodules | 2026-03-06 | Cleaner separation, simpler UX, single version source |
| Phase 3B: versionLock added to registry | 2026-03-06 | Enables deterministic pinned builds from canonical repos |
