# Repo Role Taxonomy

> Canonical reference for classifying repositories in the Evident ecosystem.
>
> Each repo receives exactly one role. The role determines packaging behavior,
> branding permissions, CI requirements, and web-builder treatment.

---

## Roles

### `platform-core`

The primary product. Contains the main codebase, API, database models, and
deployment configuration. There is exactly one `platform-core` per ecosystem.

- **Branding:** Uses the main brand (Evident).
- **Packaging:** Ships as the suite. Semver versioned.
- **CI:** Full pipeline (lint, test, build, deploy, security scan).
- **Builder:** Full export support. Strict preflight.
- **Badge color:** Blue `#58a6ff`

**Current assignment:** Evident

---

### `ops-hub`

Founder and operator console. Admin dashboard, governance framework, CRM, site
management, billing. Tightly coupled to the ecosystem's operations but deploys
to its own domain.

- **Branding:** Uses ecosystem branding (operator-facing, not public-facing).
- **Packaging:** Standalone deploy. Semver versioned.
- **CI:** Full pipeline.
- **Builder:** Limited export (prompt tier for React stacks).
- **Badge color:** Purple `#bc8cff`

**Current assignment:** Founder-Hub

---

### `product-satellite`

A user-facing application that extends the ecosystem. Ships independently. May
share branding with the main suite if it belongs to the same family.

- **Branding:** Optional. Follows the `family` field in the manifest.
- **Packaging:** Independent deploy. Semver versioned.
- **CI:** Basic pipeline minimum (build + deploy).
- **Builder:** Varies by stack tier (native, aware, or prompt).
- **Badge color:** Green `#3fb950`

**Current assignments:** Civics Hierarchy, DOJ Document Library, Essential
Goods Ledger, Informed Consent Companion, Contractor Command Center

---

### `support-tool`

Internal tooling — calculators, APIs, admin scripts, developer utilities. Not
user-facing. Supports products but is not itself a product.

- **Branding:** None. Internal use only.
- **Packaging:** Optional release. May be a backend service.
- **CI:** Optional.
- **Builder:** Metadata only. Builder cannot generate files for this stack.
- **Badge color:** Gray `#8b949e`

**Current assignment:** tillerstead-toolkit

---

### `business-site`

A marketing or authority website for a distinct business entity. Has its own
domain, brand, and audience. Not part of the main product suite.

- **Branding:** Own brand. Does not share the main suite brand.
- **Packaging:** Date-based releases or continuous deployment.
- **CI:** Basic pipeline (build + deploy + Lighthouse).
- **Builder:** Native or aware export depending on stack.
- **Badge color:** Teal `#3fb9a7`

**Current assignment:** Tillerstead

---

### `independent-venture`

A standalone product with its own brand and audience. Not part of the main
suite ecosystem. May share infrastructure patterns (manifests, tokens, CI
templates) but not branding or deployment.

- **Branding:** Own brand. Fully independent.
- **Packaging:** Semver versioned. Own release cycle.
- **CI:** Optional to full, at the venture's discretion.
- **Builder:** Varies by stack tier.
- **Badge color:** Amber `#d29922`

**Current assignment:** Geneva Bible Study

---

### `experiment`

A prototype, concept demo, or feasibility study. Not production-ready. Not
deployed to any public URL. May graduate to another role when it matures.

- **Branding:** None.
- **Packaging:** Not released. Demo data only.
- **CI:** None required.
- **Builder:** Optional export. Minimal preflight.
- **Badge color:** Red `#f85149` (dashed border)

**Current assignment:** Sweat Equity Insurance

---

## Role Assignment Rules

1. Every repo gets exactly one role.
2. The role is recorded in the `role` field of `.evident-repo.json`.
3. The role is also reflected in `workspace-registry.json`.
4. Role changes require updating both the manifest and the registry.
5. Role does not imply ownership. Ownership is recorded in the `owner` field.
6. Role does not imply family. Family is recorded in the `family` field.
   A `product-satellite` can belong to the Evident family or the Tillerstead
   family.

## Role Graduation Path

```
experiment → product-satellite → (maturity) → independent-venture
experiment → support-tool
product-satellite → platform-core (only if replacing the current core)
```

Experiments can graduate to satellites or tools. Satellites remain satellites
unless they outgrow the ecosystem and become independent ventures. There is
only ever one `platform-core`.

---

## Badge CSS

```css
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 1px 6px;
  border-radius: 4px;
  line-height: 1.6;
}
.role-badge[data-role="platform-core"]       { background: #1f6feb20; color: #58a6ff; }
.role-badge[data-role="ops-hub"]             { background: #8957e520; color: #bc8cff; }
.role-badge[data-role="product-satellite"]   { background: #3fb95020; color: #3fb950; }
.role-badge[data-role="support-tool"]        { background: #8b949e15; color: #8b949e; }
.role-badge[data-role="business-site"]       { background: #3fb9a720; color: #3fb9a7; }
.role-badge[data-role="independent-venture"] { background: #d2992220; color: #d29922; }
.role-badge[data-role="experiment"]          { background: #f8514920; color: #f85149; border-style: dashed; }
```
