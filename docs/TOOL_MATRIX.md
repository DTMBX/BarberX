# Legal Suite Tool Matrix

> Canonical registry of all Evident Technologies platform tools.
> No undocumented tools allowed. Every tool must have an entry here.

Last updated: 2026-03-01

---

## Domain: AUTH

| Tool               | API Route                  | UI Surface          | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|----------------------------|---------------------|:-------------:|:---------:|-----------------------------------|
| Login              | POST /auth/login           | /auth/login         | (public)      | Yes       | tests/tier1/auth.spec.ts          |
| Logout             | POST /auth/logout          | Header menu         | USER+         | Yes       | tests/tier1/auth.spec.ts          |
| Register           | POST /auth/register        | /auth/register      | (public)      | Yes       | tests/tier1/auth.spec.ts          |
| Password Reset     | POST /auth/reset-password  | /auth/reset         | (public)      | Yes       | tests/tier2/auth-edge.spec.ts     |
| 2FA Setup          | POST /auth/2fa/setup       | /auth/profile       | USER+         | Yes       | tests/tier2/auth-edge.spec.ts     |
| 2FA Disable        | POST /auth/2fa/disable     | /auth/profile       | USER+         | Yes       | tests/tier2/auth-edge.spec.ts     |
| Profile            | GET /auth/profile          | /auth/profile       | USER+         | No        | tests/tier1/auth.spec.ts          |
| API Token Manage   | POST /auth/api/tokens      | /auth/profile       | PRO_USER+     | Yes       | tests/tier2/auth-edge.spec.ts     |

## Domain: CASES

| Tool               | API Route                  | UI Surface          | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|----------------------------|---------------------|:-------------:|:---------:|-----------------------------------|
| List Cases         | GET /api/v1/cases          | /cases              | USER+         | No        | tests/tier1/cases.spec.ts         |
| Create Case        | POST /api/v1/cases         | /cases/new          | PRO_USER+     | Yes       | tests/tier1/cases.spec.ts         |
| View Case          | GET /api/v1/cases/:id      | /cases/:id          | USER+         | Yes       | tests/tier1/cases.spec.ts         |
| Update Case        | PUT /api/v1/cases/:id      | /cases/:id/edit     | PRO_USER+     | Yes       | tests/tier2/cases-edge.spec.ts    |
| Delete Case        | DELETE /api/v1/cases/:id   | /cases/:id          | ADMIN         | Yes       | tests/tier2/cases-edge.spec.ts    |
| Case Events        | GET /api/v1/cases/:id/events | /cases/:id/timeline | USER+       | No        | tests/tier1/cases.spec.ts         |

## Domain: EVIDENCE

| Tool               | API Route                          | UI Surface               | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|------------------------------------|--------------------------|:-------------:|:---------:|-----------------------------------|
| Upload Evidence    | POST /api/v1/evidence/upload       | /cases/:id/upload        | PRO_USER+     | Yes       | tests/tier1/evidence.spec.ts      |
| View Evidence      | GET /api/v1/evidence/:id           | /evidence/:id            | USER+         | Yes       | tests/tier1/evidence.spec.ts      |
| Download Original  | GET /api/v1/evidence/:id/download  | /evidence/:id            | PRO_USER+     | Yes       | tests/tier1/evidence.spec.ts      |
| List Evidence      | GET /api/v1/cases/:id/evidence     | /cases/:id               | USER+         | No        | tests/tier1/evidence.spec.ts      |
| Delete Evidence    | DELETE /api/v1/evidence/:id        | /evidence/:id            | ADMIN         | Yes       | tests/tier2/evidence-edge.spec.ts |
| Verify Integrity   | POST /api/v1/evidence/:id/verify   | /evidence/:id            | USER+         | Yes       | tests/tier1/evidence.spec.ts      |
| View Chain of Custody | GET /api/v1/evidence/:id/chain  | /evidence/:id/chain      | USER+         | No        | tests/tier1/evidence.spec.ts      |

## Domain: JOBS

| Tool               | API Route                          | UI Surface               | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|------------------------------------|--------------------------|:-------------:|:---------:|-----------------------------------|
| Start Transcode    | POST /api/v1/jobs/transcode        | /cases/:id/evidence/:eid | PRO_USER+     | Yes       | tests/tier1/jobs.spec.ts          |
| View Job Status    | GET /api/v1/jobs/:id               | /jobs/:id                | PRO_USER+     | No        | tests/tier1/jobs.spec.ts          |
| List Jobs          | GET /api/v1/jobs                   | /jobs                    | PRO_USER+     | No        | tests/tier1/jobs.spec.ts          |
| Cancel Job         | POST /api/v1/jobs/:id/cancel       | /jobs/:id                | MODERATOR+    | Yes       | tests/tier2/jobs-edge.spec.ts     |

## Domain: SEARCH

| Tool               | API Route                          | UI Surface               | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|------------------------------------|--------------------------|:-------------:|:---------:|-----------------------------------|
| Basic Search       | GET /api/v1/search                 | /search                  | USER+         | No        | tests/tier1/search.spec.ts        |
| Advanced Search    | POST /api/v1/search/advanced       | /search/advanced         | PRO_USER+     | Yes       | tests/tier2/search-edge.spec.ts   |
| Search Within Case | GET /api/v1/cases/:id/search       | /cases/:id               | USER+         | No        | tests/tier1/search.spec.ts        |

## Domain: EXPORT

| Tool               | API Route                          | UI Surface               | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|------------------------------------|--------------------------|:-------------:|:---------:|-----------------------------------|
| Create Export      | POST /api/v1/export                | /cases/:id/export        | PRO_USER+     | Yes       | tests/tier1/export.spec.ts        |
| Download Export    | GET /api/v1/export/:id/download    | /exports/:id             | PRO_USER+     | Yes       | tests/tier1/export.spec.ts        |
| Verify Export      | POST /api/v1/export/:id/verify     | /exports/:id             | USER+         | Yes       | tests/tier1/export.spec.ts        |
| List Exports       | GET /api/v1/exports                | /exports                 | PRO_USER+     | No        | tests/tier1/export.spec.ts        |

## Domain: AI ASSISTANT

| Tool               | API Route                          | UI Surface               | Required Role | Audit Log | E2E Test Ref                      |
|--------------------|------------------------------------|--------------------------|:-------------:|:---------:|-----------------------------------|
| Execute Action     | POST /assistant/action             | Assistant panel          | PRO_USER+     | Yes       | tests/tier1/assistant.spec.ts     |
| List Capabilities  | GET /assistant/capabilities        | Assistant panel          | PRO_USER+     | No        | tests/tier1/assistant.spec.ts     |
| Action History     | GET /assistant/history             | Assistant panel          | PRO_USER+     | No        | tests/tier2/assistant-edge.spec.ts|

---

## Rules

1. **No undocumented tools.** Every API route serving a user-facing action must appear here.
2. **Audit log column is binding.** If "Yes", the implementation must write to `AuditStream`.
3. **Role column is binding.** Enforcement is server-side via `auth/role_middleware.py`.
4. **E2E column is binding.** Each referenced test file must exist and cover the tool.
5. **Purpose-required endpoints.** All evidence download and export endpoints require a stated access purpose per `auth/access_control.py`.
