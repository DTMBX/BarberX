# Legal Suite Wiring + Assistant Integration — Implementation Report

> Branch: `refactor/auth-consolidated-v3`
> Date: 2026-03-01
> Base: `main` @ `18c586502`

---

## Phase 0 — Repo Stability Audit

### Status: PASS

| Check               | Result  | Notes                                          |
|---------------------|---------|------------------------------------------------|
| `main` up to date   | PASS    | Local and `origin/main` in sync.               |
| PR #131             | N/A     | Already merged (HEAD is PR #132).              |
| PR #132             | PASS    | Current HEAD, builds clean.                    |
| `npm install`       | PASS    | 1625 packages, 12 vulns (0 critical prod).     |
| `lint:css`          | PASS    | Stylelint on 5 files, no errors.               |
| `lint:js`           | FIXED   | ESLint config used ESM in CJS package. Fixed.  |
| Playwright smoke    | PASS    | 11/11 tests passing after title fix.           |
| Node version        | FIXED   | `.nvmrc` updated from 20 → 22.                |
| CI workflows        | PASS    | All active workflows use Node 22.              |
| Node 18 refs        | NONE    | Only in disabled `webpack.yml`.                |
| Lighthouse          | N/A     | Allowed to fail on PR (per existing config).   |

### Files Touched in Phase 0

- `.nvmrc` — Updated to 22
- `eslint.config.js` — Fixed `export default` → `module.exports`
- `tests/basic.spec.js` — Fixed stale brand name in title assertion
- `package.json` / `package-lock.json` — Added `@playwright/test`

---

## Phase 1 — Auth Consolidation

### Status: COMPLETE

#### Branch Analysis

| Branch                          | Divergent Files  | Unique Commits |
|---------------------------------|------------------|:--------------:|
| `feat/auth-security-v2`        | auth/models.py, auth/routes.py | 1     |
| `feat/enhanced-auth-security`  | auth/models.py, auth/routes.py | 1     |

**Finding**: Both branches are byte-identical (zero diff). They share the
same tree. The canonical commit (`1d7486496`) was cherry-picked into
`refactor/auth-consolidated-v3`.

#### Improvements Cherry-Picked

1. **Brute force protection** — Login attempt tracking with 5-attempt lockout (15 min).
2. **2FA support** — TOTP setup, verify, disable via `pyotp` + QR code.
3. **Unified login errors** — No information leakage (same error for invalid user/password).
4. **Audit logging** — `AuditLog.log_failed_login()` static method for anonymous events.
5. **Cleanup** — Removed stale `from datetime import timedelta` at file end.

#### New: Centralized Role Middleware

Created `auth/role_middleware.py`:
- `require_role(minimum_role)` decorator with hierarchy enforcement
- `require_any_role(roles)` for flexible access control
- `check_permission(action)` — programmatic check against `ROLE_MATRIX`
- `ROLE_MATRIX` — maps every action to allowed roles
- Fail-closed: undocumented actions denied by default
- API-aware: returns JSON 401/403 for API requests, aborts for HTML

#### Documentation

Created `docs/AUTH_ROLE_MATRIX.md`:
- Full permission matrix (24 actions × 4 roles)
- Session/token configuration table
- Enforcement point references

### Branches Recommended for Deletion

| Branch                           | Reason                          |
|----------------------------------|---------------------------------|
| `feat/auth-security-v2`         | Superseded by consolidated v3.  |
| `feat/enhanced-auth-security`   | Identical to v2.                |
| `test/fix-playwright-suite`     | Stale test branch.              |

---

## Phase 2 — Legal Suite Tool Matrix

### Status: COMPLETE

Created `docs/TOOL_MATRIX.md` defining all 7 domains:

| Domain        | Tools Documented |
|---------------|:----------------:|
| AUTH          | 8                |
| CASES         | 6                |
| EVIDENCE      | 7                |
| JOBS          | 4                |
| SEARCH        | 3                |
| EXPORT        | 4                |
| AI ASSISTANT  | 3                |

Each entry specifies: API route, UI surface, required role, audit requirement,
and E2E test reference.

---

## Phase 3 — AI Assistant Capability Registry

### Status: COMPLETE

Created `backend/app/core/capability_registry.py`:

#### Architecture

```
POST /assistant/action
  → CapabilityRegistry.execute()
    → 1. Validate capability_id exists
    → 2. Enforce role (server-side, ranked hierarchy)
    → 3. Validate args against ParamSchema
    → 4. Execute handler
    → 5. Record ActionAuditRecord (always, even on failure)
    → Return { status, result, audit_reference }
```

#### Built-in Capabilities

| capability_id         | Required Role | Audit |
|-----------------------|:-------------:|:-----:|
| case.create_note      | PRO_USER      | Yes   |
| evidence.upload       | PRO_USER      | Yes   |
| job.start_transcode   | PRO_USER      | Yes   |
| export.create         | PRO_USER      | Yes   |
| export.verify         | USER          | Yes   |

#### Design Constraints

- No direct DB access from assistant layer.
- Registry is freezable (immutable after startup).
- All args hashed (SHA-256) for audit traceability.
- Unknown parameters rejected (no silent pass-through).
- Capability definitions are frozen dataclasses.

#### Endpoint Blueprint

Created `backend/app/core/assistant_routes.py`:
- `POST /assistant/action` — Execute capability
- `GET /assistant/capabilities` — List all registered capabilities
- `GET /assistant/history` — Query audit log

---

## Phase 4 — UI Receipt System

### Status: COMPLETE

Created:
- `src/assets/js/assistant-receipt.js` — `AssistantReceipt` class + `executeAndReceipt()` helper
- `src/assets/css/assistant-receipt.css` — WCAG AA compliant styling

#### Receipt Properties

Every AI action receipt displays:
- Capability executed (e.g., `case.create_note`)
- Affected case ID
- Timestamp (ISO-8601)
- Audit reference (linked to audit log entry)
- Status icon (success/denied/error/validation)
- Error details (when applicable)

#### Accessibility

- `role="log"` container with `aria-live="polite"`
- `role="article"` per receipt
- Focus management for screen readers
- `prefers-reduced-motion` respected
- Dark mode support
- XSS prevention via textContent escaping

---

## Phase 5 — Playwright Tiered Testing

### Status: COMPLETE — 11/11 Tier 1 passing

#### Test Structure

| Tier | Directory     | Gate      | Tests |
|------|---------------|-----------|:-----:|
| 1    | tests/tier1/  | PR (must pass) | 11 |
| 2    | tests/tier2/  | Full suite     | 7  |
| 3    | tests/tier3/  | Optional perf  | 2  |

#### Tier 1 — PR Gate Smoke (all passing)

| File                    | Tests | Status |
|-------------------------|:-----:|:------:|
| auth.spec.ts            | 3     | PASS   |
| cases.spec.ts           | 1     | PASS   |
| evidence.spec.ts        | 1     | PASS   |
| export.spec.ts          | 1     | PASS   |
| jobs.spec.ts            | 1     | PASS   |
| search.spec.ts          | 1     | PASS   |
| assistant.spec.ts       | 2     | PASS   |
| basic.spec.js (root)    | 1     | PASS   |

#### Test Quality

- No `5s` arbitrary waits
- Strict mode selectors (`getByRole`, `getByText`)
- Deterministic assertions (status code ranges)
- Graceful degradation (static site vs. full backend)

---

## Phase 6 — Evidence Pipeline Hardening

### Status: VERIFIED — No violations found

#### Existing Compliance (verified by code review)

| Requirement                          | Status  | Implementation                           |
|--------------------------------------|---------|------------------------------------------|
| Originals immutable                  | PASS    | `FileExistsError` on duplicate store     |
| SHA-256 stored                       | PASS    | Computed at ingest, verified post-copy   |
| Derivatives reference original hash  | PASS    | Stored under `derivatives/<sha256>/`     |
| Audit log append-only                | PASS    | `AuditStream.record()` — no edit/delete  |
| Export reproducible                  | PASS    | Manifests store transforms + params      |
| Post-copy integrity check            | PASS    | Hash recomputed after copy, file deleted on mismatch |

#### New: Programmatic Integrity Verifier

Created `services/evidence_integrity_verifier.py`:
- 5 automated checks per evidence item
- Produces JSON compliance report
- Exit code 0/1 for CI integration
- Checks: sha256_recorded, original_immutable, derivative_hash_valid, audit_append_only, manifest_completeness

---

## Phase 7 — Clean Branch Structure

### Status: COMPLETE

Updated `docs/CONTRIBUTING.md` with:
- Branching strategy (long-lived: main, gh-pages, release/*, hotfix/*)
- Short-lived patterns (feat, fix, refactor, chore, test, docs)
- PR requirements checklist
- Commit message format
- Development setup commands
- Architecture principles
- Security reporting
- Stale branch cleanup procedure

### Branches Recommended for Remote Deletion

```bash
git push origin --delete feat/auth-security-v2
git push origin --delete feat/enhanced-auth-security
git push origin --delete test/fix-playwright-suite
```

---

## Phase 8 — Summaries

### Architecture Summary

```
┌─────────────────────────────────────────────────┐
│                 Frontend (Eleventy)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Pages    │ │ Tools UI │ │ Assistant Panel  │ │
│  │ (static) │ │ (static) │ │ (receipt system) │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │ API calls
┌────────────────────▼────────────────────────────┐
│               Flask Backend (API)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Auth     │ │ Routes   │ │ Assistant        │ │
│  │ (roles,  │ │ (cases,  │ │ (capability      │ │
│  │  2FA,    │ │  evidence│ │  registry,       │ │
│  │  rate    │ │  export) │ │  audit)          │ │
│  │  limit)  │ │          │ │                  │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Services Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Evidence │ │ Hashing  │ │ Audit Stream     │ │
│  │ Store    │ │ Service  │ │ (append-only,    │ │
│  │ (immut.) │ │ (SHA256) │ │  dual-write)     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Security Summary

| Layer              | Mechanism                                    |
|--------------------|----------------------------------------------|
| Authentication     | Flask-Login + session cookies                |
| 2FA                | TOTP (RFC 6238) via pyotp                    |
| Rate Limiting      | Flask-Limiter (10/min auth, 200/hr general)  |
| Role Enforcement   | `auth/role_middleware.py` — server-side only  |
| Brute Force        | 5-attempt lockout, 15-min duration           |
| Secure Headers     | Flask-Talisman (CSP, HSTS, X-Frame-Options)  |
| Session            | HttpOnly, SameSite=Lax, Secure (prod)        |
| Evidence Integrity | SHA-256 at ingest + post-copy verification   |
| Audit              | Append-only, dual-write (DB + manifest)      |
| Assistant          | Capability-restricted, schema-validated      |

### CI Map

| Workflow                    | Trigger      | Required | Node |
|-----------------------------|-------------|----------|------|
| ci.yml                      | PR + push   | Yes      | 22   |
| law-tests.yml               | PR + push   | Yes      | 22   |
| lighthouse-ci.yml           | PR          | No       | 22   |
| security-scan.yml           | PR + push   | Yes      | 22   |
| pages.yml                   | push (main) | Yes      | 22   |
| python.yml                  | PR + push   | Yes      | N/A  |

### Test Coverage Map

| Tier | Scope         | Tests | Status  | Gate     |
|------|---------------|:-----:|---------|----------|
| 1    | PR Smoke      | 11    | PASSING | Required |
| 2    | Full Suite    | 7     | Written | Optional |
| 3    | Performance   | 2     | Written | Optional |

### Recommended Next PR Sequence

1. **PR: Auth Consolidation** — Merge `refactor/auth-consolidated-v3` → `main`
   - Includes: role middleware, 2FA, brute force, test fixes
   - Delete: `feat/auth-security-v2`, `feat/enhanced-auth-security`

2. **PR: Backend Wiring** — Wire Flask assistant blueprint into app factory
   - Register capabilities at startup
   - Add integration tests

3. **PR: CI Tiered Tests** — Update CI to run Tier 1 as gate, Tier 2 on schedule
   - Add Tier 1 to `ci.yml` required step
   - Add Tier 2/3 as nightly workflow

4. **PR: Evidence Verifier CI** — Add integrity verifier to CI pipeline
   - Run `evidence_integrity_verifier.py` on release branches

5. **PR: Stale Branch Cleanup** — Delete obsolete remote branches

---

## Files Created

| File                                          | Purpose                          |
|-----------------------------------------------|----------------------------------|
| `auth/role_middleware.py`                     | Centralized role enforcement     |
| `backend/app/core/capability_registry.py`    | AI Assistant capability registry |
| `backend/app/core/assistant_routes.py`       | Assistant Flask blueprint        |
| `backend/app/core/__init__.py`               | Package init                     |
| `backend/app/__init__.py`                    | Package init                     |
| `backend/__init__.py`                        | Package init                     |
| `services/evidence_integrity_verifier.py`    | Evidence pipeline verifier       |
| `src/assets/js/assistant-receipt.js`         | UI receipt component             |
| `src/assets/css/assistant-receipt.css`       | Receipt styling                  |
| `docs/TOOL_MATRIX.md`                        | Legal Suite tool registry        |
| `docs/AUTH_ROLE_MATRIX.md`                   | Role permission matrix           |
| `tests/tier1/auth.spec.ts`                   | Tier 1: Auth tests               |
| `tests/tier1/cases.spec.ts`                  | Tier 1: Cases tests              |
| `tests/tier1/evidence.spec.ts`               | Tier 1: Evidence tests           |
| `tests/tier1/export.spec.ts`                 | Tier 1: Export tests             |
| `tests/tier1/jobs.spec.ts`                   | Tier 1: Jobs tests               |
| `tests/tier1/search.spec.ts`                 | Tier 1: Search tests             |
| `tests/tier1/assistant.spec.ts`              | Tier 1: Assistant tests          |
| `tests/tier2/auth-edge.spec.ts`              | Tier 2: Auth edge cases          |
| `tests/tier2/evidence-edge.spec.ts`          | Tier 2: Evidence edge cases      |
| `tests/tier2/export-edge.spec.ts`            | Tier 2: Export edge cases        |
| `tests/tier2/assistant-edge.spec.ts`         | Tier 2: Assistant edge cases     |
| `tests/tier3/performance.spec.ts`            | Tier 3: Performance tests        |

## Files Modified

| File                       | Change                                    |
|----------------------------|-------------------------------------------|
| `.nvmrc`                   | 20 → 22                                  |
| `eslint.config.js`        | `export default` → `module.exports`      |
| `tests/basic.spec.js`     | Title regex: Tillerstead → Evident       |
| `package.json`            | Added `@playwright/test`                  |
| `auth/models.py`          | Added `AuditLog.log_failed_login()`      |
| `auth/routes.py`          | Brute force + 2FA + unified errors       |
| `docs/CONTRIBUTING.md`    | Full rewrite with branching strategy     |
