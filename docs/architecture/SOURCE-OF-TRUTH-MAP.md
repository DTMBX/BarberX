# Source-of-Truth Map

**Document:** Canonical source table for every app and surface  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident Technologies LLC + Tillerstead LLC + Personal — full ecosystem

---

## Purpose

This document declares the single canonical source for every deployable surface
in the ecosystem. When a discrepancy exists between two copies of the same
codebase, the **canonical source** listed here governs.

No surface may have two places where original edits are permitted.

---

## Quick Reference

| Surface | Canonical Source | Business | Classification |
| ------- | --------------- | -------- | -------------- |
| BWC Frontend | `Evident/bwc/frontend/` | Evident LLC | monorepo-native |
| BWC Frontend New | `Evident/bwc/frontend_new/` | Evident LLC | migration-artifact |
| BWC Backend | `Evident/bwc/backend/` | Evident LLC | monorepo-native |
| Evident Marketing | `Evident/` (root 11ty build) | Evident LLC | monorepo-native |
| Design Tokens | `Evident/packages/design-tokens/` | Evident LLC | monorepo-native |
| Web Builder | `Evident/tools/web-builder/` | Evident LLC | monorepo-native |
| Founder-Hub | `Founder-Hub/` | Evident LLC | canonical-standalone |
| Civics Hierarchy | `ventures/Civics Hierarchy/` | Evident LLC | canonical-standalone |
| DOJ Document Library | `ventures/DOJ Document Library Tool/` | Evident LLC | canonical-standalone |
| Essential Goods Ledger | `ventures/Essential Goods Ledger/` | Evident LLC | canonical-standalone |
| Informed Consent | `ventures/Informed Consent Companion/` | Evident LLC | canonical-standalone |
| Geneva Bible Study | `ventures/Geneve Bible Study/` | Personal | canonical-standalone |
| Tillerstead Site | `ventures/Tillerstead/` | Tillerstead LLC | canonical-standalone |
| Tillerstead Toolkit | `ventures/tillerstead-toolkit/` | Tillerstead LLC | canonical-standalone |
| Contractor Command | `ventures/Contractor Command Center/` | Tillerstead LLC | canonical-standalone |
| Sweat Equity Insurance | `ventures/Sweat Equity Insurance/` | Tillerstead Ventures LLC | canonical-standalone |

---

## Workspace Copies (Non-Canonical)

The following directories inside `Evident/apps/` are **workspace-linked copies**
of their canonical standalone repos. They exist for monorepo build coordination
and must not be treated as sources of truth.

| Workspace copy | Canonical source | Sync direction |
| -------------- | --------------- | -------------- |
| `apps/civics-hierarchy/` | `ventures/Civics Hierarchy/civics-hierarchy-main/` | Standalone → workspace |
| `apps/epstein-library-evid/` | `ventures/DOJ Document Library Tool/epstein-library-evid-main/` | Standalone → workspace |
| `apps/essential-goods-ledg/` | `ventures/Essential Goods Ledger/essential-goods-ledg-main/` | Standalone → workspace |
| `apps/geneva-bible-study-t/` | `ventures/Geneve Bible Study/geneva-bible-study-t-main/` | Standalone → workspace |

### How to identify the canonical copy

1. **`.evident-repo.json` present** → canonical source
2. **`spark.meta.json` present** → canonical source
3. **No `.git` directory and part of Evident monorepo** → workspace-linked copy
4. **`@evident/` scoped package name** → workspace integration rename, not canonical
5. **`dist/` and `node_modules/` present** → consumption-side copy

---

## Known Divergence (Current State)

These divergences exist as of the audit date and must be reconciled in Phase B:

| Aspect | Workspace (apps/) | Standalone (ventures/) | Resolution |
| ------ | ----------------- | --------------------- | ---------- |
| Dependency versions | Newer (monorepo-wide updates) | Older (original pins) | Back-port updates to standalone |
| Package names (2/4) | `@evident/*` scoped | `spark-template` placeholder | Fix standalone names; remove @evident scope or formalize it |
| README content (2/4) | Real project descriptions | Spark template boilerplate | Copy workspace READMEs to standalone |
| `.evident-repo.json` | Missing | Present | Already correct — canonical has metadata |
| `spark.meta.json` | Missing | Present | Already correct — canonical has metadata |

---

## Classification Definitions

| Classification | Meaning | Edit policy |
| -------------- | ------- | ----------- |
| **monorepo-native** | Source of truth lives inside the Evident monorepo. No external canonical copy. | Edit in place. |
| **canonical-standalone** | The authoritative source lives in its own repo/folder. | Edit only in the standalone location. |
| **workspace-linked** | A copy inside `apps/` that tracks a canonical standalone. | Do not edit directly. Sync from standalone. |
| **migration-artifact** | A copy that will be removed after migration completes. | Do not edit. Freeze until resolved. |
| **deployment-shell** | A thin wrapper that pulls content from another source at build time. | Edit wrapper config only; content comes from source. |

---

## Enforcement

1. All pull requests that touch an `apps/` workspace copy must reference the
   corresponding standalone repo to confirm the canonical source has been
   updated first.
2. CI may verify that workspace copies do not diverge from their canonical
   source beyond an allowed delta (dependency versions due to monorepo update
   cycles).
3. New satellite apps must be created as standalone repos first, then optionally
   linked into the monorepo workspace.
