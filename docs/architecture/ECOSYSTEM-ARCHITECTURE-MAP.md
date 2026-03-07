# Evident Technologies — Ecosystem Architecture Map

**Document:** Step 1 of 12 — Ecosystem Architecture Map  
**Date:** 2026-03-06  
**Status:** Baseline  
**Scope:** All repositories under Devon Tyler / Evident Technologies

---

## 1. Recommended Ecosystem Map

```
EVIDENT TECHNOLOGIES ECOSYSTEM
══════════════════════════════════════════════════════════════════════

 ┌─────────────────────────────────────────────────────────────────┐
 │                     MAIN SUITE (Product)                       │
 │                                                                │
 │   Evident — BWC / eDiscovery Platform                          │
 │   ├─ Backend API (FastAPI + Flask legacy)                      │
 │   ├─ BWC Subsystem (FastAPI + Next.js, isolated)               │
 │   ├─ Evidence Processing Pipeline (Celery + ML)                │
 │   ├─ Chain-of-Custody & Integrity Services                     │
 │   ├─ Case Management & Legal Discovery                         │
 │   ├─ Admin Dashboard (Node.js)                                 │
 │   ├─ .NET MAUI (Mobile/Desktop clients)                        │
 │   └─ Marketing Site (11ty static)                              │
 │                                                                │
 └─────────────────────────────────────────────────────────────────┘
          │
          │  shares governance standards, manifest schema,
          │  brand contracts, audit patterns
          │
 ┌────────┴────────────────────────────────────────────────────────┐
 │                  OPERATIONS HUB (Founder-Hub)                   │
 │                                                                 │
 │   Founder-Hub — Portfolio, Operations & Tool Registry           │
 │   ├─ ToolHub (manifest registry for all satellite apps)         │
 │   ├─ Ops Layer (billing, tenancy, backup, audit)                │
 │   ├─ Governance Framework (policies, risk register, controls)   │
 │   ├─ Contract Templates (legal policies)                        │
 │   └─ Admin Console (RBAC, CRM, lead capture)                   │
 │                                                                 │
 └────────┬────────────────────────────────────────────────────────┘
          │
          │  manifest registration, brand alignment
          │
 ┌────────┴────────────────────────────────────────────────────────┐
 │                     SATELLITE APPS                              │
 │                                                                 │
 │   LEGAL / CIVIC                                                 │
 │   ├─ DOJ Document Library Tool (forensic document analysis)     │
 │   ├─ Civics Hierarchy (government jurisdiction reference)       │
 │   └─ Informed Consent Companion (consent decision support)      │
 │                                                                 │
 │   TRADE / COMMERCE                                              │
 │   ├─ Tillerstead (contractor marketing site)                    │
 │   ├─ tillerstead-toolkit (contractor calculators + API)         │
 │   ├─ Contractor Command Center (estimation PWA)                 │
 │   ├─ Essential Goods Ledger (economic data tracker)             │
 │   └─ Sweat Equity Insurance (insurance model prototype)         │
 │                                                                 │
 │   PERSONAL / EDUCATIONAL                                        │
 │   └─ Geneva Bible Study (offline Bible reader PWA)              │
 │                                                                 │
 └─────────────────────────────────────────────────────────────────┘
```

---

## 2. Main Suite Definition

**Repository:** `DTMBX/Evident`  
**Role:** Primary product. The BWC / eDiscovery platform.  
**What lives here and only here:**

| Layer | Contents | Tech |
|-------|----------|------|
| **Backend API** | FastAPI routes, Flask legacy routes, auth, models, 44 service files | Python 3.12, SQLAlchemy 2, PostgreSQL, Redis |
| **BWC Subsystem** | Body-worn camera forensic processing (isolated backend + frontend) | FastAPI + Next.js 14, MinIO WORM storage |
| **Evidence Pipeline** | Ingestion, hashing, OCR, transcription, privilege detection | Celery, Whisper, PyTorch, Tesseract, FFmpeg |
| **Chain of Custody** | Integrity ledger, SHA-256 hashing, HMAC manifests, audit logs | Python services, append-only design |
| **Case Management** | Matters, parties, legal holds, review workflows, FRCP export | SQLAlchemy ORM, 18 model files |
| **Admin** | User management, system health, auth console | Node.js + Express |
| **MAUI Clients** | Cross-platform mobile/desktop apps | .NET 8, C#, XAML |
| **Marketing Site** | Public-facing pages (static, pre-built) | 11ty + Nunjucks + Tailwind |
| **CLI** | Command-line pipeline interface | Python (`cli/evident.py`) |
| **Infrastructure** | Docker, Kubernetes, Terraform, deployment scripts | YAML, HCL, PowerShell |

**What does NOT belong in this repo (currently mixed in):**

| Item | Current Location | Recommended Home |
|------|-----------------|-----------------|
| `apps/civics-hierarchy/` | Evident/apps/ | Separate satellite repo (already exists) |
| `apps/epstein-library-evid/` | Evident/apps/ | Separate satellite repo (already exists) |
| `apps/essential-goods-ledg/` | Evident/apps/ | Separate satellite repo (already exists) |
| `apps/geneva-bible-study-t/` | Evident/apps/ | Separate satellite repo (already exists) |
| `ventures/` | Evident/ventures/ | Not in main suite at all |
| `tillerstead-toolkit/` | Evident/tillerstead-toolkit/ | Separate satellite repo (already exists) |
| Marketing HTML pages for Tillerstead | Evident root (*.html references) | Tillerstead repo |
| `tools/web-builder/` | Evident/tools/ | Stays — internal developer tool |

---

## 3. Satellite App Categories

### Category A — Legal / Civic Satellites

These apps connect thematically to Evident's legal-tech mission. They may consume shared manifest schemas or governance patterns, but they run independently and deploy independently.

| App | Repo | Stack | Backend | Deploy | Relation to Main Suite |
|-----|------|-------|---------|--------|----------------------|
| **DOJ Document Library Tool** | `ventures/DOJ Document Library Tool` | React + TS + Vite + Docker | FastAPI + PostgreSQL + Qdrant | Docker / Railway | Strongest satellite. Forensic evidence patterns originated here. Could register as Evident module via manifest. |
| **Civics Hierarchy** | `ventures/Civics Hierarchy` | React + TS + Vite | None (frontend-only) | GitHub Pages | Reference tool. Registered in Founder-Hub ToolHub. |
| **Informed Consent Companion** | `ventures/Informed Consent Companion` | React + TS + Vite | None (frontend-only) | GitHub Pages | Light satellite. Consent/accountability adjacent. |

### Category B — Trade / Commerce Satellites

These apps serve a construction/contracting business vertical. They are operationally independent from the legal-tech product but share an owner and governance standards.

| App | Repo | Stack | Backend | Deploy | Relation to Main Suite |
|-----|------|-------|---------|--------|----------------------|
| **Tillerstead** | `ventures/Tillerstead` | Jekyll + HTML/CSS/JS | None (static site) | GitHub Pages | Independent marketing site. Separate CNAME, separate brand. |
| **tillerstead-toolkit** | `ventures/tillerstead-toolkit` | Next.js 14 + FastAPI | FastAPI + PostgreSQL + Redis | Railway (backend) + Pages (frontend) | Independent product. Share governance conventions only. |
| **Contractor Command Center** | `ventures/Contractor Command Center` | React + TS + PWA | None (offline PWA) | GitHub Pages | Independent PWA. May coordinate with tillerstead-toolkit. |
| **Essential Goods Ledger** | `ventures/Essential Goods Ledger` | React + TS + Vite + D3 | 8 data source connectors (read-only) | GitHub Pages | Independent data tool. No backend. |
| **Sweat Equity Insurance** | `ventures/Sweat Equity Insurance` | Vanilla HTML/JS | None (prototype) | Static / demo only | Prototype. Not production-ready. |

### Category C — Personal / Educational Satellites

| App | Repo | Stack | Backend | Deploy |
|-----|------|-------|---------|--------|
| **Geneva Bible Study** | `ventures/Geneve Bible Study` | React + TS + PWA | None (offline PWA) | GitHub Pages + platform stores |

---

## 4. Repo Relationship Model

```
                    ┌──────────────┐
                    │   Evident    │  Main Suite
                    │  (BWC/eDisc) │  Product repo
                    └──────┬───────┘
                           │
              governance standards, manifest schema
                           │
                    ┌──────┴───────┐
                    │  Founder-Hub │  Operations Hub
                    │  (ToolHub +  │  Registry + governance
                    │   Ops + Gov) │  framework
                    └──────┬───────┘
                           │
              manifest registration (read-only contract)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴──────┐
    │  Legal /   │   │  Trade /  │   │ Personal / │
    │  Civic     │   │  Commerce │   │ Education  │
    │  Sats      │   │  Sats     │   │ Sats       │
    └───────────┘   └───────────┘   └────────────┘

    Relationship types:
    ═══  owns/contains (code dependency)
    ───  shares standards (convention dependency)
    · · ·  optional registration (manifest only)
```

**Dependency rules:**

| From | To | Type | Notes |
|------|----|------|-------|
| Evident | Founder-Hub | Convention | Shares governance templates, manifest schema |
| Founder-Hub | Satellites | Registry | ToolHub registers satellites via manifest JSON |
| Satellites | Evident | None | Satellites do NOT import Evident code |
| Satellites | Founder-Hub | Manifest | Satellites publish a manifest file; Founder-Hub indexes it |
| Satellites | Each other | None | No satellite depends on another satellite |

**Hard rule:** No runtime code flows between repos. Shared alignment is through conventions, manifests, and governance documents — not imports or shared modules.

---

## 5. What Should Stay Separate

### Separate repos (do not merge)

| Repo | Reason |
|------|--------|
| **Evident** | Main product. Has its own backend, CI/CD, deployment, data stores. Merging anything into it adds risk to the forensic platform. |
| **Founder-Hub** | Operations and governance hub. Different tech stack (React SPA vs. Python backend). Different deploy target. Different audience (operator vs. end-user). |
| **Tillerstead** | Entirely different brand, domain, CNAME. Jekyll site. Has no logical reason to be inside a legal-tech repo. |
| **tillerstead-toolkit** | Own backend (FastAPI), own deploy (Railway). Shares nothing with Evident except governance patterns. |
| **DOJ Document Library Tool** | Full-stack Docker app. Own database, own vector store. If it grows, it becomes its own product. |
| **Contractor Command Center** | Offline PWA. Separate install, separate update cycle. |
| **Geneva Bible Study** | Unrelated domain. Offline PWA targeting app stores. |
| **Civics Hierarchy** | Lightweight reference tool. No backend. |
| **Essential Goods Ledger** | Data visualization tool with external API connectors. No shared runtime. |
| **Informed Consent Companion** | Lightweight tool. Own deploy. |
| **Sweat Equity Insurance** | Prototype only. May or may not proceed. |

### Items to extract from Evident (currently embedded)

| Item | Current Path | Action |
|------|-------------|--------|
| `apps/civics-hierarchy/` | Evident repo | Remove. Already exists as separate repo. Keep only manifest reference. |
| `apps/epstein-library-evid/` | Evident repo | Remove. Already exists as separate repo. Keep only manifest reference. |
| `apps/essential-goods-ledg/` | Evident repo | Remove. Already exists as separate repo. Keep only manifest reference. |
| `apps/geneva-bible-study-t/` | Evident repo | Remove. Already exists as separate repo. Keep only manifest reference. |
| `tillerstead-toolkit/` | Evident repo | Remove. Already exists as separate repo at `ventures/tillerstead-toolkit`. |
| `ventures/` | Evident repo | Remove entirely from main suite. Investor/venture materials belong in Founder-Hub or a standalone docs repo. |

After extraction, Evident's `apps/` folder should contain **only BWC subsystem components** or be eliminated in favor of `bwc/` as the sole internal app directory.

---

## 6. What Can Share Standards Without Sharing Code

These items are **convention-level alignment** — shared by agreement and documentation, not by `import` or `require`.

### 6a. Governance Standards (shared across all repos)

| Standard | Description | Enforcement |
|----------|-------------|-------------|
| Append-only audit logging | Every write operation produces an immutable log entry | Each repo implements its own logger following the same schema |
| SHA-256 integrity hashing | All evidence, exports, and manifests are hash-verified | Each repo uses its own hashing utility |
| RBAC patterns | Role-based access follows the same tier model | Each repo enforces locally |
| Non-accusatory language | No output infers guilt, liability, or conclusions | Copilot instructions + review |
| Deterministic processing | All transforms are reproducible from inputs | Architecture rule per repo |

### 6b. Manifest Schema (shared registry contract)

| Artifact | Lives In | Consumed By |
|----------|----------|-------------|
| `ToolManifest` TypeScript schema | Founder-Hub `apps/tooling/ToolManifest.ts` | All satellites that register with ToolHub |
| `tool-manifest.schema.json` | Founder-Hub `apps/tooling/` | CI validation in satellite repos |
| Manifest JSON files | Each satellite repo (one file per tool) | Founder-Hub ToolHub registry |

### 6c. Brand and UI Conventions (shared design tokens)

| Convention | Description | How Shared |
|------------|-------------|------------|
| Color palette | Evident brand palette: navy, slate, gold accents | Design token JSON or CSS custom properties file, copied (not linked) |
| Typography | System font stack, heading scale | Documented in brand guidelines |
| Tone | Calm, professional, observational | `copilot-instructions.md` per repo |
| Component patterns | Radix UI primitives + Tailwind utility classes | Convention doc, not a shared npm package |

### 6d. CI/CD Patterns (shared workflow templates)

| Pattern | Description | How Shared |
|---------|-------------|------------|
| Lint + format on PR | ESLint, Prettier, Stylelint | GitHub Actions workflow template per repo |
| Secret scanning | Pre-commit secret scan | Shared script pattern (copy, not link) |
| Accessibility checks | Pa11y / axe-core on build | Shared config template |
| Dependency audit | `npm audit` / `pip audit` in CI | Standard workflow step |

---

## 7. Suggested Naming and Labeling Conventions

### 7a. Repo Naming

| Pattern | Example | Use |
|---------|---------|-----|
| `evident` | `DTMBX/Evident` | Main product suite — one repo |
| `evident-hub` | `DTMBX/Founder-Hub` (rename candidate) | Operations hub — one repo |
| `evident-sat-{name}` | `evident-sat-doj-library` | Legal/civic satellite |
| `tillerstead` | `DTMBX/tillerstead` | Trade brand — marketing site |
| `tillerstead-{tool}` | `tillerstead-toolkit` | Trade brand — product tools |
| `{name}` | `geneva-bible-study` | Personal/educational — no prefix needed |

### 7b. Internal Labels (for ToolHub manifest registration)

| Label | Meaning | Examples |
|-------|---------|---------|
| `core` | Part of the main BWC/eDiscovery suite | BWC backend, evidence pipeline, case management |
| `ops` | Operational infrastructure and governance | ToolHub, billing engine, audit framework |
| `satellite:legal` | Legal-tech adjacent satellite | DOJ Library, Civics Hierarchy |
| `satellite:trade` | Commerce/contractor satellite | Contractor Command Center, tillerstead-toolkit |
| `satellite:personal` | Personal or educational satellite | Geneva Bible Study |
| `tool:internal` | Developer/build tool not shipped to users | Web Builder, CLI, deployment scripts |
| `tool:public` | User-facing tool or calculator | Pricing calculator, material estimator |
| `prototype` | Not production-ready, experimental | Sweat Equity Insurance |

### 7c. Branch Naming

| Pattern | Use |
|---------|-----|
| `main` | Production branch (all repos) |
| `dev` | Integration branch (main suite + hub only) |
| `feat/{ticket}-{slug}` | Feature work |
| `fix/{ticket}-{slug}` | Bug fixes |
| `release/{version}` | Release candidates |

### 7d. Manifest File Naming

Each satellite publishes one manifest file:

```
{repo-root}/manifest.json
```

Schema: `ToolManifest` from Founder-Hub  
Fields: `id`, `name`, `version`, `category`, `status`, `brand`, `entryPoint`, `capabilities`, `tags`

---

## Summary Table

| # | Repo | Role | Category | Separate Repo | Shares Standards | Shares Code |
|---|------|------|----------|--------------|-----------------|-------------|
| 1 | Evident | Main Suite | core | Yes (primary) | Source of truth | No outbound |
| 2 | Founder-Hub | Operations Hub | ops | Yes | Consumes + extends | No outbound |
| 3 | DOJ Document Library | Satellite | satellite:legal | Yes | Governance + manifest | No |
| 4 | Civics Hierarchy | Satellite | satellite:legal | Yes | Governance + manifest | No |
| 5 | Informed Consent | Satellite | satellite:legal | Yes | Governance + manifest | No |
| 6 | Tillerstead | Satellite | satellite:trade | Yes | Governance only | No |
| 7 | tillerstead-toolkit | Satellite | satellite:trade | Yes | Governance only | No |
| 8 | Contractor Command Center | Satellite | satellite:trade | Yes | Governance only | No |
| 9 | Essential Goods Ledger | Satellite | satellite:trade | Yes | Governance + manifest | No |
| 10 | Sweat Equity Insurance | Satellite | prototype | Yes | Minimal | No |
| 11 | Geneva Bible Study | Satellite | satellite:personal | Yes | Governance only | No |

---

## Next Steps (Remaining Planners)

This document is Step 1 of 12. The following planners build on this map:

| Step | Planner | Depends On |
|------|---------|-----------|
| 2 | Workspace Registry Designer | This map |
| 3 | Repo Role Classifier | This map |
| 4 | Shared Contract and Manifest Planner | Steps 2–3 |
| 5 | BWC / eDiscovery Main Suite Packaging Planner | Steps 1–4 |
| 6 | Satellite Packaging Planner | Steps 1–4 |
| 7 | Multi-Repo Export and Targeting Planner | Steps 5–6 |
| 8 | Cross-Repo UI and Brand Consistency Planner | Steps 4, 6 |
| 9 | Build and Release Workflow Planner | Steps 5–7 |
| 10 | Safe Merge and Consolidation Planner | Steps 1–6 |
| 11 | Language and Stack Boundary Planner | Steps 1, 5 |
| 12 | Beginner Operator Workflow Planner | All steps |

---

*This document should be reviewed before any repo restructuring, merge, or deployment target change.*
