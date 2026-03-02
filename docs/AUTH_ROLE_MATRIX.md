# Auth Role Matrix

> Canonical reference for Evident Technologies role-based access control.
> All enforcement is server-side. Client-side gating is cosmetic only.

## Role Hierarchy

| Rank | Role        | Description                             |
|------|-------------|-----------------------------------------|
| 3    | ADMIN       | Full system access, user management     |
| 2    | MODERATOR   | Case oversight, job management          |
| 1    | PRO_USER    | Case creation, evidence upload, export  |
| 0    | USER        | Read-only access, basic search          |

## Permission Matrix

| Action               | USER | PRO_USER | MODERATOR | ADMIN |
|----------------------|:----:|:--------:|:---------:|:-----:|
| auth.login           |  Y   |    Y     |     Y     |   Y   |
| auth.register        |  Y   |    Y     |     Y     |   Y   |
| auth.profile         |  Y   |    Y     |     Y     |   Y   |
| auth.admin           |      |          |           |   Y   |
| cases.list           |  Y   |    Y     |     Y     |   Y   |
| cases.create         |      |    Y     |     Y     |   Y   |
| cases.delete         |      |          |           |   Y   |
| evidence.view        |  Y   |    Y     |     Y     |   Y   |
| evidence.upload      |      |    Y     |     Y     |   Y   |
| evidence.download    |      |    Y     |     Y     |   Y   |
| evidence.delete      |      |          |           |   Y   |
| jobs.view            |      |    Y     |     Y     |   Y   |
| jobs.start           |      |    Y     |     Y     |   Y   |
| jobs.cancel          |      |          |     Y     |   Y   |
| search.basic         |  Y   |    Y     |     Y     |   Y   |
| search.advanced      |      |    Y     |     Y     |   Y   |
| export.create        |      |    Y     |     Y     |   Y   |
| export.verify        |  Y   |    Y     |     Y     |   Y   |
| export.download      |      |    Y     |     Y     |   Y   |
| assistant.action     |      |    Y     |     Y     |   Y   |
| admin.users          |      |          |           |   Y   |
| admin.audit_log      |      |          |           |   Y   |
| admin.system         |      |          |           |   Y   |

## Enforcement Points

- **Server-side**: `auth/role_middleware.py` — `require_role()`, `require_any_role()`, `check_permission()`
- **Decorators**: `auth/decorators.py` — `token_required`, `admin_required`
- **Access control**: `auth/access_control.py` — `purpose_required()`

## Principles

1. **Fail closed**: undefined actions are denied.
2. **No silent escalation**: role changes require ADMIN + audit log entry.
3. **Server-side only**: UI may hide elements, but server always re-checks.
4. **Audit trail**: every denied access attempt is logged.

## Session & Token Rules

| Parameter                    | Value            |
|------------------------------|------------------|
| Session lifetime             | 30 days          |
| Session cookie: HttpOnly     | Yes              |
| Session cookie: SameSite     | Lax              |
| Session cookie: Secure       | Yes (prod)       |
| Max login attempts           | 5                |
| Lockout duration             | 15 minutes       |
| 2FA support                  | TOTP (RFC 6238)  |
| API token type               | Bearer           |
| Rate limit: auth endpoints   | 10/min           |
| Rate limit: general API      | 200/hr, 50/min   |
