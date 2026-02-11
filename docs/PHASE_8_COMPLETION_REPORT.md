# Phase 8 Completion Report — API Hardening & Webhook Notifications

**Version:** 0.7.0
**Date:** 2026-02-10
**Predecessor:** Phase 7 (v0.6.0) — 238 tests
**Final test count:** 288 (238 existing + 50 new)

---

## Scope

Phase 8 delivers programmatic API access and event-driven webhook notifications
for the Evident forensic evidence platform. All new surfaces are authentication-
gated, metadata-only (no PII or content bytes), and append-only audited.

---

## Deliverables

### 1. Bearer Token Authentication Middleware (`auth/api_auth.py`)

| Component            | Detail                                                 |
| -------------------- | ------------------------------------------------------ |
| `api_token_required` | Decorator for Bearer-token-gated endpoints             |
| `api_admin_required` | Stacks on top, checks `g.api_user.is_admin`            |
| Token validation     | Expiration, active state, user active, `last_used_at`  |
| Injection            | Sets `g.api_token`, `g.api_user` for downstream use    |

### 2. Versioned REST API (`routes/api_v1.py`)

Blueprint at `/api/v1/` — 15+ endpoints:

| Group    | Endpoints                                                        |
| -------- | ---------------------------------------------------------------- |
| Cases    | `GET /cases` (paginated, filterable), `GET /cases/<id>`          |
| Evidence | `GET /evidence`, `GET /evidence/<id>`, `GET /evidence/<id>/audit`, `GET /evidence/verify/<hash>` |
| Audit    | `GET /audit` (global, paginated, filterable by action/since)     |
| Tokens   | `GET /tokens`, `POST /tokens`, `DELETE /tokens/<id>`             |
| Webhooks | `GET /webhooks`, `POST /webhooks`, `DELETE /webhooks/<id>`       |
| Health   | `GET /health` (no auth)                                          |

All serializers return metadata only. No PII, no content bytes, no transcripts.
Pagination helper enforces max 100 per page, default 25.

### 3. Webhook Subscription Model (`models/webhook.py`)

| Feature               | Detail                                              |
| --------------------- | --------------------------------------------------- |
| HMAC-SHA256 signing   | Every payload signed with subscription secret       |
| Event filtering       | 11 valid event types or `*` wildcard                |
| Auto-disable          | After 10 consecutive delivery failures              |
| Delivery health       | `consecutive_failures`, `last_failure_at/reason`, `last_success_at`, `total_deliveries` |
| `WebhookDeliveryLog`  | Append-only audit of every delivery attempt         |

**Valid events:**
`evidence.ingested`, `evidence.integrity_verified`, `evidence.integrity_failed`,
`evidence.exported`, `case.created`, `case.updated`, `case.exported`,
`share_link.created`, `share_link.accessed`, `share_link.revoked`,
`audit.critical`.

### 4. Webhook Service (`services/webhook_service.py`)

| Method                | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| `dispatch()`          | Match active subs, build envelope, deliver           |
| `create_subscription()` | Validate events, generate secret, persist          |
| `delete_subscription()` | Soft-deactivate (sets `is_active=False`)           |
| `list_subscriptions()` | All subs for user, newest first                     |
| `_deliver()`          | HMAC sign, POST with headers, 10s timeout, log      |

Delivery headers: `X-Evident-Event`, `X-Evident-Signature`, `X-Evident-Delivery`.

---

## Test Coverage (50 new tests)

| Class                      | Tests | Covers                                     |
| -------------------------- | ----- | ------------------------------------------ |
| `TestApiTokenAuth`         | 6     | Missing/invalid/expired/inactive tokens, valid access, usage tracking |
| `TestCasesApi`             | 6     | List, pagination, filter, get, 404, no PII |
| `TestEvidenceApi`          | 5     | List, get, 404, hash verify (found/not)    |
| `TestAuditApi`             | 3     | List, invalid since, evidence audit trail   |
| `TestTokenApi`             | 6     | List, create, missing name, invalid expiry, revoke, 404 |
| `TestWebhookModel`         | 7     | Secret gen, sign/verify, wildcard/specific event, inactive, auto-disable, success reset |
| `TestWebhookService`       | 6     | Create, invalid events, list, delete, wrong-user delete, dispatch |
| `TestWebhookRoutes`        | 7     | List, create, non-HTTPS reject, missing fields, invalid events, delete, 404 |
| `TestApiHealth`            | 2     | No auth required, version present           |
| `TestWebhookDeliveryLog`   | 1     | Log created on dispatch                     |
| **Total**                  | **50** |                                            |

---

## Regression

| Suite                        | Tests | Status  |
| ---------------------------- | ----- | ------- |
| Phase 1 — Forensic Integrity | 17    | Passed  |
| Phase 2 — Defensibility      | 17    | Passed  |
| Phase 3 — Case Event Invariants | 22 | Passed  |
| Phase 3 — Case Management    | 17    | Passed  |
| Phase 4 — Migration Smoke    | 9     | Passed  |
| Phase 4 — Integrity Statement | 29   | Passed  |
| Phase 5 — Access Controls    | 21    | Passed  |
| Phase 5 — Storage Backend    | 25    | Passed  |
| Phase 6 — Court Package      | 15    | Passed  |
| Phase 6 — Health & Logging   | 19    | Passed  |
| Phase 7 — Share & Transparency | 47  | Passed  |
| **Phase 8 — API & Webhooks** | **50** | **Passed** |
| **Total**                    | **288** | **All green** |

---

## Files Changed

| File                           | Action   | Purpose                          |
| ------------------------------ | -------- | -------------------------------- |
| `auth/api_auth.py`            | Created  | Bearer token middleware           |
| `models/webhook.py`           | Created  | Subscription and delivery models  |
| `services/webhook_service.py` | Created  | Event dispatch engine             |
| `routes/api_v1.py`            | Created  | Versioned REST API blueprint      |
| `tests/test_api_and_webhooks.py` | Created | Phase 8 test suite             |
| `app_config.py`               | Modified | Register `api_v1_bp` blueprint    |
| `VERSION`                     | Modified | 0.6.0 → 0.7.0                    |
| `package.json`                | Modified | 0.6.0 → 0.7.0                    |
| `CHANGELOG.md`                | Modified | Phase 8 entry                     |

---

## Forensic Integrity Notes

- All API responses are serialized metadata only — no evidence content, no
  transcripts, no PII.
- Webhook secrets are generated server-side and returned exactly once on
  creation. They are stored as-is (not hashed) because they are server-side
  signing keys, not authentication credentials.
- `WebhookDeliveryLog` is append-only. No delete or update operations are
  exposed.
- HMAC-SHA256 with constant-time comparison (`hmac.compare_digest`) for all
  signature verification.
- HTTPS enforcement on webhook URLs (no plaintext delivery).
- Auto-disable after 10 consecutive failures prevents unbounded retry storms.

---

## Phase Lock

Phase 8 (v0.7.0) is now locked. No modifications without change-control
approval per `docs/CHANGE_CONTROL_POLICY.md`.
