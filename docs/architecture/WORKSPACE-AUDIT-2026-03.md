# Workspace Architecture Audit — March 2026

> Scope: Full ecosystem audit across 12 workspace roots
> Auditor: Automated (Copilot architect mode)
> Date: 2026-03-06

---

## 1. Executive Summary

### State of the Workspace

The Evident ecosystem contains **12 repositories** across 3 physical
directories. The core product (BWC/eDiscovery) lives in `Evident/`. Operations
and founder tooling lives in `Founder-Hub/`. Nine satellite projects live in
`ventures/`. Tillerstead operates as a separate business.

The workspace has strong bones: npm workspaces are configured, 19 active CI
workflows exist, manifests cover 3 of 12 repos, a visual web-builder with
working tab/modal/export systems is in place, and 19 architecture documents
define the intended structure.

### Biggest Risks

1. **Manifest coverage gap.** Only 3 of 12 repos have `.evident-repo.json`.
   The remaining 9 (all satellites) are invisible to the manifest system.
2. **Founder-Hub accessibility.** Navigation lacks `aria-label`, `aria-current`,
   `aria-expanded`, and skip links. WCAG Level AA is not met.
3. **Dead code in web-builder.** `btnCopyAllCommands` listener targets a
   non-existent button. `btnRedoToolbar` has no event handler.
4. **Role confusion.** The workspace registry uses ad-hoc role labels that mix
   structural position (ops, experiment) with product type (satellite-app,
   site). No formal taxonomy governs which label to use.
5. **Registry staleness.** The `workspace-registry.json` sidecar has no
   `remoteUrl` for 9 of 11 entries. Export targets and stacks are partially
   outdated.

### Biggest Opportunities

1. **Role taxonomy.** A formal 7-role system would make every repo's purpose
   and packaging behavior self-documenting.
2. **Manifest propagation.** Adding `.evident-repo.json` to all 9 remaining
   repos would complete the registry and make the web-builder ecosystem-aware.
3. **Founder-Hub ARIA pass.** 5 targeted fixes would bring Navigation.tsx and
   SiteRouter.tsx to WCAG 2.1 AA.
4. **Investor-ready structure.** The repo naming, manifest system, and
   architecture docs already form 70% of a credible presentation. Closing the
   remaining 30% is mostly metadata, not code.

### Immediate Reality Check

- The web-builder is 96% wired. The 4% gap is cosmetic (dead redo button, dead
  copy-all listener).
- Founder-Hub is a real, shipping React 19 SPA with 40+ admin panels, lazy
  loading, and proper code splitting. It is not a demo.
- Evident monorepo's npm workspaces (`apps/*`, `packages/*`) are correctly
  configured. The 4 embedded apps build independently.
- Tillerstead is a separate production business site with its own CI, domain,
  and governance. It must stay separate.
- The architecture doc library (19 files in `docs/architecture/`) is
  comprehensive and internally consistent.

---

## 2. Workspace Inventory Table

| Path | Role | Relationship to Evident | Separate or Satellite | Packaging | Confidence |
|------|------|------------------------|----------------------|-----------|------------|
| `Evident/` | `platform-core` | **IS** the main product | Core | Suite installer; ship as `evident-suite` | High |
| `Founder-Hub/` | `ops-hub` | Founder/operator console for Evident ecosystem | Companion satellite | Standalone deploy to devon-tyler.com | High |
| `ventures/Civics Hierarchy/` | `data-tool` | Evident-family satellite; civic analytics | Product satellite | Independent GitHub Pages deploy | High |
| `ventures/DOJ Document Library Tool/` | `data-tool` | Evident-family satellite; forensic documents | Product satellite | Docker + static deploy | High |
| `ventures/Essential Goods Ledger/` | `data-tool` | Evident-family satellite; economic insight | Product satellite | GitHub Pages + API connectors | High |
| `ventures/Informed Consent Companion/` | `public-app` | Evident-family satellite; consent education | Product satellite | GitHub Pages deploy | High |
| `ventures/Geneve Bible Study/` | `public-app` | Personal/faith; not Evident-branded | Independent venture | PWA + App Store; own brand | High |
| `ventures/Sweat Equity Insurance/` | `experiment` | Tillerstead Ventures IP prototype | Experiment | Not deployable; demo only | High |
| `ventures/Contractor Command Center/` | `public-app` | Tillerstead-family; construction PWA | Product satellite (Tillerstead) | PWA deploy; own brand | High |
| `ventures/tillerstead-toolkit/` | `backend-api` | Tillerstead-family; calculator API | Support tool (Tillerstead) | Railway/Docker backend | High |
| `ventures/Tillerstead/` | `business-site` | **Separate business.** Not Evident. | **Separate** | GitHub Pages + Netlify; tillerstead.com | High |
| `Evident/apps/civics-hierarchy/` | `workspace-member` | npm workspace source inside Evident | Embedded | Builds within monorepo | High |
| `Evident/apps/epstein-library-evid/` | `workspace-member` | npm workspace source inside Evident | Embedded | Builds within monorepo | High |
| `Evident/apps/essential-goods-ledg/` | `workspace-member` | npm workspace source inside Evident | Embedded | Builds within monorepo | High |
| `Evident/apps/geneva-bible-study-t/` | `workspace-member` | npm workspace source inside Evident | Embedded | Builds within monorepo | High |

**Note:** The `apps/` entries inside Evident are the npm workspace SOURCE for 4
of the venture repos. The `ventures/` copies may be stale checkouts or
independent clones. See SAFE-CONSOLIDATION.md for the canonical analysis.

---

## 3. Wiring and Navigation Audit

### Web-Builder (tools/web-builder/index.html)

**Strengths:**
- Tab/tablist wiring is WCAG-compliant (2 tablists, 9 tabs, 9 panels, all
  cross-referenced with `aria-controls` and `aria-labelledby`).
- 4 modals all have `role="dialog"`, `aria-modal="true"`, `aria-labelledby`,
  Escape-to-close, and overlay-click-to-close.
- 27 of 28 buttons are wired to event listeners.
- Keyboard navigation covers Delete, Ctrl+Z, Escape, and arrow keys within
  tablists.
- Zero duplicate IDs across 155+ elements.
- Export panel: all 9 form controls wired (profile selector, target picker,
  filename input, 5 export modes, preflight checklist).

**Issues (2):**

| Issue | Severity | Location |
|-------|----------|----------|
| `btnRedoToolbar` — button exists, no event listener | Medium | HTML ~line 2678; no matching `addEventListener` |
| `btnCopyAllCommands` — listener exists, no button | Low | JS ~line 5543; guarded by `if (copyAllBtn)` so no crash |

**Scaling risks:** The file is ~8,200 lines. Adding more tabs or panels will
push maintainability. Consider extracting CSS into a separate file when the file
exceeds 10,000 lines.

### Founder-Hub (React 19 SPA)

**Strengths:**
- Hash-based routing with 8 views, all lazy-loaded.
- Admin dashboard: 40+ nav items with permission-guarded tab switching.
- Radix UI provides built-in ARIA for tabs, accordions, and dialogs.
- Code splitting: vendor-react, vendor-radix, vendor-icons chunks.
- Clean build output in `dist/`.

**Issues (7):**

| Issue | Severity | Location |
|-------|----------|----------|
| No `aria-label` on main `<nav>` | High | Navigation.tsx |
| No `aria-current="page"` on active nav link | High | Navigation.tsx active link |
| No `aria-expanded` on mobile menu toggle | High | Navigation.tsx hamburger button |
| No `aria-busy` on loading states | Medium | SiteRouter.tsx loader |
| No skip link (`Skip to main content`) | Medium | App-wide |
| 3 unused props in Navigation.tsx (`investorMode`, `onToggleInvestorMode`, `showInvestorToggle`) | Low | Navigation.tsx |
| `useActiveSection` hook does not announce changes to AT | Low | use-active-section.ts |

**Tab systems:** Radix `@radix-ui/react-tabs` used in CaseJacket.tsx. Semantic
and correct. No custom tablist wiring issues.

### Cross-Repo Navigation

There is no shared navigation between Evident and Founder-Hub. This is correct.
They are separate deploys with separate domains. Any cross-linking should be
via standard hyperlinks, not shared state or shared routers.

---

## 4. Recommended Architecture Model

```
┌──────────────────────────────────────────────────┐
│               EVIDENT ECOSYSTEM                   │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  PLATFORM CORE (Evident/)                    │ │
│  │  BWC · eDiscovery · Case Mgmt · Flask API   │ │
│  │  11ty Site · .NET MAUI · npm workspaces     │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  OPS HUB         │  │  PRODUCT SATELLITES  │  │
│  │  Founder-Hub     │  │  Civics Hierarchy    │  │
│  │  devon-tyler.com │  │  DOJ Document Lib    │  │
│  │                   │  │  Essential Goods     │  │
│  │                   │  │  Informed Consent    │  │
│  └─────────────────┘  └─────────────────────┘   │
│                                                   │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  INTERNAL TOOLS  │  │  INDEPENDENT VENTURE │  │
│  │  web-builder     │  │  Geneva Bible Study  │  │
│  │  design-tokens   │  │  (Personal/faith)    │  │
│  │  scripts/        │  │                       │  │
│  └─────────────────┘  └─────────────────────┘   │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  EXPERIMENT                                  │ │
│  │  Sweat Equity Insurance (demo only)          │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│           TILLERSTEAD (SEPARATE BUSINESS)         │
│                                                   │
│  ┌─────────────────┐  ┌─────────────────────┐   │
│  │  BUSINESS SITE   │  │  SUPPORT PRODUCTS    │  │
│  │  Tillerstead/    │  │  tillerstead-toolkit │  │
│  │  tillerstead.com │  │  Contractor CCC      │  │
│  └─────────────────┘  └─────────────────────┘   │
└──────────────────────────────────────────────────┘
```

---

## 5. Top 10 Safest Improvements in Order

### 1. Remove dead `btnCopyAllCommands` listener
- **Why:** Dead code that runs on every page load.
- **Risk:** None. Already guarded by null check.
- **Effort:** 1 minute.
- **Impact:** Cleaner codebase, one fewer false positive in audits.

### 2. Disable or remove `btnRedoToolbar` button
- **Why:** Users see a Redo button that does nothing.
- **Risk:** None. Undo works; Redo was never implemented.
- **Effort:** 1 minute (hide it) or 30 minutes (implement redo).
- **Impact:** Eliminates user confusion.

### 3. Add `aria-label` to Founder-Hub Navigation.tsx
- **Why:** Screen readers cannot identify the main navigation.
- **Risk:** None. One attribute addition.
- **Effort:** 2 minutes.
- **Impact:** WCAG 2.1 AA compliance for main navigation.

### 4. Add `aria-current="page"` to active Founder-Hub nav link
- **Why:** Active section is only communicated visually.
- **Risk:** None.
- **Effort:** 5 minutes.
- **Impact:** Screen reader users know which section is active.

### 5. Add `aria-expanded` to Founder-Hub mobile menu toggle
- **Why:** Mobile menu toggle state invisible to assistive technology.
- **Risk:** None.
- **Effort:** 5 minutes.
- **Impact:** Mobile accessibility compliance.

### 6. Propagate `.evident-repo.json` to all 9 remaining repos
- **Why:** Only 3 of 12 repos have manifests. The web-builder cannot
  auto-detect the rest.
- **Risk:** Low. Additive change; no code impact.
- **Effort:** 30 minutes.
- **Impact:** Complete ecosystem visibility in the builder.

### 7. Update `workspace-registry.json` with GitHub URLs
- **Why:** 9 of 11 entries have empty `remoteUrl`.
- **Risk:** None.
- **Effort:** 15 minutes.
- **Impact:** Registry becomes useful for linking to GitHub.

### 8. Apply formal role taxonomy to all manifests
- **Why:** Current roles (ops, site, experiment, satellite-app) are ad-hoc.
  A formal taxonomy makes packaging behavior deterministic.
- **Risk:** Low. Manifest field changes; no code coupling.
- **Effort:** 20 minutes.
- **Impact:** Clear investor-ready classification of every repo.

### 9. Remove unused Navigation.tsx props in Founder-Hub
- **Why:** `investorMode`, `onToggleInvestorMode`, `showInvestorToggle` are
  declared but never used.
- **Risk:** None. Compile-time verifiable.
- **Effort:** 5 minutes.
- **Impact:** Cleaner component interface.

### 10. Add skip link to Founder-Hub
- **Why:** Keyboard users must tab through all nav items.
- **Risk:** None.
- **Effort:** 10 minutes.
- **Impact:** WCAG 2.1 AA keyboard navigation compliance.

---

## 6. Implementation Phases

### Phase 1 — Critical Wiring and Structure Fixes (Now)
- Fix web-builder dead controls (items 1–2).
- Fix Founder-Hub ARIA gaps (items 3–5, 9–10).
- Estimate: 1 session.

### Phase 2 — Registry and Manifests (After Phase 1)
- Create `.evident-repo.json` for all 9 remaining repos.
- Update `workspace-registry.json` with GitHub URLs and role taxonomy.
- Apply formal role labels.
- Estimate: 1 session.

### Phase 3 — Packaging and Cross-Repo Consistency (After Phase 2)
- Apply design token families to satellites that need them.
- Standardize CI workflow templates per satellite tier.
- Verify stack tier assignments are correct.
- Estimate: 2 sessions.

### Phase 4 — Investor-Ready Presentation (After Phase 3)
- Create ecosystem overview page in Founder-Hub.
- Add release status badges to all manifests.
- Verify all repos build and deploy cleanly.
- Create printable ecosystem map for investor decks.
- Estimate: 2 sessions.

---

## 7. Exact Repair Tasks

### Web-Builder Fixes

| # | Task | File | Action |
|---|------|------|--------|
| W1 | Remove dead `btnCopyAllCommands` listener | web-builder/index.html ~L5543 | Delete the guarded code block (lines 5543–5570) |
| W2 | Hide `btnRedoToolbar` until redo is implemented | web-builder/index.html ~L2678 | Add `style="display:none"` or remove the button |

### Founder-Hub Fixes

| # | Task | File | Action |
|---|------|------|--------|
| F1 | Add `aria-label="Main navigation"` to nav element | Navigation.tsx | Add attribute to `<nav>` |
| F2 | Add `aria-current="page"` to active nav link | Navigation.tsx | Conditionally set on active section link |
| F3 | Add `aria-expanded={isOpen}` to mobile menu button | Navigation.tsx | Add to Sheet trigger button |
| F4 | Remove 3 unused props | Navigation.tsx | Remove investorMode, onToggleInvestorMode, showInvestorToggle |
| F5 | Add skip link before nav | Navigation.tsx or App.tsx | `<a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>` |
| F6 | Add `aria-busy={true}` to loading states | SiteRouter.tsx | Add to loading container |

### Manifest Propagation

| # | Repo | Action |
|---|------|--------|
| M1 | Civics Hierarchy | Create `.evident-repo.json` |
| M2 | DOJ Document Library Tool | Create `.evident-repo.json` |
| M3 | Essential Goods Ledger | Create `.evident-repo.json` |
| M4 | Informed Consent Companion | Create `.evident-repo.json` |
| M5 | Geneva Bible Study | Create `.evident-repo.json` |
| M6 | Sweat Equity Insurance | Create `.evident-repo.json` |
| M7 | Contractor Command Center | Create `.evident-repo.json` |
| M8 | tillerstead-toolkit | Create `.evident-repo.json` |

### Registry Update

| # | Task | File | Action |
|---|------|------|--------|
| R1 | Add GitHub URLs to all 11 entries | workspace-registry.json | Fill `remoteUrl` fields |
| R2 | Apply formal role taxonomy | workspace-registry.json | Update `role` fields per taxonomy |

---

## 8. Proposed Files to Add

| File | Location | Purpose |
|------|----------|---------|
| `.evident-repo.json` × 8 | Each satellite repo root | Manifest for builder auto-detection |
| `ROLE-TAXONOMY.md` | `docs/architecture/` | Formal role definitions (see Section 12 below) |
| _(already exists)_ `workspace-registry.json` | `tools/web-builder/` | Needs update, not creation |
| _(already exists)_ `ECOSYSTEM-ARCHITECTURE-MAP.md` | `docs/architecture/` | Already covers ecosystem layout |
| _(already exists)_ `SATELLITE-PACKAGING-MODEL.md` | `docs/architecture/` | Already covers satellite tiers |
| _(already exists)_ `BUILD-RELEASE-WORKFLOW.md` | `docs/architecture/` | Already covers release flow |

**Assessment:** The architecture doc library is already comprehensive. Only
ROLE-TAXONOMY.md and the 8 manifest files are genuinely missing. No new design
documents are needed.

---

## 9. Branch Strategy

```
fix/web-builder-dead-controls       ← Phase 1: W1, W2
fix/founder-hub-aria                ← Phase 1: F1–F6
feat/satellite-manifests            ← Phase 2: M1–M8
feat/role-taxonomy                  ← Phase 2: R1, R2, ROLE-TAXONOMY.md
chore/registry-github-urls          ← Phase 2: R1
```

---

## 10. Git Commit Plan

```
1. fix(web-builder): remove dead btnCopyAllCommands listener
2. fix(web-builder): hide btnRedoToolbar until redo is implemented
3. fix(founder-hub): add aria-label to main navigation
4. fix(founder-hub): add aria-current to active nav link
5. fix(founder-hub): add aria-expanded to mobile menu toggle
6. fix(founder-hub): remove unused investorMode props from Navigation
7. fix(founder-hub): add skip link for keyboard navigation
8. feat(manifests): add .evident-repo.json to 8 satellite repos
9. feat(taxonomy): add ROLE-TAXONOMY.md with formal role definitions
10. chore(registry): update workspace-registry with GitHub URLs and roles
```

---

## 11. What Should Not Be Merged

| Repo | Must Stay Separate | Reason |
|------|-------------------|--------|
| **Tillerstead** | Yes — separate business, separate domain, separate governance | Different LLC, different brand, different audience. Shared standards are optional. |
| **tillerstead-toolkit** | Yes — Tillerstead family, not Evident | Backend API for Tillerstead products. Not Evident-branded. |
| **Contractor Command Center** | Yes — Tillerstead family | Construction PWA. Tillerstead brand. |
| **Geneva Bible Study** | Yes — personal/faith project | Not Evident-branded. Not Tillerstead. Independent. |
| **Sweat Equity Insurance** | Yes — experiment | Tillerstead Ventures IP. Not deployable. |

**What CAN be tightly integrated (already is):**
- `apps/civics-hierarchy` ← npm workspace member of Evident
- `apps/epstein-library-evid` ← npm workspace member of Evident
- `apps/essential-goods-ledg` ← npm workspace member of Evident
- `apps/geneva-bible-study-t` ← npm workspace member of Evident
- `packages/design-tokens` ← shared package within Evident

---

## 12. Role Taxonomy System

### Recommended Roles (7)

| Role | Slug | Definition |
|------|------|-----------|
| **Platform Core** | `platform-core` | The primary product. Contains the main codebase, API, database models, deployment config. There is only one per ecosystem. |
| **Ops Hub** | `ops-hub` | Founder/operator console. Admin dashboard, governance, CRM, site management. Tightly coupled to the ecosystem but deploys independently. |
| **Product Satellite** | `product-satellite` | A user-facing application that extends the ecosystem. Ships independently. May share branding with the main suite. |
| **Support Tool** | `support-tool` | Internal tooling — calculators, APIs, admin scripts, dev utilities. Not user-facing. Supports products but is not itself a product. |
| **Business Site** | `business-site` | A marketing or authority website for a distinct business entity. Has its own domain, brand, and audience. |
| **Independent Venture** | `independent-venture` | A standalone product with its own brand and audience. Not part of the main suite ecosystem. May share infrastructure patterns but not branding. |
| **Experiment** | `experiment` | A prototype, concept demo, or feasibility study. Not production-ready. Not deployed. May graduate to another role. |

### How Role Affects Packaging and Release

| Role | Can Be Released? | Shares Main Brand? | Included in Suite Installer? | Requires CI? | Deploy Target |
|------|-----------------|--------------------|-----------------------------|-------------|---------------|
| `platform-core` | Yes — semver | Yes | Yes — IS the suite | Yes — full | Render, GH Pages |
| `ops-hub` | Yes — semver | Yes (operator-facing) | No — separate deploy | Yes — full | GH Pages (own domain) |
| `product-satellite` | Yes — semver | Optional | No — linked, not bundled | Yes — basic+ | GH Pages, Docker |
| `support-tool` | Optional | No | No | Optional | Railway, Docker, none |
| `business-site` | Yes — date-based | No — own brand | No | Yes — basic | GH Pages, Netlify |
| `independent-venture` | Yes — semver | No — own brand | No | Optional | GH Pages, App Stores |
| `experiment` | No | No | No | No | None |

### How Role Affects Web-Builder Behavior

| Role | Builder Export? | Preflight Level | Stack Tier Notice | Registry Badge |
|------|----------------|----------------|-------------------|---------------|
| `platform-core` | Yes — full suite | Strict (all 6 checks) | Shows stack tier | Blue badge |
| `ops-hub` | Limited — prompt tier | Strict | Shows "Prompt — React 19" | Purple badge |
| `product-satellite` | Varies by stack tier | Standard (4 checks) | Shows stack tier | Green badge |
| `support-tool` | No — metadata only | N/A | "Builder cannot export for this stack" | Gray badge |
| `business-site` | Yes — native or aware | Standard | Shows stack tier | Teal badge |
| `independent-venture` | Varies by stack tier | Standard | Shows stack tier | Amber badge |
| `experiment` | Optional | Minimal (2 checks) | May show warning | Red/outline badge |

### Visual Badges for UI

```css
/* Role badges for registry cards and export panel */
.role-badge[data-role="platform-core"]       { background: #1f6feb20; color: #58a6ff; }
.role-badge[data-role="ops-hub"]             { background: #8957e520; color: #bc8cff; }
.role-badge[data-role="product-satellite"]   { background: #3fb95020; color: #3fb950; }
.role-badge[data-role="support-tool"]        { background: #8b949e15; color: #8b949e; }
.role-badge[data-role="business-site"]       { background: #3fb9a720; color: #3fb9a7; }
.role-badge[data-role="independent-venture"] { background: #d2992220; color: #d29922; }
.role-badge[data-role="experiment"]          { background: #f8514920; color: #f85149; border-style: dashed; }
```

### Applying the Taxonomy

| Repo | Current Role | Recommended Role |
|------|-------------|-----------------|
| Evident | `main-suite-core` | `platform-core` |
| Founder-Hub | `ops` | `ops-hub` |
| Civics Hierarchy | `satellite-app` | `product-satellite` |
| DOJ Document Library | `satellite-app` | `product-satellite` |
| Essential Goods Ledger | `satellite-app` | `product-satellite` |
| Informed Consent Companion | `satellite-app` | `product-satellite` |
| Geneva Bible Study | `satellite-app` | `independent-venture` |
| Sweat Equity Insurance | `experiment` | `experiment` (correct) |
| Contractor Command Center | `satellite-app` | `product-satellite` (Tillerstead family) |
| tillerstead-toolkit | `satellite-app` | `support-tool` |
| Tillerstead | `site` | `business-site` |

---

## 13. Next Best Prompt

After reviewing this audit, run the following prompt to execute Phase 1:

```
You are operating as a disciplined refactoring assistant in my Evident
ecosystem workspace.

TASK: Execute Phase 1 repairs from the March 2026 Workspace Audit.

SCOPE:
1. In tools/web-builder/index.html:
   - Remove the dead btnCopyAllCommands listener (lines ~5543–5570).
   - Hide btnRedoToolbar by adding style="display:none" until redo is
     implemented.

2. In Founder-Hub (C:\Users\Devon Tyler\Desktop\Founder-Hub):
   - Add aria-label="Main navigation" to the <nav> in Navigation.tsx.
   - Add aria-current="page" to the active nav link in Navigation.tsx.
   - Add aria-expanded={isOpen} to the mobile menu toggle in Navigation.tsx.
   - Remove the unused props: investorMode, onToggleInvestorMode,
     showInvestorToggle from the Navigation component.
   - Add a skip link (<a href="#main-content" class="sr-only
     focus:not-sr-only">Skip to main content</a>) before the nav in
     App.tsx or the layout root.
   - Add aria-busy={true} to the loading indicator in SiteRouter.tsx.

RULES:
- Make minimal, targeted edits.
- Do not refactor surrounding code.
- Preserve all existing functionality.
- Commit-ready changes only.
```

---

*This audit is grounded in actual file reads across all 12 workspace
repositories. Confidence levels are marked in the inventory table. No claims
are made about repos that were not inspected.*
