# Dual-Business Deployment Plan

**Document:** Publication & Deployment Architecture  
**Date:** 2026-03-06  
**Status:** Approved baseline  
**Scope:** Evident Technologies LLC + Tillerstead LLC — full ecosystem

---

## 1. EXECUTIVE SUMMARY

**Best overall direction:** Two clean, separately-deployed business ecosystems
sharing only governance conventions and manifest schema. Evident Technologies
ships the BWC/eDiscovery Suite as its primary product, with satellite apps
federated through a catalog surface. Tillerstead ships its contractor site and
toolkit as wholly separate products under separate domain, deployment, and legal
boundaries.

**Biggest cleanup needs:**

- The `apps/` directory inside Evident contains 4 satellite app copies that
  duplicate repos already in `ventures/`. These embedded copies should be
  removed; the canonical source is the standalone repo for each.
- 9 of 11 workspace-registry entries lack `remoteUrl` values.
- The `bwc/` directory has two frontend directories (`frontend/` and
  `frontend_new/`) — indicating a migration that needs resolution.
- Most satellite repos use placeholder names (`spark-template`) in their
  `package.json`.
- 5 of 8 venture READMEs contain generic Spark template content.

**Biggest deployment risks:**

- The Evident CNAME (`www.evident.icu`) differs from the manifest's `siteUrl`
  (`https://evidenttechnologies.com`). This must be reconciled before
  publication.
- BWC backend deploys to Render (free tier) with a 20 GB upload limit; the app
  may require a paid plan before production traffic.
- Founder-Hub is deployed to `devon-tyler.com` — this is a personal domain, not
  an Evident product domain. Its role as "ops hub" must be clarified.
- Tillerstead Toolkit backend has no public domain; it is currently configured
  for Railway with CORS allowing `tillerstead.com` origins only.

**Biggest packaging opportunities:**

- The BWC subsystem (`bwc/`) is the strongest product asset. Packaging it with a
  dedicated subdomain (`app.evident.icu` or `suite.evidenttechnologies.com`)
  creates a clear product surface.
- Tillerstead Toolkit could be surfaced on `tools.tillerstead.com` or embedded
  at `tillerstead.com/tools/` via iframe, providing immediate value.
- Founder-Hub's ToolHub registry already catalogs all apps — making it the
  natural admin gateway if rebranded properly.

---

## 2. BUSINESS BOUNDARY MAP

### Evident Technologies LLC

| Layer | Contents |
|-------|----------|
| **Core product** | BWC / eDiscovery Suite — forensic evidence processing, chain of custody, case management |
| **Primary domain** | `evident.icu` (CNAME) or `evidenttechnologies.com` (manifest) — must reconcile |
| **Backend** | FastAPI (BWC) + Flask (legacy API) on Render |
| **Frontend** | Next.js 14 (BWC), 11ty (marketing site), .NET MAUI (desktop/mobile) |
| **Satellite apps** | DOJ Document Library, Civics Hierarchy, Essential Goods Ledger, Informed Consent Companion |
| **Support tools** | Web Builder, CLI (`cli/evident.py`), PowerShell tools, design tokens |
| **Ops hub** | Founder-Hub (devon-tyler.com) — admin, CRM, ToolHub, governance |
| **Internal only** | Web Builder, build scripts, RAG context, test harnesses |
| **Must stay separate** | Tillerstead LLC products, Sweat Equity Insurance (Tillerstead IP), Contractor Command Center (Tillerstead vertical) |

### Tillerstead LLC

| Layer | Contents |
|-------|----------|
| **Core product** | Tillerstead marketing site — TCNA-compliant contractor presence |
| **Primary domain** | `tillerstead.com` (CNAME + Netlify) |
| **Backend** | Tillerstead Toolkit API on Railway (FastAPI + PostgreSQL) |
| **Frontend** | Jekyll static site (marketing), TillerPro web tools |
| **Satellite apps** | Tillerstead Toolkit (calculator hub), Contractor Command Center (estimation PWA) |
| **Experiments** | Sweat Equity Insurance (Tillerstead Ventures LLC IP) |
| **Internal only** | Toolkit backend admin, calculator engine internals |
| **Must stay separate** | All Evident Technologies products, Founder-Hub, legal-tech satellites |

### Shared — Conventions Only

| Shared Item | Mechanism |
|-------------|-----------|
| Manifest schema (`evident-repo.json` format) | Convention — each repo uses independently |
| Governance patterns (copilot-instructions) | Convention — each business adapts |
| Design token CSS variables | Optional import — no runtime coupling |
| Workspace registry format | Read-only catalog — no deployment coupling |

---

## 3. REPO AND APP CLASSIFICATION TABLE

| # | Name | Business | Role | Visibility | Maturity | Package Rec | Deploy Rec | Action |
|---|------|----------|------|-----------|----------|-------------|------------|--------|
| 1 | **Evident** | Evident LLC | platform-core | Public site + private backend | Beta | Monorepo — suite ships from here | Render (API) + GH Pages (site) | Keep — primary product |
| 2 | **Founder-Hub** | Evident LLC | ops-hub | Private (admin portal) | Beta | Standalone deploy | GH Pages → devon-tyler.com | Keep — clarify domain story |
| 3 | **DOJ Document Library** | Evident LLC | product-satellite | Public (deferred) | Experimental | Independent repo + Docker | Docker / Railway | Keep separate — strongest satellite |
| 4 | **Civics Hierarchy** | Evident LLC | product-satellite | Public (deferred) | Experimental | Independent repo | GH Pages | Keep separate |
| 5 | **Essential Goods Ledger** | Evident LLC | product-satellite | Public (deferred) | Experimental | Independent repo | GH Pages | Keep separate |
| 6 | **Informed Consent Companion** | Evident LLC | product-satellite | Public (beta) | Experimental | Independent repo | GH Pages | Keep separate |
| 7 | **Geneva Bible Study** | Personal | product-satellite | Public (production) | Production (v1.0) | Independent repo, MIT license | GH Pages + app stores | Keep separate — only prod-ready satellite |
| 8 | **Tillerstead** | Tillerstead LLC | business-site | Public (production) | Stable | Independent repo | Netlify → tillerstead.com | Keep separate — different LLC |
| 9 | **tillerstead-toolkit** | Tillerstead LLC | support-tool | Public (deferred) | Beta | Independent repo | Railway (API) | Keep separate — different LLC |
| 10 | **Contractor Command Center** | Tillerstead LLC | product-satellite | Public (deferred) | Experimental | Independent repo | GH Pages | Keep separate — Tillerstead vertical |
| 11 | **Sweat Equity Insurance** | Tillerstead Ventures LLC | experiment | Private (demo only) | MVP | Static files — no build system | Not deployed | Archive or keep private |
| 12 | **apps/civics-hierarchy** | Evident LLC | embedded-copy | N/A | N/A | Remove from monorepo | N/A | **Remove** — duplicate of standalone |
| 13 | **apps/epstein-library-evid** | Evident LLC | embedded-copy | N/A | N/A | Remove from monorepo | N/A | **Remove** — duplicate of standalone |
| 14 | **apps/essential-goods-ledg** | Evident LLC | embedded-copy | N/A | N/A | Remove from monorepo | N/A | **Remove** — duplicate of standalone |
| 15 | **apps/geneva-bible-study-t** | Evident LLC | embedded-copy | N/A | N/A | Remove from monorepo | N/A | **Remove** — duplicate of standalone |
| 16 | **bwc/frontend_new** | Evident LLC | migration-wip | N/A | N/A | Merge into bwc/frontend or remove | N/A | **Resolve** — pick canonical frontend |

---

## 4. RECOMMENDED DEPLOYMENT ARCHITECTURE

```
EVIDENT TECHNOLOGIES LLC — DEPLOYMENT MAP
══════════════════════════════════════════

  evident.icu (or evidenttechnologies.com)       ← reconcile domain first
  ├─ www.evident.icu                              ← marketing site (11ty → GH Pages)
  ├─ app.evident.icu                              ← BWC Suite (Next.js → Render or Vercel)
  ├─ api.evident.icu                              ← BWC API (FastAPI → Render)
  └─ docs.evident.icu  (optional)                 ← public docs (GH Pages)

  devon-tyler.com                                 ← Founder-Hub / ops portal (GH Pages)
  ├─ devon-tyler.com/#admin                       ← admin dashboard
  ├─ devon-tyler.com/#offerings                   ← services catalog
  └─ devon-tyler.com/#s/{slug}                    ← published microsites

  Satellite Apps (GH Pages — each on own subdomain or path):
  ├─ dtmbx.github.io/civics-hierarchy             ← Civics Hierarchy
  ├─ dtmbx.github.io/informed-consent-com         ← Informed Consent
  ├─ dtmbx.github.io/essential-goods-ledg         ← Essential Goods Ledger
  └─ dtmbx.github.io/epstein-library              ← DOJ Library (static shell only)


TILLERSTEAD LLC — DEPLOYMENT MAP
════════════════════════════════

  tillerstead.com                                 ← marketing site (Jekyll → Netlify)
  ├─ tillerstead.com/tools/                       ← TillerPro tools (embedded or linked)
  ├─ tillerstead.com/calculators/                 ← calculator landing pages
  └─ tillerstead.com/reviews/                     ← testimonials

  api.tillerstead.com (or Railway default URL)    ← Toolkit API (FastAPI → Railway)
  ├─ /api/calculators
  ├─ /api/jobs
  ├─ /api/products
  └─ /api/rooms

  Contractor Command Center:
  └─ dtmbx.github.io/contractor-command-center    ← PWA (GH Pages, standalone)

  Sweat Equity Insurance:
  └─ NOT DEPLOYED — private demo only
```

**Separation safeguards:**

- Evident and Tillerstead never share a domain, subdomain, or hosting account.
- No CORS configuration ever lists both `evident.icu` and `tillerstead.com` as
  allowed origins.
- Deployment pipelines are entirely separate (different repos, different
  workflow files, different hosting targets).
- DNS records are managed independently.

---

## 5. TILLERSTEAD TOOLKIT INTEGRATION PLAN

### Options Compared

| Method | Description | Boundary Preservation | UX Quality | Implementation Effort | Recommended? |
|--------|-------------|----------------------|------------|----------------------|-------------|
| **Direct embed** | Import toolkit components into Tillerstead static site via JS bundle | Poor — couples codebases | Seamless | High — requires build pipeline in Jekyll | No |
| **iframe embed** | Load toolkit at `api.tillerstead.com/calculators/` inside `<iframe>` on `tillerstead.com/tools/` | Excellent — complete isolation | Good with `postMessage` sizing | Low | **Yes — primary** |
| **Linked standalone** | Link from `tillerstead.com/tools/` to separate toolkit URL | Excellent — no coupling | Moderate — user leaves site | Minimal | Yes — fallback |
| **Shared design shell** | Build a shell app that loads both via micro-frontend | Good | Best | Very high — overengineered | No |

### Recommended: iframe embed with linked fallback

1. Tillerstead marketing site adds a `/tools/` or `/calculators/` page.
2. That page renders an `<iframe>` pointing to the toolkit's deployed URL
   (Railway or dedicated static host).
3. The toolkit API returns pre-rendered calculator UIs or a lightweight SPA.
4. `postMessage` protocol handles:
   - Calculator result passing (toolkit → parent)
   - Resize signaling (toolkit → parent, for responsive height)
   - Theme synchronization (parent → toolkit, optional)
5. Fallback: if iframe/JS disabled, the page shows a direct link to the
   standalone toolkit URL.
6. No shared build system, no shared JS bundle, no shared node_modules.

**Boundary contract** (see `embed-contract.md` in Phase 2):

- Toolkit iframe must not access parent DOM.
- Parent must not inject scripts into iframe.
- Only structured `postMessage` data is exchanged.
- Toolkit owns its own auth, session, data, and API calls.
- Branding inside the iframe follows Tillerstead LLC visual standards only.

---

## 6. TOP 12 SAFEST IMPROVEMENTS IN ORDER

| # | Title | Why It Matters | Risk | Effort | Impact |
|---|-------|---------------|------|--------|--------|
| 1 | **Reconcile Evident domain** (evident.icu vs evidenttechnologies.com) | Two domain references in config; confusing in production | Low — config-only change | Small | High — foundational |
| 2 | **Remove `apps/` embedded satellite copies** | 4 duplicate app trees inflate the monorepo and diverge from canonical repos | Low — removing copies only | Small | High — cleans monorepo |
| 3 | **Resolve `bwc/frontend` vs `bwc/frontend_new`** | Two frontend directories create confusion about canonical source | Medium — must verify which is current | Medium | High — unblocks BWC deploy |
| 4 | **Add `.evident-repo.json` to all satellite repos** | 9 of 12 entries in registry lack manifests; invisible to tooling | Low — metadata only | Small | Medium — enables catalog |
| 5 | **Fill `remoteUrl` in workspace-registry.json** | 9 of 11 entries missing; registry is incomplete | None | Trivial | Medium |
| 6 | **Rename `spark-template` in satellite package.json files** | 5 repos share the same generic name; confuses tooling | None | Trivial | Medium |
| 7 | **Replace placeholder READMEs** in 5 venture repos | Generic Spark template text; no project identity | None | Small | Medium — investor-readability |
| 8 | **Add skip link and ARIA landmarks** to Founder-Hub | WCAG 2.1 AA compliance gap | None | Small | Medium — accessibility |
| 9 | **Create `business-boundary-rules.md`** | No formal document enforces LLC separation | None | Small | High — governance |
| 10 | **Create `embed-contract.md` for Tillerstead Toolkit** | No formal integration spec exists | None | Small | Medium — prevents coupling |
| 11 | **Create deployment-map.md** | No single document maps domain → hosting → repo | None | Small | Medium — ops clarity |
| 12 | **Rotate Founder-Hub default credentials** | Default admin password published in SECURITY.md | Medium if deployed as-is | Trivial | High — security |

---

## 7. CLEANUP PLAN

### Phase 1 — Repo and Naming Cleanup

- Confirm which `bwc/frontend*` directory is canonical; mark the other for removal.
- Tag `apps/` satellite copies as redundant in a tracking comment or remove them.
- Rename `spark-template` in satellite `package.json` files to proper names.
- Update Evident `.evident-repo.json` if domain is reconciled.
- Confirm workspace-registry family assignments are correct.
- Commit with: `chore: phase-1 repo cleanup — naming, dedup, structure`

### Phase 2 — Manifests and Classification

- Add `.evident-repo.json` to all satellite repos that lack one.
- Update `workspace-registry.json` with GitHub URLs and corrected metadata.
- Create: `business-boundary-rules.md`, `embed-contract.md`, `deployment-map.md`.
- Create `app-catalog.json` (machine-readable catalog of all published apps).
- Commit with: `chore: phase-2 manifests, boundary docs, catalog`

### Phase 3 — Navigation and Portal Cleanup

- Finalize Founder-Hub ARIA fixes (skip link, aria-current, etc.).
- Ensure web-builder sidebar correctly lists only real apps.
- Add Tillerstead Toolkit embed surface to Tillerstead site (or stub page).
- Confirm all navigation links across sites point to correct domains.
- Commit with: `feat: phase-3 navigation, portal, accessibility`

### Phase 4 — Deployment Cleanup

- Reconcile Evident domain (`evident.icu` vs `evidenttechnologies.com`).
- Configure subdomain for BWC app (`app.evident.icu`).
- Verify Tillerstead Netlify deploy is clean and pointing to correct CNAME.
- Confirm Railway deploy for Tillerstead Toolkit is operational.
- Audit CORS origins in all backends.
- Commit with: `chore: phase-4 deployment reconciliation`

### Phase 5 — Publication and Release Readiness

- Set version numbers in all publishable repos (semver).
- Add LICENSE files where missing.
- Rotate or remove default credentials from published repos.
- Run Lighthouse audit on all public surfaces.
- Tag first release for the most-ready surfaces.
- Commit with: `chore: phase-5 release prep — versions, licenses, audit`

---

## 8. FILES TO ADD

| File | Location | Purpose |
|------|----------|---------|
| `business-boundary-rules.md` | `Evident/docs/architecture/` | Formal LLC separation rules |
| `embed-contract.md` | `Evident/docs/architecture/` | Tillerstead Toolkit embed protocol |
| `deployment-map.md` | `Evident/docs/architecture/` | Domain → hosting → repo mapping |
| `app-catalog.json` | `Evident/tools/web-builder/` | Machine-readable published app catalog |
| `.evident-repo.json` | Each satellite repo root | Manifest for classification and discovery |

---

## 9. PUBLISHING ORDER

| Order | Surface | Domain | What Ships | Blocking Issues |
|-------|---------|--------|------------|-----------------|
| 1 | **Tillerstead marketing site** | tillerstead.com | Jekyll static site | None — already live |
| 2 | **Evident marketing site** | evident.icu / evidenttechnologies.com | 11ty static site | Domain reconciliation |
| 3 | **Geneva Bible Study** | dtmbx.github.io/... | React PWA (v1.0) | README cleanup |
| 4 | **Founder-Hub (ops portal)** | devon-tyler.com | React SPA | Credential rotation, ARIA fixes |
| 5 | **Tillerstead Toolkit API** | Railway URL → api.tillerstead.com | FastAPI backend | Railway config verification |
| 6 | **Informed Consent Companion** | dtmbx.github.io/... | React SPA | README cleanup |
| 7 | **Civics Hierarchy** | dtmbx.github.io/... | React SPA | README cleanup |
| 8 | **Essential Goods Ledger** | dtmbx.github.io/... | React SPA | README, API key management |
| 9 | **BWC / eDiscovery Suite** | app.evident.icu | Next.js + FastAPI | Frontend resolution, backend hardening |
| 10 | **DOJ Document Library** | Docker / Railway | React + FastAPI | Docker config, security review |
| 11 | **Contractor Command Center** | dtmbx.github.io/... | React PWA | Needs deployment workflow |
| 12 | **Sweat Equity Insurance** | NOT PUBLISHED | Static demo | Regulatory clarity required |

---

## 10. WHAT SHOULD NOT BE MERGED

### Must Stay Separate — LLC Boundary

| Evident Technologies LLC | Tillerstead LLC |
|-------------------------|-----------------|
| Evident monorepo | Tillerstead site repo |
| Founder-Hub | tillerstead-toolkit |
| DOJ Document Library | Contractor Command Center |
| Civics Hierarchy | Sweat Equity Insurance |
| Informed Consent Companion | |
| Essential Goods Ledger | |

### Should Share Standards Only

- Manifest schema (`.evident-repo.json` format) — convention, not dependency
- Design token CSS variables — optional import
- Copilot instruction patterns — each business adapts independently

### Should Never Be Co-Branded

- Evident + Tillerstead must not appear on the same branded page.
- Founder-Hub must not display Tillerstead as an "Evident product."
- Tillerstead must not reference Evident in its marketing.
- Shared workspace tooling (web-builder) is internal-only — not customer-facing.

### Should Be Linked Rather Than Embedded

- Tillerstead Toolkit calculators: iframe embed on tillerstead.com is permitted;
  direct code import is not.
- Satellite apps from Evident catalog: linked from Founder-Hub ToolHub, not
  bundled into the main suite.
- Contractor Command Center: linked from Tillerstead site, not merged into it.

---

## 11. BRANCH AND COMMIT PLAN

### First 6 Branch Names

```
chore/phase-1-repo-cleanup
chore/phase-2-manifests-and-boundaries
feat/phase-3-navigation-portal
chore/phase-4-deployment-reconciliation
chore/phase-5-release-prep
docs/dual-business-architecture
```

### First 12 Commit Messages

```
1.  docs: add dual-business deployment plan
2.  chore: add business-boundary-rules.md
3.  chore: add embed-contract.md for Tillerstead Toolkit
4.  chore: add deployment-map.md skeleton
5.  chore: add app-catalog.json
6.  chore: update workspace-registry.json with GitHub URLs and roles
7.  chore: add .evident-repo.json to DOJ Document Library
8.  chore: add .evident-repo.json to Civics Hierarchy
9.  chore: add .evident-repo.json to Essential Goods Ledger
10. chore: add .evident-repo.json to Informed Consent Companion
11. chore: add .evident-repo.json to Geneva Bible Study
12. chore: add .evident-repo.json to Contractor Command Center
```

---

## 12. NEXT IMPLEMENTATION PROMPT

> Execute Phase 1 and Phase 2 of the Dual-Business Deployment Plan.
>
> **Phase 1** — Repo and naming cleanup:
> - Confirm `apps/` satellite copies are redundant vs standalone repos
> - Confirm BWC frontend canonical directory
> - Fix workspace-registry.json metadata
> - Validate family assignments
>
> **Phase 2** — Manifests and contracts:
> - Create `.evident-repo.json` for all satellite repos lacking one
> - Create `business-boundary-rules.md`
> - Create `embed-contract.md` for Tillerstead Toolkit
> - Create `deployment-map.md` skeleton
> - Create `app-catalog.json`
> - Update `workspace-registry.json` with GitHub URLs
>
> Rules:
> - Do not merge Evident and Tillerstead.
> - Do not begin deployment changes.
> - Keep edits explicit and auditable.
> - Provide commit messages for each logical group.
