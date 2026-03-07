# Business Boundary Rules

**Document:** Dual-LLC Separation Policy  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident Technologies LLC + Tillerstead LLC

---

## Purpose

This document defines the non-negotiable separation rules between
Evident Technologies LLC and Tillerstead LLC. All contributors, automated
tools, and AI assistants must respect these boundaries.

---

## Legal Entities

| Entity | Registration | Primary Domain | Product Focus |
|--------|-------------|----------------|---------------|
| **Evident Technologies LLC** | — | evident.icu / evidenttechnologies.com | BWC / eDiscovery, forensic evidence processing |
| **Tillerstead LLC** | NJ HIC #13VH10808800 | tillerstead.com | TCNA-compliant tile & stone installation, South Jersey |
| **Tillerstead Ventures LLC** | — | — | Experimental ventures (Sweat Equity Insurance) |

Each entity has its own:
- legal identity
- product scope
- domain
- deployment surface
- repository boundary
- branding

---

## Separation Rules

### 1. No Shared Repos

Each LLC's products ship from separate repositories. Evident products never live
in a Tillerstead repo. Tillerstead products never live in the Evident monorepo.

**Exception:** The `apps/` workspace in the Evident monorepo may contain
workspace-linked copies of satellite apps for build/test coordination. These
are npm workspace members, not the canonical source for Tillerstead products.

### 2. No Shared Domains

Evident domains (`evident.icu`, `evidenttechnologies.com`) must never serve
Tillerstead content. Tillerstead domains (`tillerstead.com`) must never serve
Evident content.

### 3. No Shared Branding

- Evident logo, name, and trade dress must not appear on Tillerstead surfaces.
- Tillerstead logo, name, trade dress, and NJ HIC license references must not
  appear on Evident surfaces.
- "Devon Tyler" may appear as the owner on both, but the product brands stay
  separate.

### 4. No Shared Hosting Accounts

Each LLC uses its own hosting account, deployment pipeline, and CI/CD
configuration. A shared GitHub organization (`DTMBX`) is acceptable for code
storage, but deployment targets must be isolated.

### 5. No Shared CORS Origins

Backend APIs must not list both businesses' domains in their CORS
`allowed_origins` configuration. Each API serves its own business.

### 6. No Shared Legal Documents

Licenses, terms of service, privacy policies, and disclaimers are per-LLC.
An `MIT` license on a personal project (e.g., Geneva Bible Study) does not
extend to Evident or Tillerstead products.

### 7. No Co-Branded Marketing

Marketing content, investor materials, and public-facing copy must reference
only the LLC that owns the product. The two businesses must never appear as a
combined venture.

---

## What May Be Shared

| Shared Item | Mechanism | Constraint |
|-------------|-----------|-----------|
| Manifest schema (`.evident-repo.json`) | Convention — each repo uses independently | No runtime coupling |
| Design token CSS variables | Optional CSS import | No JS dependency |
| Copilot instruction patterns | Each business adapts independently | Not a shared file |
| Workspace registry format | Read-only catalog in internal tooling | Not published externally |
| Build tooling patterns | Convention only (linting, formatting) | Not shared node_modules |

---

## Toolkit Embedding

Tillerstead Toolkit may be embedded on `tillerstead.com` using the protocol
defined in [EMBED-CONTRACT.md](EMBED-CONTRACT.md). The toolkit:

- Runs as an isolated iframe or linked standalone app.
- Uses only Tillerstead LLC branding inside the embed.
- Does not access parent page DOM.
- Does not depend on Evident infrastructure.

See [EMBED-CONTRACT.md](EMBED-CONTRACT.md) for the full integration specification.

---

## Enforcement

1. All pull requests touching deployment configs, CNAME files, CORS settings,
   or branding assets must be reviewed for boundary compliance.
2. AI-assisted code generation must flag any change that could blur LLC
   boundaries.
3. The workspace registry (`workspace-registry.json`) must include a `business`
   field for every entry.
4. Automated checks should verify that no Evident workflow deploys to
   Tillerstead domains and vice versa.

---

## Founder-Hub Clarification

**Founder-Hub** (devon-tyler.com) is classified as the operations hub for
Evident Technologies LLC. It operates under the `Evident` family and brand.

- Its ToolHub catalog may list Tillerstead products for internal reference only.
- It must not present Tillerstead products as Evident products.
- Any public-facing catalog must indicate the correct business owner for each
  listed app.
