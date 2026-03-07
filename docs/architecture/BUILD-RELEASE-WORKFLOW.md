# Build & Release Workflow

> Step 9 of the Evident Ecosystem Architecture Series
>
> Principle: **Every change is local until you decide it's public. Every
> release is a deliberate act, not an accident.**

---

## 1. Workflow Stages

Every change in the ecosystem moves through the same five stages, regardless
of repo or stack. The stages are sequential — a change cannot skip a stage.

```text
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│  LOCAL   │───▶│ PREVIEW │───▶│  REVIEW  │───▶│ RELEASE │───▶│  DEPLOY  │
│  (dev)   │    │ (branch)│    │  (PR)    │    │ (tag)   │    │  (live)  │
└─────────┘    └─────────┘    └──────────┘    └─────────┘    └──────────┘
```

| Stage | What Happens | Who Acts | Artifact |
| --- | --- | --- | --- |
| **Local** | Edit code, run dev server, check output | Developer | Working tree |
| **Preview** | Push branch, CI builds, preview URL generated | Developer + CI | Build artifact |
| **Review** | Open PR, pass gates, inspect preview | Developer + reviewer | Approved PR |
| **Release** | Merge to main, tag version, generate changelog | Developer | Git tag + notes |
| **Deploy** | CI deploys to production target | CI (automated) | Live site/service |

Not every change goes through all five stages. Bug fixes to a personal
satellite may go straight from Local → Release → Deploy. The stages exist to
be available, not to be mandatory for every commit.

---

## 2. Stage Definitions

### 2.1 Local (Development)

The developer works on their machine. No external side effects.

**Activities:**
- Edit source files
- Run the local dev server (`npm run dev`, `bundle exec jekyll serve`, etc.)
- Export from the web-builder to a local repo folder
- Run linters and formatters locally
- Run tests locally

**Exit criteria:**
- Code compiles / builds without errors
- Linter passes (or warnings understood)
- Change works as expected in local preview

**Commands by stack:**

| Stack | Dev Server | Lint | Build |
| --- | --- | --- | --- |
| Evident (11ty) | `npm run dev` | `npm run lint:js && npm run lint:css` | `npm run build` |
| Evident (Python) | `uvicorn` / `flask run` | `ruff check .` | N/A (interpreted) |
| Founder-Hub (Vite) | `npm run dev` | `npm run lint` | `npm run build` |
| Tillerstead (Jekyll) | `npm run dev` | `npm run lint` | `npm run build` |
| React satellites (Vite) | `npm run dev` | `npm run lint` | `npm run build` |
| tillerstead-toolkit (FastAPI) | `uvicorn app.main:app --reload` | `ruff check .` | N/A (interpreted) |

### 2.2 Preview (Branch)

The developer pushes a branch. CI builds and optionally generates a preview.

**Activities:**
- Push feature branch to GitHub
- CI runs lint + build + test (automated)
- Preview URL available (GitHub Pages preview, Netlify deploy preview, or
  `npm run preview` locally)
- Share preview URL with reviewer if needed

**Exit criteria:**
- CI passes (green check)
- Preview is visually correct
- No security scan failures

**Preview availability by repo:**

| Repo | Preview Method |
| --- | --- |
| Evident (site) | Netlify deploy preview (automatic on PR) |
| Founder-Hub | Vite preview (`npm run preview`) or staging environment |
| Tillerstead | Netlify deploy preview (automatic on PR) |
| React satellites | `npm run preview` locally, or deploy to staging branch |
| Python backends | Local only (no cloud preview for API changes) |

### 2.3 Review (Pull Request)

A PR is opened against the default branch. Review gates are checked.

**Activities:**
- Open PR with descriptive title and body
- CI gate checks run automatically
- Reviewer inspects diff, preview, and test results
- Reviewer approves or requests changes

**Exit criteria:**
- All CI checks pass
- At least one approval (for main suite and companions)
- No unresolved review comments
- PR description explains what changed and why

**Review requirements by tier:**

| Tier | PR Required | Approval Required | CI Gate |
| --- | --- | --- | --- |
| Main suite (Evident) | Yes | Yes (1 reviewer) | Lint + Build + Test Tier 1 |
| Ops hub (Founder-Hub) | Yes | Yes (1 reviewer) | Lint + Build + Test |
| Companion satellites | Yes | Recommended | Lint + Build |
| Venture satellites | Recommended | Optional | Build |
| Independent / Personal | Optional | Optional | Build (if CI exists) |

For a solo operator: "approval" means you pushed the branch, waited for CI,
reviewed the diff yourself in the PR view, and consciously merged. The PR
still serves as an audit record.

### 2.4 Release (Tag)

After merge, a version is tagged and release notes are created.

**Activities:**
- Merge PR to main
- Determine version bump (patch, minor, major)
- Create annotated git tag
- Write release notes (what changed, what's new)

**Exit criteria:**
- Tag exists on the merge commit
- Release notes published on GitHub
- `packagingStatus` and `releaseStatus` in `.evident-repo.json` are accurate

**When to tag:**

Not every merge needs a tag. Tag when:

- A user-visible feature is complete
- A bug fix affects production
- A dependency update changes behavior
- A milestone or sprint boundary is reached

Accumulate small commits and tag in batches. A release every 1–4 weeks is
reasonable for most repos.

### 2.5 Deploy (Production)

CI or a manual action pushes the release to the production target.

**Activities:**
- CI deploys automatically on tag or merge (varies by repo)
- Smoke test the live deployment
- Update status page or monitoring if applicable

**Exit criteria:**
- Live URL loads correctly
- No errors in deployment logs
- Health check passes (for API deployments)

**Deployment triggers by repo:**

| Repo | Trigger | Target | Method |
| --- | --- | --- | --- |
| Evident (site) | Push to main | GitHub Pages + Netlify | Automatic (CI) |
| Evident (backend) | Manual or tag | Render | Manual deploy or auto-deploy on main |
| Founder-Hub | Push to main | GitHub Pages | Automatic (CI) |
| Tillerstead | Push to main | GitHub Pages + Netlify | Automatic (CI) |
| tillerstead-toolkit | Push to main | Railway | Automatic (nixpacks) |
| React satellites | Push to main | GitHub Pages | Automatic (CI, where configured) |
| DOJ Library (local engine) | Manual | Docker Compose | Manual `docker compose up` |

---

## 3. Main Suite Workflow

The Evident main suite has the strictest workflow because it handles forensic
evidence. Mistakes affect evidentiary integrity.

### 3.1 Development Flow

```text
main ─────────────────────────────────────────────────▶
  │                                                     │
  └── feat/describe-the-change ──── PR ──── merge ──────┘
  └── fix/describe-the-fix ──────── PR ──── merge ──────┘
  └── chore/describe-the-task ───── PR ──── merge ──────┘
```

**Rules:**
- Never push directly to main
- Every change goes through a PR
- CI must pass before merge
- Squash merge preferred (clean history)

### 3.2 CI Gate (Required)

Every PR triggers these checks:

| Check | Tool | Blocks Merge |
| --- | --- | --- |
| JavaScript lint | ESLint | Yes |
| CSS lint | Stylelint | Yes |
| Python lint | Ruff | Yes |
| TypeScript check | `tsc --noEmit` | Yes |
| Site build | `npm run build` | Yes |
| Test Tier 1 | Playwright (Chromium) | Yes |
| Security scan | CodeQL | Yes (on main) |

**Test Tier 2** (extended Playwright, Python pytest) runs after Tier 1 but
does not block merge. Failures are logged for investigation.

### 3.3 Release Process

```text
1. All PRs for this release are merged to main
2. Run:  git tag -a v0.8.1 -m "Release 0.8.1: [summary]"
3. Run:  git push origin v0.8.1
4. GitHub Release is created (manually or via release.yml workflow)
5. CI deploys:
   - Site → GitHub Pages + Netlify
   - Backend → Render (if backend changes in the tag diff)
   - MAUI → MSIX package (triggered by v* tag)
```

### 3.4 Version Authority

The main suite uses a single `VERSION` file at the repo root as the source
of truth. All other version references (`package.json`, API response headers,
about pages) read from it or are synchronized during the build.

**Format:** Semantic versioning — `MAJOR.MINOR.PATCH`

| Version Component | Increment When |
| --- | --- |
| MAJOR | Breaking API changes, data model changes, evidence schema changes |
| MINOR | New features, new forensic tools, new UI sections |
| PATCH | Bug fixes, dependency updates, documentation corrections |

**Current drift to resolve:** `VERSION` = 0.7.0, `package.json` = 0.8.0.
Consolidate to the higher value (0.8.0) and keep `VERSION` as the authority.

### 3.5 Hotfix Workflow

For urgent production fixes:

```text
main ──────────────────────────────────────────────────▶
  │                                                     │
  └── hotfix/describe-urgency ──── PR (expedited) ──────┘
```

- Hotfix branches start from main (not from a feature branch)
- CI still must pass, but review can be self-approved with a note
- Tag immediately after merge with a PATCH bump
- Deploy immediately

---

## 4. Satellite Workflow

Satellites are simpler. They ship independently and have lower ceremony.

### 4.1 Companion Satellites (Evident Family)

Companions (DOJ Library, Civics Hierarchy, ICC, EGL) follow a lighter version
of the main suite workflow.

```text
main ───────────────────────────────────▶
  │                                      │
  └── feat/short-description ─── PR ─────┘
```

**Rules:**
- PRs recommended (required for published products)
- CI should run lint + build at minimum
- Squash merge preferred
- Tag releases when publishing to GitHub Pages

**Minimum CI checks:**

| Check | Tool | Required |
| --- | --- | --- |
| Build | `npm run build` | Yes |
| Lint | ESLint | Recommended |
| Type check | `tsc --noEmit` | Recommended |
| Test | Vitest | When tests exist |

### 4.2 Venture Satellites (Tillerstead Family)

Tillerstead family products follow trade-appropriate discipline.

**Tillerstead (site):**
- Same branch → PR → merge flow as main suite
- CI: Jekyll build + Playwright nav tests + lint
- Deploy: automatic on merge via `jekyll.yml` workflow
- Tags for customer-facing milestones

**tillerstead-toolkit (API):**
- Branch → PR → merge flow
- Railway auto-deploys on push to main
- No CI currently — add `ruff check` + health check as first step
- Tag after stable API changes

**Contractor Command Center, Sweat Equity Insurance:**
- Direct push to main acceptable (early-stage prototypes)
- Tag when first public release is ready

### 4.3 Independent Satellites

Geneva Bible Study and similar personal projects:
- No workflow requirements beyond local build verification
- Push when ready, tag when publishing to app stores
- CI optional

### 4.4 Satellite Version Strategy

Satellites use `package.json` version as the source of truth (no separate
`VERSION` file needed). Semantic versioning, same rules as main suite.

**Current placeholder versions (0.0.0) should be bumped** to `0.1.0` when
the product first serves real users, and to `1.0.0` when it is publicly
launched and stable.

---

## 5. Web-Builder Export Workflow

The web-builder adds a unique step to the workflow: visual editing produces
files that must be reviewed before they enter the normal git flow.

### 5.1 Export-to-Repo Flow

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐
│  Web Builder │───▶│  Local Repo  │───▶│   Branch +   │───▶│  Normal   │
│  (edit/export│    │  (file saved │    │   PR         │    │  workflow  │
│   to folder) │    │   to disk)   │    │              │    │           │
└──────────────┘    └──────────────┘    └──────────────┘    └───────────┘
```

**Steps:**
1. Open target repo folder in web-builder
2. Edit page visually
3. Export to repo folder (File System Access API)
4. Switch to VS Code — the exported file appears as an unstaged change
5. Review the diff (`git diff`)
6. Create a branch, commit, push, PR — normal workflow from here

### 5.2 Export Review Checklist

Before committing web-builder output:

- [ ] Diff looks reasonable (no unexpected changes)
- [ ] Foundation tokens are linked (consistency check)
- [ ] Legal footer band is present
- [ ] Metadata `<head>` is complete
- [ ] Filename follows naming convention
- [ ] Image assets are optimized (not raw screenshots)

The web-builder's export preflight covers some of these automatically. The
developer is responsible for the rest via the diff review.

---

## 6. Common Review Gates

Every repo in the ecosystem uses the same categories of review gate,
scaled to the repo's tier.

### 6.1 Gate Definitions

| Gate | What It Checks | Tool |
| --- | --- | --- |
| **Build** | Code compiles, assets generate, output is valid | Stack-specific build command |
| **Lint** | Code style, formatting, common errors | ESLint, Stylelint, Ruff |
| **Type** | Type safety (where applicable) | TypeScript (`tsc`), mypy |
| **Test** | Behavior correctness | Playwright, Vitest, Pytest |
| **Security** | Known vulnerabilities, code patterns | CodeQL, pip-audit, npm audit |
| **Accessibility** | WCAG compliance, keyboard nav | Lighthouse CI, axe-core |
| **Performance** | Page weight, load time, layout shifts | Lighthouse CI |

### 6.2 Gate Requirements by Tier

| Gate | Main Suite | Companions | Ventures | Independent |
| --- | --- | --- | --- | --- |
| Build | Required | Required | Required | Required |
| Lint | Required | Recommended | Recommended | Optional |
| Type | Required | Recommended | Optional | Optional |
| Test | Required (Tier 1) | When tests exist | Optional | Optional |
| Security | Required | Recommended | Optional | Optional |
| Accessibility | Required | Recommended | Recommended | Optional |
| Performance | Recommended | Optional | Optional | Optional |

"Required" means CI blocks merge if the gate fails.  
"Recommended" means CI reports the result but does not block.  
"Optional" means the gate may not be configured at all.

### 6.3 Minimum Viable CI

For a repo that has no CI today, the starter configuration is:

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
```

This is 15 lines. It ensures the project builds. Add lint, test, and
security gates as the project matures.

For Python repos:

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pip install ruff
      - run: ruff check .
```

---

## 7. Branch Naming Patterns

All repos use the same branch naming convention. Branch names are lowercase,
use forward slashes as separators, and describe the change in 2–5 words.

### 7.1 Branch Prefixes

| Prefix | Purpose | Example |
| --- | --- | --- |
| `feat/` | New feature or capability | `feat/add-export-targeting` |
| `fix/` | Bug fix | `fix/footer-alignment-mobile` |
| `chore/` | Maintenance, dependencies, cleanup | `chore/update-tailwind-v4` |
| `docs/` | Documentation-only changes | `docs/add-release-checklist` |
| `hotfix/` | Urgent production fix | `hotfix/broken-login-redirect` |
| `refactor/` | Code restructuring (no behavior change) | `refactor/consolidate-orm` |
| `test/` | Test-only additions or fixes | `test/add-nav-playwright` |

### 7.2 Branch Rules

- Default branch is always `main` (not `master`, not `develop`)
- No long-lived feature branches — merge within days, not weeks
- No `develop` or `staging` branches — use PR previews instead
- Delete branches after merge (GitHub setting: auto-delete)
- Branch names must not contain spaces, uppercase, or special characters
  beyond `/` and `-`

### 7.3 Protected Branch Configuration

| Branch | Protection | Applies To |
| --- | --- | --- |
| `main` | Require PR, require CI pass, no force push | Main suite, Founder-Hub |
| `main` | Require CI pass | Companion + Venture satellites |
| `main` | No protection | Independent / early-stage repos |

---

## 8. Versioning Strategy

### 8.1 Version Sources

| Repo Type | Version Source | Format |
| --- | --- | --- |
| Main suite (Evident) | `VERSION` file at repo root | `MAJOR.MINOR.PATCH` |
| Node.js repos | `package.json` `version` field | `MAJOR.MINOR.PATCH` |
| Python-only repos | `__version__` in main module | `MAJOR.MINOR.PATCH` |

### 8.2 Version Lifecycle

```text
0.0.0  ──▶  0.1.0  ──▶  0.x.y  ──▶  1.0.0  ──▶  1.x.y
 │            │           │           │           │
 │            │           │           │           Stable patch/minor
 │            │           │           First public release
 │            │           Pre-release iteration
 │            First usable version
 Placeholder (not yet started)
```

| Version | Meaning | Stability Expectation |
| --- | --- | --- |
| `0.0.0` | Placeholder, no usable version exists | None |
| `0.1.0` | First version that does something for a real user | Low — expect changes |
| `0.x.y` | Active pre-release development | Breaking changes possible |
| `1.0.0` | First stable public release | Semver rules apply from here |
| `1.x.y` | Stable product with semver guarantees | Patch = safe, Minor = additive, Major = breaking |

### 8.3 Tag Format

Git tags follow this format:

```text
v{MAJOR}.{MINOR}.{PATCH}
```

Examples: `v0.8.0`, `v1.0.0`, `v1.2.3`

- Always annotated (`git tag -a`)
- Always pushed (`git push origin v1.2.3`)
- Tag message is the release summary

### 8.4 Current Version Inventory

| Repo | Current Version | Target Next Version | Action Needed |
| --- | --- | --- | --- |
| Evident | 0.7.0 / 0.8.0 (drift) | 0.8.0 (consolidate) | Sync VERSION file to 0.8.0 |
| Founder-Hub | 0.0.0 | 0.1.0 | Bump when shipping first feature |
| Tillerstead | 1.0.0 | 1.x.y | Already stable — continue semver |
| tillerstead-toolkit | N/A | 0.1.0 | Add version to `app/__init__.py` |
| DOJ Library | 0.0.0 | 0.1.0 | Bump when functional |
| Informed Consent | 0.0.0 | 0.1.0 | Bump when functional |
| Civics Hierarchy | 0.0.0 | 0.1.0 | Bump when functional |
| Essential Goods Ledger | 0.0.0 | 0.1.0 | Bump when functional |
| Geneva Bible Study | 1.0.0 | 1.x.y | Already tagged — continue |

---

## 9. Release Checklist Format

Every tagged release should include a checklist in the GitHub Release notes.
The checklist format is the same across all repos — items are skipped when not
applicable, not removed.

### 9.1 Release Note Template

```markdown
## v{VERSION} — {Title}

**Date:** {YYYY-MM-DD}
**Repo:** {repo-name}
**Tag:** v{VERSION}

### What Changed
- {change 1}
- {change 2}
- {change 3}

### Release Checklist
- [ ] Code builds without errors
- [ ] Linter passes (or warnings documented)
- [ ] Tests pass (or skipped with reason)
- [ ] Security scan clean (or findings documented)
- [ ] Version bumped in source (VERSION / package.json)
- [ ] `.evident-repo.json` releaseStatus is accurate
- [ ] Changelog / release notes written
- [ ] Tag created and pushed
- [ ] Deployment verified (live URL loads)
- [ ] No broken links on deployed pages

### Scope
- [ ] Frontend changes
- [ ] Backend changes
- [ ] API changes
- [ ] Data model changes
- [ ] Dependency updates
- [ ] Documentation only
- [ ] Infrastructure / CI changes

### Evidence Integrity (Main Suite Only)
- [ ] No original evidence mutation
- [ ] Hash verification intact
- [ ] Audit log append-only preserved
- [ ] Chain of custody unbroken
```

### 9.2 Abbreviated Checklist (Satellites)

For satellites with lower ceremony:

```markdown
## v{VERSION} — {Title}

### What Changed
- {changes}

### Checks
- [ ] Builds
- [ ] Deploys
- [ ] Looks correct on live URL
```

---

## 10. Packaging Status Integration

The `.evident-repo.json` manifest tracks two status fields that connect the
build/release workflow to the ecosystem registry.

### 10.1 packagingStatus

Reflects how well the repo is organized for release.

| Value | Meaning | Typical Workflow |
| --- | --- | --- |
| `not-started` | Raw work, no structure | Local only |
| `planned` | Architecture defined, not yet implemented | Local + docs |
| `in-progress` | Actively being structured | Branching + previews |
| `packaged` | Build works, CI configured, ready to ship | Full workflow |
| `published` | Publicly available, versioned, maintained | Full workflow + tags |

### 10.2 releaseStatus

Reflects the maturity of what the repo currently ships.

| Value | Meaning | Version Range |
| --- | --- | --- |
| `draft` | Not yet functional | 0.0.0 |
| `alpha` | Works but incomplete, expect breakage | 0.1.0 – 0.x.y |
| `beta` | Feature-complete for core use cases, expect polish issues | 0.x.y |
| `rc` | Release candidate, final testing before stable | 0.x.y or 1.0.0-rc.1 |
| `stable` | Publicly released, semver guarantees apply | 1.0.0+ |
| `maintenance` | No new features, security and bug fixes only | 1.x.y |
| `archived` | No longer maintained | Final tag |

### 10.3 Status Transitions

```text
not-started ──▶ planned ──▶ in-progress ──▶ packaged ──▶ published
draft ──▶ alpha ──▶ beta ──▶ rc ──▶ stable ──▶ maintenance ──▶ archived
```

Update these fields when the repo's state changes. The web-builder registry
and Founder-Hub ToolHub read these fields to display accurate status.

---

## 11. Deployment Target Reference

Each repo type has a preferred deployment target. This is not enforced —
repos may use alternative targets — but the preferred path is documented.

| Output Type | Preferred Target | Fallback | Config File |
| --- | --- | --- | --- |
| Static site (Jekyll) | GitHub Pages | Netlify | `jekyll.yml` workflow |
| Static site (11ty) | GitHub Pages + Netlify | Vercel | `deploy-eleventy-pages.yml` |
| SPA (Vite/React) | GitHub Pages | Netlify, Cloudflare Pages | `deploy-pages.yml` workflow |
| Python API (FastAPI) | Railway | Render, Fly.io | `railway.toml` or `render.yaml` |
| Python API (Flask) | Render | Railway | `render.yaml` |
| Docker service | Railway or self-hosted | Fly.io | `docker-compose.yml` |
| Mobile (MAUI) | GitHub Releases (MSIX) | App stores | `windows-release.yml` |
| PWA | GitHub Pages | Netlify | Standard SPA deploy |

---

## 12. Workflow Quick Reference

### For a Beginner Operator

#### I changed a file and want to publish it

```text
1. Save the file
2. Open terminal in VS Code
3. git checkout -b feat/describe-what-you-changed
4. git add .
5. git commit -m "feat: describe what you changed"
6. git push origin feat/describe-what-you-changed
7. Open the PR link that GitHub prints
8. Wait for green checks
9. Merge the PR
10. (If tagging) git checkout main && git pull
11. git tag -a v0.x.y -m "Release 0.x.y: what changed"
12. git push origin v0.x.y
```

#### I exported from web-builder and want to commit it

```text
1. Export from web-builder to the repo folder
2. Open VS Code — see the changed file in Source Control
3. Review the diff (click the file in Source Control panel)
4. Follow steps 3–12 above
```

#### I need to fix something urgently in production

```text
1. git checkout main && git pull
2. git checkout -b hotfix/describe-the-fix
3. Make the fix
4. git add . && git commit -m "fix: describe the fix"
5. git push origin hotfix/describe-the-fix
6. Open PR, merge immediately after CI passes
7. Tag with a PATCH bump
8. Verify the live deployment
```

### VS Code Tasks Available

The Evident repo includes pre-configured VS Code tasks for common operations:

| Task | Action |
| --- | --- |
| **Build site** | `npm run build` |
| **Dev server** | `npm run dev` (background) |
| **Test site** | `npm run test` |
| **Git: Stage All** | `git add .` |
| **Git: Status** | `git status -sb` |
| **Git: Diff Staged** | `git diff --staged --stat` |
| **Git: Quick Commit** | `git commit -m "Update site via Web Builder"` |
| **Git: Push to Main** | `git push origin main` |
| **Git: Full Deploy** | Stage + commit + push in one step |
| **Lint: CSS** | `npm run lint:css` |
| **Format: All Files** | `npm run format` |
| **Validate: HTML** | `npx html-validate *.html` |

---

## 13. Current Gaps to Address

| Gap | Repos Affected | Priority | Action |
| --- | --- | --- | --- |
| No CI | tillerstead-toolkit, DOJ Library | High | Add minimum viable CI (Section 6.3) |
| Version drift | Evident (0.7.0 vs 0.8.0) | High | Sync VERSION to 0.8.0 |
| Placeholder versions | 5 React satellites at 0.0.0 | Medium | Bump to 0.1.0 when functional |
| No branch protection | Most satellites | Medium | Enable on main for published repos |
| No automated tests | tillerstead-toolkit | Medium | Add health-check test at minimum |
| No security scanning | Tillerstead, satellites | Low | Add npm audit or CodeQL |
| Missing release notes | All repos | Low | Use template (Section 9) for next release |

---

## 14. Governance

This document is the canonical reference for build and release workflows
across the Evident ecosystem. It is maintained at
`docs/architecture/BUILD-RELEASE-WORKFLOW.md`.

Changes to this document should be reviewed when:
- A new deployment target is added
- A new repo enters the ecosystem
- CI gate requirements change

The workflow described here is designed for a solo operator managing multiple
repos. Scale review requirements upward when the team grows.
