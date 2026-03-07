# Safe Merge / Consolidation Strategy

> Step 10 of the Evident Ecosystem Architecture Series
>
> Principle: **Unify by structure, not by force. Standardize before merging.
> Merge only what cannot remain separate.**

---

## 0. Correction to Step 5

Step 5 (Main Suite Packaging Plan, §2 Extract) recommended deleting `apps/*` on
the assumption that separate repos existed elsewhere. This was incorrect.

**Verified facts (Step 10 audit):**

| Item | Actual State |
| --- | --- |
| `apps/civics-hierarchy/` | npm workspace member. The **source of truth**. |
| `apps/epstein-library-evid/` | npm workspace member. Scoped as `@evident/epstein-library`. |
| `apps/essential-goods-ledg/` | npm workspace member. Scoped as `@evident/essential-goods`. |
| `apps/geneva-bible-study-t/` | npm workspace member. The **source of truth**. |
| `ventures/` on Desktop | Extracted copies (no `.git/`). Diverged from `apps/`. Archive or delete. |
| `tillerstead-toolkit/` | Tracked in Evident git, NOT in npm workspaces. Different product family. |
| `packages/design-tokens` | Shared workspace package (`@evident/design-tokens` v1.0.0). In use. |

**Revised recommendation:** Do not delete `apps/`. They are the authoritative
workspace members. The desktop `ventures/` copies are the redundant artifacts.

---

## 1. Structural Overview

```text
evident/                          ← Single git repo, npm workspaces
├── apps/                         ← 4 React workspace members (SOURCE)
│   ├── civics-hierarchy/
│   ├── epstein-library-evid/
│   ├── essential-goods-ledg/
│   └── geneva-bible-study-t/
├── packages/                     ← 1 shared package
│   └── design-tokens/            ← @evident/design-tokens v1.0.0
├── tillerstead-toolkit/          ← Git-tracked, NOT in npm workspaces
├── backend/                      ← Flask/FastAPI Python backend
├── bwc/                          ← Body-worn camera subsystem
├── src/ai/                       ← AI pipeline
├── src/ (11ty)                   ← Marketing site
└── ...                           ← Admin, CLI, .NET, tools
```

External repos (own git, own deploy):

```text
Founder-Hub/                      ← React 19, devon-tyler.com
Tillerstead/                      ← Jekyll, tillerstead.com
```

Desktop copies (no `.git/`, diverged):

```text
ventures/Civics Hierarchy/        ← Stale copy of apps/civics-hierarchy
ventures/DOJ Document Library/    ← Stale copy of apps/epstein-library-evid
ventures/Essential Goods Ledger/  ← Stale copy of apps/essential-goods-ledg
ventures/Geneve Bible Study/      ← Stale copy of apps/geneva-bible-study-t
ventures/Contractor Command Center/  ← Standalone (not in monorepo)
ventures/Informed Consent Companion/ ← Standalone (not in monorepo)
ventures/Sweat Equity Insurance/     ← Standalone (static HTML)
```

---

## 2. Classification: Merge, Separate, or Standardize

Every directory and shared concern falls into one of three dispositions.

### 2.1 — KEEP TOGETHER (already merged, retain)

These belong in the Evident monorepo and should stay.

| Item | Reason |
| --- | --- |
| `apps/*` (4 React apps) | npm workspace members. Shared build pipeline. Shared design tokens. |
| `packages/design-tokens` | Shared dependency consumed by all `apps/*`. |
| `backend/`, `services/`, `models/`, `routes/`, `auth/` | Core product. Tight ORM coupling. Ships as one unit. |
| `bwc/` | Companion product. Self-contained but co-versioned with core. |
| `src/ai/` | AI pipeline. Zero coupling but benefits from co-location for testing. |
| `admin/`, `cli/`, `tools/`, `scripts/` | Internal tooling. Light. No extraction benefit. |

### 2.2 — EXTRACT (remove from this repo)

| Item | Action | Reason |
| --- | --- | --- |
| `tillerstead-toolkit/` | Move to `ventures/Tillerstead/` or its own repo. | Different product family. Not in npm workspaces. Not tested by monorepo CI. Dead weight. |
| Desktop `ventures/` copies (4 apps) | Archive or delete. | Diverged, no `.git/`, superseded by `apps/`. |

### 2.3 — STANDARDIZE WITHOUT MERGING

These remain in separate repos but adopt shared standards.

| Item | Shared Standard | Mechanism |
| --- | --- | --- |
| Founder-Hub | Design tokens, manifest schema, build workflow | `.evident-repo.json` manifest + foundation tokens |
| Tillerstead | Design tokens (tillerstead family), manifest schema | `.evident-repo.json` manifest + `tillerstead.foundation.css` |
| Contractor Command Center | Manifest schema only | `.evident-repo.json` when promoted past prototype |
| Informed Consent Companion | Component conventions, manifest schema | `.evident-repo.json` + shadcn patterns |
| Sweat Equity Insurance | Manifest schema only | `.evident-repo.json` when promoted past prototype |

---

## 3. Shared Code Consolidation Plan

### 3.1 Duplicate Utilities — Severity Assessment

| Utility | Count | Consistency | Risk | Action |
| --- | --- | --- | --- | --- |
| `cn()` (clsx + twMerge) | 9 | Identical across all React repos | Low | Extract to `@evident/utils` |
| `debounce()` | 10+ | Fragmented (6 in Evident assets, 2 Tillerstead, 1 CCC) | Medium | Extract to `@evident/utils`; retire site-layer copies |
| `validateEmail()` | 10+ | Fragmented (regex variants, 3 languages) | Medium | Extract per-language canonical; share in respective packages |
| `formatCurrency()` | 10+ | Highly fragmented (5+ patterns) | High | Standardize on `Intl.NumberFormat`; extract to `@evident/utils` |
| `formatDate()` | 10+ | Fragmented | Medium | Standardize on `Intl.DateTimeFormat`; extract to `@evident/utils` |

### 3.2 New Shared Package: `@evident/utils`

Add to `packages/utils/` in the monorepo:

```text
packages/
├── design-tokens/    ← Existing
└── utils/            ← New
    ├── package.json
    ├── src/
    │   ├── cn.ts
    │   ├── debounce.ts
    │   ├── format-currency.ts
    │   ├── format-date.ts
    │   └── validate-email.ts
    └── tsconfig.json
```

**Scope rules:**

- Only pure, side-effect-free functions.
- Zero runtime dependencies beyond `clsx` and `tailwind-merge`.
- Each function exported individually (tree-shakeable).
- All functions deterministic. No randomness. No network calls.

**Migration:**

1. Create `@evident/utils` package.
2. Move canonical implementations.
3. Update imports in each `apps/*` workspace member.
4. Delete duplicate implementations.
5. Satellite repos import via npm (when/if published) or copy the source file.

### 3.3 Shared Configuration Presets

Configs that are identical or near-identical across all 5 React projects:

| File | Status | Consolidation |
| --- | --- | --- |
| `components.json` | Identical (5/5) | Move to workspace root. Symlink or reference from each app. |
| `tsconfig.json` | Identical (5/5) | Create `packages/tsconfig/tsconfig.base.json`. Each app extends it. |
| `tailwind.config.js` | Near-identical (trivial diffs) | Create `packages/tailwind-config/`. Each app imports and overrides. |
| `vite.config.ts` | Near-identical (only base path differs) | Create `packages/vite-config/` exporting a factory: `createViteConfig({ base })`. |
| `eslint.config.js` | Diverged | Founder-Hub has full config; apps inherit from root. Standardize on Founder-Hub pattern. Defer. |

**Priority order:** tsconfig (zero risk) → tailwind (low risk) → vite factory
(medium risk) → eslint (defer).

---

## 4. Dependency Version Alignment

### 4.1 Current State

| Metric | Value |
| --- | --- |
| Shared packages across React projects | 54 |
| Identical versions | 50 (93%) |
| Major version drift | 4 packages |
| Internal apps alignment | 100% (all 4 Evident apps synchronized) |

### 4.2 Major Version Drift

| Package | Evident Apps | Founder-Hub | Migration Path |
| --- | --- | --- | --- |
| `zod` | 3.25 | 4.3 | Upgrade Evident apps to Zod 4. Breaking: schema API changes. Test all validators. |
| `uuid` | 11.1 | 13.0 | Upgrade Evident apps to uuid 13. Likely non-breaking for `v4()` usage. |
| `@hookform/resolvers` | 4.1 | 5.2 | Upgrade Evident apps. Test all form validation. |
| `lucide-react` | 0.575 | 0.484 | Upgrade Founder-Hub to 0.575. Non-breaking (additive icon updates). |

**Alignment strategy:**

1. Upgrade Evident apps to match Founder-Hub on `zod`, `uuid`,
   `@hookform/resolvers`.
2. Upgrade Founder-Hub to match Evident apps on `lucide-react`.
3. Pin coordinated versions in a root-level constraints file or
   `pnpm-workspace.yaml` overrides.

### 4.3 Founder-Hub Exclusive Dependencies

These exist only in Founder-Hub and reflect its unique scope:

| Package | Purpose | Share? |
| --- | --- | --- |
| `@playwright/test` | E2E testing | Adopt in monorepo CI when ready |
| `vitest` | Unit testing | Adopt in monorepo CI when ready |
| `@supabase/supabase-js` | Auth + DB client | Already in Evident backend (Python). JS client stays Founder-Hub-only. |
| `@stripe/stripe-js` | Payment integration | Founder-Hub-only |
| `@xterm/xterm` | Terminal emulator UI | Founder-Hub-only |

No action needed. These are product-specific, not candidates for sharing.

---

## 5. What Must NOT Be Merged

### 5.1 Repos That Stay Separate

| Repo | Reason |
| --- | --- |
| **Founder-Hub** | Different deploy target (devon-tyler.com). Different auth (Supabase direct). Different product scope (operations hub, not evidence platform). |
| **Tillerstead** | Different tech stack (Jekyll). Different brand family. Different domain (tillerstead.com). Production site. |
| **Contractor Command Center** | Static prototype. No shared code. No shared infra. |
| **Sweat Equity Insurance** | Static prototype. Vanilla HTML. No build system. |
| **Informed Consent Companion** | Separate product. Separate compliance scope (HIPAA-adjacent). |

### 5.2 Warning Signs Against Merging

A merge should be rejected if any of the following are true:

1. **Different deploy targets.** If two projects deploy to different hosts,
   domains, or infrastructure, merging adds coordination cost with no build
   benefit.

2. **Different compliance boundaries.** Evidence platform code and
   health-consent code have different regulatory exposure. Co-locating them
   creates audit scope creep.

3. **Different release cadences.** If one project ships weekly and another ships
   quarterly, a shared repo creates release friction.

4. **Different tech stacks.** Jekyll and React have nothing to share at the
   build layer. Co-location adds tooling burden.

5. **Single-person team.** At current team size, multi-repo coordination cost is
   near zero. The overhead of monorepo governance exceeds the benefit of
   co-location for satellites.

6. **Evidentiary risk.** Merging code into the Evident repo expands the
   forensic audit surface. Every line in the repo is subject to chain-of-custody
   scrutiny. Non-evidence code does not belong in that scope.

---

## 6. Consolidation Sequence

Ordered by risk (lowest first) and dependency (prerequisites before dependents).

### Phase 1 — Cleanup (no code changes)

| # | Action | Risk | Reversible |
| --- | --- | --- | --- |
| 1.1 | Archive or delete desktop `ventures/` copies of the 4 apps already in `apps/`. | None | Yes (re-extract from GitHub) |
| 1.2 | Move `tillerstead-toolkit/` out of Evident repo into its own repo or into `ventures/Tillerstead/`. | Low | Yes (git history preserved via filter-branch or subtree split) |
| 1.3 | Correct Step 5 document: replace "Delete local copy" with "Retain — workspace source of truth" for all `apps/*` entries. | None | N/A (documentation) |

### Phase 2 — Shared Packages (additive only)

| # | Action | Risk | Reversible |
| --- | --- | --- | --- |
| 2.1 | Create `packages/tsconfig/` with `tsconfig.base.json`. Each app extends it. | Low | Yes (revert extends, keep local copy) |
| 2.2 | Create `packages/utils/` with `cn`, `debounce`, `formatCurrency`, `formatDate`, `validateEmail`. | Low | Yes (revert imports) |
| 2.3 | Create `packages/tailwind-config/` with shared preset. Each app imports and overrides. | Low | Yes |
| 2.4 | Create `packages/vite-config/` with `createViteConfig()` factory. | Medium | Yes |

### Phase 3 — Dependency Alignment (coordinate upgrades)

| # | Action | Risk | Reversible |
| --- | --- | --- | --- |
| 3.1 | Upgrade `uuid` v11 → v13 in all Evident apps. | Low | Yes (downgrade) |
| 3.2 | Upgrade `@hookform/resolvers` v4 → v5 in all Evident apps. Test forms. | Medium | Yes (downgrade + revert) |
| 3.3 | Upgrade `zod` v3 → v4 in all Evident apps. Test all schema validators. | High | Yes but labor-intensive |
| 3.4 | Upgrade `lucide-react` to latest in Founder-Hub. | Low | Yes |
| 3.5 | Pin shared versions in workspace root `package.json` overrides. | Low | Yes |

### Phase 4 — Config Deduplication (after Phase 2 proves stable)

| # | Action | Risk | Reversible |
| --- | --- | --- | --- |
| 4.1 | Replace per-app `tsconfig.json` with `extends` references. | Low | Yes |
| 4.2 | Replace per-app `tailwind.config.js` with shared import + local overrides. | Medium | Yes |
| 4.3 | Replace per-app `vite.config.ts` with factory call. | Medium | Yes |
| 4.4 | Consolidate `components.json` to workspace root. | Low | Yes |
| 4.5 | Standardize ESLint config across all apps (adopt Founder-Hub pattern). | Medium | Yes |

---

## 7. Decision Matrix

For each future consolidation question, apply this matrix:

| Question | If YES → | If NO → |
| --- | --- | --- |
| Do both projects share the same deploy target? | Consider merging. | Keep separate. |
| Do both projects share the same compliance scope? | Consider merging. | Keep separate. |
| Do both projects share >80% of their dependency tree? | Standardize deps. | Standardize nothing. |
| Do both projects share >50% of their config files? | Extract shared config package. | Keep local configs. |
| Do both projects share utility code? | Extract shared utility package. | No action. |
| Does merging expand the forensic audit surface? | Do not merge. | Proceed with caution. |
| Is the code deterministic and reproducible? | Safe to share. | Isolate. |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Zod v3→v4 migration breaks schema validation | High | High | Create branch. Run full test suite per app before merge. |
| Shared config package introduces build failures | Medium | Medium | Each app retains fallback local config during transition. |
| Removing `ventures/` copies loses uncommitted work | Low | Medium | Diff against `apps/` source before deleting. Archive first. |
| `tillerstead-toolkit/` extraction loses git history | Medium | Low | Use `git subtree split` to preserve commit history. |
| Utility package becomes a coupling point | Low | Medium | Enforce pure-function-only rule. No shared state. No side effects. |

---

## 9. Post-Consolidation State

After all phases complete, the workspace looks like this:

```text
evident/                          ← Single git repo
├── apps/                         ← 4 React workspace members
│   ├── civics-hierarchy/
│   ├── epstein-library-evid/
│   ├── essential-goods-ledg/
│   └── geneva-bible-study-t/
├── packages/                     ← Shared workspace packages
│   ├── design-tokens/            ← @evident/design-tokens (existing)
│   ├── utils/                    ← @evident/utils (new)
│   ├── tsconfig/                 ← @evident/tsconfig (new)
│   ├── tailwind-config/          ← @evident/tailwind-config (new)
│   └── vite-config/              ← @evident/vite-config (new)
├── core/                         ← Evident platform backend (per Step 5)
├── bwc/                          ← BWC companion
├── ai/                           ← AI pipeline
├── site/                         ← Marketing site (11ty)
├── dotnet/                       ← .NET gateway + mobile
├── admin/                        ← Admin dashboard
├── cli/                          ← CLI tools
├── tools/                        ← Internal tooling (incl. web-builder)
├── docs/                         ← Architecture + governance
├── tokens/                       ← Foundation token source files
└── infrastructure/               ← Deploy configs

External (separate repos, shared standards only):
  Founder-Hub/                    ← devon-tyler.com
  Tillerstead/                    ← tillerstead.com
  tillerstead-toolkit/            ← Extracted from Evident
```


### Dependency Count (Estimated)

| Before | After |
| --- | --- |
| 54 shared packages, 4 at major drift | 54 shared packages, 0 at major drift |
| 10+ duplicate `debounce` implementations | 1 canonical in `@evident/utils` |
| 12 identical `components.json` files | 1 at workspace root |
| 5 near-identical `tsconfig.json` files | 1 base + 5 `extends` references |
| 0 shared config packages | 4 shared config packages |

---

## 10. Governance

### Who Decides to Merge

Any merge of a satellite into the monorepo requires:

1. A document explaining why separation no longer serves the project.
2. Confirmation that the merge does not expand the forensic audit surface.
3. A reversibility plan (how to split back out if needed).

No merge is executed on convenience alone.

### Review Cadence

- **Quarterly:** Review `workspace-registry.json` for stale entries.
- **Per release:** Verify shared package versions are aligned.
- **Per new satellite:** Apply the decision matrix (§7) before onboarding.

---

*This document supersedes the "Extract" section of Step 5 (MAIN-SUITE-PACKAGING-PLAN.md)
regarding `apps/*` disposition. All other Step 5 recommendations remain valid.*
