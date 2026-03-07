# Satellite Packaging Model

> Step 6 of the Evident Ecosystem Architecture Series
>
> Principle: **Related but not merged. Clear enough for a stranger to
> understand in five minutes.**

---

## 1. Satellite Inventory

Eleven repositories live outside the main Evident BWC / eDiscovery Suite. Each
one ships independently, deploys independently, and owns its own release cycle.

| # | Name | Stack | Output | Maturity | Deploy | Family |
|---|------|-------|--------|----------|--------|--------|
| 1 | Founder-Hub | React 19 + TS + Vite | Web app | Beta | GitHub Pages | Evident |
| 2 | DOJ Document Library | React + TS + FastAPI + Docker | Web app | Beta | Docker / Railway | Evident |
| 3 | Civics Hierarchy | React + TS + Vite | Static site | Alpha | GitHub Pages | Evident |
| 4 | Informed Consent Companion | React 19 + TS + Vite | Web app | Beta | GitHub Pages | Evident |
| 5 | Essential Goods Ledger | React + TS + D3 | Static site | Beta | GitHub Pages | Evident |
| 6 | Tillerstead | Jekyll + HTML/CSS/JS | Static site | Production | tillerstead.com | Tillerstead |
| 7 | tillerstead-toolkit | FastAPI + React | Web app | Alpha | Railway | Tillerstead |
| 8 | Contractor Command Center | React + TS + PWA | PWA | Production | GitHub Pages | Tillerstead |
| 9 | Sweat Equity Insurance | HTML + Vanilla JS | Static page | Prototype | Embedded | Tillerstead |
| 10 | Geneva Bible Study | React + TS + Capacitor | PWA + Native | Stable | GitHub Pages + Stores | Personal |
| 11 | BWC (embedded in Evident) | FastAPI + Next.js 14 | Web app | Beta | Not yet deployed | Evident |

---

## 2. Satellite Categories

Satellites are grouped by their **relationship to the main suite**, not by
topic or technology. Three tiers.

### Tier 1 — Companion Satellites

Apps that extend, reference, or directly serve the Evident platform's mission.
They share the Evident brand vocabulary, governance standards, and may appear in
the platform's tool launcher.

| App | Why Companion |
|-----|---------------|
| DOJ Document Library | Forensic document analysis. Strongest satellite. Overlapping evidence patterns. |
| Civics Hierarchy | Government jurisdiction reference used alongside legal discovery workflows. |
| Informed Consent Companion | Consent documentation aligns with due process and accountability. |
| Essential Goods Ledger | Economic data context for damages, cost-of-living, and compliance analysis. |
| Founder-Hub | Operations layer. Manages the registry, billing, and governance for the family. |
| BWC subsystem | Body-worn camera workflow. Ships from the main repo but with independent cadence. |

**Brand rule:** May use "Evident" or "by Evident Technologies" in their
identity. Registered in the Founder-Hub ToolHub manifest.

### Tier 2 — Venture Satellites

Apps under the same ownership but serving a different business vertical. They
share governance patterns and coding standards but not the Evident product
brand.

| App | Why Venture |
|-----|-------------|
| Tillerstead | Tile contracting business site. Separate brand, separate domain. |
| tillerstead-toolkit | Contractor calculators and project tools. Serves Tillerstead operations. |
| Contractor Command Center | Construction estimation PWA. Offline-capable field tool. |
| Sweat Equity Insurance | Insurance model prototype. Exploratory, not production. |

**Brand rule:** Uses its own brand ("Tillerstead", "Contractor Command Center").
May reference "Evident Technologies" only in footer attribution or legal
notices, never in product identity.

### Tier 3 — Independent Satellites

Apps with no direct relationship to either the Evident platform or a venture
vertical. They exist in the ecosystem because they share an owner and
governance standards.

| App | Why Independent |
|-----|----------------|
| Geneva Bible Study | Personal Bible reader. Completely standalone. No business relationship to Evident. |

**Brand rule:** No Evident branding. Standalone product identity. Shares only
coding conventions and manifest schema.

---

## 3. Naming Conventions

### 3.1 Repository Names

Repository names are the permanent identifier. They must be:

- lowercase with hyphens (no spaces, no underscores)
- descriptive enough to understand without context
- prefixed by family when disambiguation is needed

| Current Name | Recommended Slug | Notes |
|---|---|---|
| Evident | `evident` | Main suite. No prefix needed. |
| Founder-Hub | `founder-hub` | Ops layer. Already correct. |
| DOJ Document Library Tool | `doj-document-library` | Drop "Tool" suffix — redundant. |
| Civics Hierarchy | `civics-hierarchy` | Already correct. |
| Informed Consent Companion | `informed-consent-companion` | Already correct. |
| Essential Goods Ledger | `essential-goods-ledger` | Already correct. |
| Tillerstead | `tillerstead` | Already correct. |
| tillerstead-toolkit | `tillerstead-toolkit` | Already correct. |
| Contractor Command Center | `contractor-command-center` | Already correct. |
| Sweat Equity Insurance | `sweat-equity-insurance` | Already correct. |
| Geneva Bible Study | `geneva-bible-study` | Already correct. |

### 3.2 Display Names

Display names appear in the web-builder registry, the ToolHub catalog, and any
user-facing launcher. They follow natural capitalization.

| Slug | Display Name |
|------|-------------|
| `evident` | Evident |
| `founder-hub` | Founder Hub |
| `doj-document-library` | DOJ Document Library |
| `civics-hierarchy` | Civics Hierarchy |
| `informed-consent-companion` | Informed Consent Companion |
| `essential-goods-ledger` | Essential Goods Ledger |
| `tillerstead` | Tillerstead |
| `tillerstead-toolkit` | Tillerstead Toolkit |
| `contractor-command-center` | Contractor Command Center |
| `sweat-equity-insurance` | Sweat Equity Insurance |
| `geneva-bible-study` | Geneva Bible Study |

### 3.3 What Not to Do

- Do not prefix satellites with "Evident-" unless they are Tier 1 companions
  and the context requires disambiguation (e.g., Docker image tags).
- Do not add version numbers to display names.
- Do not use internal codenames in user-facing contexts.
- Do not abbreviate names in the catalog. Abbreviations belong in CLI aliases
  and script variables, not product listings.

---

## 4. Packaging Tiers

Every satellite falls into one of four packaging states. The tier determines
what infrastructure and polish is expected before the app is shown publicly.

### Published

The app has a stable deployment, a working build pipeline, and a manifest file.
It can be linked from the catalog.

**Requirements:**

- `.evident-repo.json` at repo root with `releaseStatus: "stable"` or higher
- Working `npm run build` or equivalent
- Deployed to at least one host (GitHub Pages, Railway, Docker, App Store)
- README with purpose statement, setup instructions, and deploy target
- No broken dependencies or build errors on main branch

**Current qualifiers:** Tillerstead, Contractor Command Center, Geneva Bible
Study

### Listed

The app is functional and deployed but still under active development. It
appears in the catalog with a maturity badge.

**Requirements:**

- `.evident-repo.json` with `releaseStatus: "beta"` or `"alpha"`
- Builds successfully on main branch
- Deployed to at least one host
- README with purpose statement

**Current qualifiers:** Founder-Hub, DOJ Document Library, Civics Hierarchy,
Informed Consent Companion, Essential Goods Ledger, tillerstead-toolkit, BWC

### Draft

The app is in active development but not yet deployed or stable enough for
public listing. Visible in the web-builder registry for the owner, hidden from
external catalogs.

**Requirements:**

- `.evident-repo.json` with `releaseStatus: "draft"` or `"alpha"`
- Repository exists with meaningful code

**Current qualifiers:** Sweat Equity Insurance

### Archived

The app is no longer maintained. It remains in the registry for historical
reference but is hidden from active catalogs and grayed out in the web-builder.

**Requirements:**

- `.evident-repo.json` with `releaseStatus: "archived"`
- No active deployment

**Current qualifiers:** None

---

## 5. Catalog and Launcher Strategy

### 5.1 Where Satellites Appear

Satellites are listed in three places, each with different requirements:

| Surface | Audience | Shows |
|---------|----------|-------|
| **Web-builder registry** | Developer (you) | All tiers, all families |
| **Founder-Hub ToolHub** | Internal ops / future collaborators | Published + Listed Tier 1 companions only |
| **Evident marketing site** | Public visitors | Published Tier 1 companions only |

### 5.2 Catalog Card Format

Every satellite in the catalog renders as a card with these fields:

```
┌──────────────────────────────────────────┐
│  [Icon]  DOJ Document Library            │
│                                          │
│  Forensic document analysis and public   │
│  records research tool.                  │
│                                          │
│  Stack: React + FastAPI + Docker         │
│  Status: Beta                            │
│  Family: Evident                         │
│                                          │
│  [Open]  [GitHub]  [Docs]               │
└──────────────────────────────────────────┘
```

**Required fields:** Name, one-sentence description, stack, status badge,
family badge.

**Optional fields:** Live URL, GitHub URL, documentation link.

**Status badges:**

| Badge | Color | Meaning |
|-------|-------|---------|
| Production | Green | Stable, deployed, public |
| Stable | Blue | Reliable, may not be publicly promoted |
| Beta | Amber | Functional, under active development |
| Alpha | Gray | Early stage, expect breaking changes |
| Prototype | Outline | Concept only, not for use |
| Archived | Dimmed | No longer maintained |

**Family badges:**

| Badge | Color | Scope |
|-------|-------|-------|
| Evident | Primary brand color | Legal-tech platform family |
| Tillerstead | Trade/earthy accent | Contractor business family |
| Personal | Neutral | Independent projects |

### 5.3 Catalog Sort Order

1. Main suite always first (not a satellite card — it is the header)
2. Tier 1 companions, sorted by maturity (Production → Alpha)
3. Tier 2 ventures, sorted by maturity
4. Tier 3 independents, sorted by maturity
5. Archived at the bottom, collapsed by default

### 5.4 Grouping in the Launcher

If the Evident platform ever provides a "tool launcher" or "app drawer" for
users (not just the developer), only Tier 1 companions at Published or Listed
status appear. They are grouped by function, not by technology:

```
EVIDENCE & DISCOVERY
├─ DOJ Document Library
├─ BWC Evidence Workflow
└─ Essential Goods Ledger

LEGAL REFERENCE
├─ Civics Hierarchy
└─ Informed Consent Companion
```

Tier 2 and Tier 3 satellites never appear in the product launcher. They are
separate products.

---

## 6. Brand Relationship Rules

### Rule 1 — Main Suite Identity Is Protected

The name "Evident" without qualification refers exclusively to the BWC /
eDiscovery platform. No satellite may call itself "Evident" or use the Evident
logo as its primary mark.

### Rule 2 — Companions Acknowledge the Relationship

Tier 1 companions may use:

- "Part of the Evident Technologies ecosystem"
- "Built by Evident Technologies"
- "Compatible with Evident"
- The Evident wordmark in a secondary position (footer, about page)

They may not use:

- "Evident" as part of their product name (e.g., "Evident Civics" is wrong)
- The Evident logo as their app icon
- Language implying they are the main product

### Rule 3 — Ventures Use Their Own Brand

Tier 2 ventures use their own name, logo, and brand identity. The connection
to Evident Technologies appears only in:

- Legal footer: "A product of Evident Technologies LLC"
- Privacy policy / terms of service references
- Repository manifest (`family` and `owner` fields)

### Rule 4 — Independents Stand Alone

Tier 3 independents carry no Evident branding in any user-facing context. The
only link is the `.evident-repo.json` manifest, which is a developer-facing
file.

### Rule 5 — Shared Standards Are Invisible to Users

All satellites follow Evident governance standards (audit logging, accessibility,
security). This is an internal quality commitment, not a marketing claim.
Satellites do not advertise "Evident Certified" or "Evident Approved" unless a
formal certification program exists.

---

## 7. When a Satellite Should Stay Standalone

A satellite must remain a separate repo and never merge into the main suite if
any of these are true:

| Condition | Example |
|-----------|---------|
| It serves a different audience than BWC/eDiscovery users | Tillerstead (contractors), Geneva Bible Study (readers) |
| It has a different release cadence | Contractor Command Center ships weekly; main suite ships on demand |
| It uses a fundamentally different tech stack | Tillerstead is Jekyll; main suite is Python + FastAPI |
| It has different compliance requirements | Geneva Bible Study has no forensic audit obligations |
| It could be sold, transferred, or open-sourced independently | Essential Goods Ledger has standalone value |
| It would confuse the main product's purpose if bundled | Bundling a Bible reader into a forensic platform weakens both |

A satellite should be **considered for absorption** into the main suite only if:

- It shares the same database
- It shares the same auth system
- It cannot function without the main suite's API
- It would confuse users if it had a separate login

Currently, **no satellite qualifies for absorption**. BWC is the closest, but
it is intentionally isolated with its own database, auth, and S3 storage.

---

## 8. Manifest Schema Extension

The existing `.evident-repo.json` schema (Step 4) already captures most of what
the satellite packaging model needs. Two optional fields are recommended to
formalize the tier system:

```json
{
  "satelliteTier": {
    "type": "string",
    "enum": ["companion", "venture", "independent"],
    "description": "Relationship tier to the main Evident suite."
  },
  "catalogVisibility": {
    "type": "string",
    "enum": ["published", "listed", "draft", "archived"],
    "description": "Whether and how this repo appears in catalogs."
  }
}
```

These fields are added to the schema as optional properties. Existing manifests
continue to work without them. When present, the web-builder registry and
Founder-Hub ToolHub use them to filter and sort catalog entries.

---

## 9. Web-Builder Registry Presentation

The web-builder's Repos panel (Step 2) already groups by family and shows role
badges. To support the packaging model, the following enhancements are
recommended:

### 9.1 Tier Indicator

Add a small tier label below the role badge on each registry card:

```
┌──────────────────────────┐
│  DOJ Document Library    │
│  satellite-app · Beta    │
│  Tier 1 — Companion      │  ← New
│  Evident family           │
│  React + FastAPI + Docker │
└──────────────────────────┘
```

### 9.2 Filter by Tier

Add tier chips to the existing search/filter bar:

```
[All] [Companion] [Venture] [Independent] [Archived]
```

### 9.3 Grouping Toggle

Offer two grouping modes (toggle button):

- **By Family** (current default): Evident → Tillerstead → Personal
- **By Tier**: Companion → Venture → Independent

### 9.4 Visibility Badge

Cards for "Draft" repos show a muted style. Cards for "Archived" repos show
a strikethrough name and collapse to a single line.

### 9.5 Quick Actions per Tier

| Tier | Quick Actions |
|------|--------------|
| Companion | Open, GitHub, Deploy, Register in ToolHub |
| Venture | Open, GitHub, Deploy |
| Independent | Open, GitHub |
| Archived | GitHub (read-only) |

---

## 10. Migration Checklist

To move from the current state to the packaging model described above:

- [ ] Add `satelliteTier` and `catalogVisibility` to the manifest schema
- [ ] Update `.evident-repo.json` in Evident root (add `satelliteTier:
      "companion"` for BWC visibility)
- [ ] Create `.evident-repo.json` in each satellite repo that lacks one
- [ ] Populate `satelliteTier` and `catalogVisibility` in each manifest
- [ ] Update web-builder registry cards to show tier labels
- [ ] Add tier filter chips to the registry search bar
- [ ] Update Founder-Hub ToolHub to respect `catalogVisibility` field
- [ ] Rename "DOJ Document Library Tool" → "DOJ Document Library" in all
      manifests and registry entries
- [ ] Verify all Tier 1 companions have working builds on main branch
- [ ] Verify all Published satellites have README with setup instructions

---

## 11. Decision Record

| Decision | Rationale |
|----------|-----------|
| Three relationship tiers (companion, venture, independent) | Matches real business structure without over-engineering |
| Four packaging states (published, listed, draft, archived) | Maps directly to release maturity and catalog visibility |
| No satellite uses "Evident" in its product name | Protects main suite identity from dilution |
| Ventures carry their own brand | Different audience, different domain, different trust expectations |
| Only Tier 1 companions appear in the product launcher | Users should not see unrelated apps inside a forensic platform |
| Sort by maturity within tier | Puts the most usable apps first |
| Manifest schema extended, not replaced | Backward compatible with Step 4 manifests |
| No satellite qualifies for absorption today | All have independent DB, auth, and deploy targets |

---

## References

- [ECOSYSTEM-ARCHITECTURE-MAP.md](ECOSYSTEM-ARCHITECTURE-MAP.md) — Step 1
- [MAIN-SUITE-PACKAGING-PLAN.md](MAIN-SUITE-PACKAGING-PLAN.md) — Step 5
- `tools/web-builder/workspace-registry.json` — Current registry data
- `tools/web-builder/evident-repo-manifest.schema.json` — Manifest schema
