# Key Management & Secret Rotation

> Evident Technologies — Operational Security Reference  
> Version: 0.5.0 (Phase 6)

---

## Scope

This document covers the lifecycle of secrets used by the Evident platform.
It does **not** constitute legal advice or a certified security policy.

---

## 1. SECRET_KEY (Flask Session Signing)

### Purpose

Flask uses `SECRET_KEY` to sign session cookies and CSRF tokens.
Compromise of this key allows session forgery.

### Generation

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

This produces a 64-character hex string (256-bit entropy).

### Storage

- Store in `.env` file with `chmod 600` permissions.
- Or inject via environment variable in systemd unit / container orchestrator.
- Never commit to version control.

### Rotation Procedure

1. Generate a new key (see above).
2. Update `.env` (or your secrets manager).
3. Restart the application: `sudo systemctl restart evident`
4. **Effect**: All existing user sessions are invalidated.
   Users must re-authenticate.
5. This is by design — there is no "soft rotation" for Flask session keys.

### Rotation Schedule

- **Minimum**: Every 90 days.
- **Immediately** if: a key is committed to VCS, a server is compromised,
  or a team member with production access departs.

---

## 2. DATABASE_URL Credentials

### Generation

```bash
# Generate a strong random password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### Rotation Procedure

1. In PostgreSQL:
   ```sql
   ALTER USER evident WITH PASSWORD 'new-strong-password';
   ```
2. Update `DATABASE_URL` in `.env`.
3. Restart the application.

### Notes

- Use SSL connections to PostgreSQL in production:
  ```
  DATABASE_URL=postgresql://evident:PASS@host:5432/evident?sslmode=require
  ```
- Consider using IAM authentication or short-lived tokens where supported.

---

## 3. S3 / Object Storage Credentials

When `STORAGE_BACKEND=s3`, the application needs AWS credentials.

### Preferred: IAM Roles (no static keys)

- On EC2: assign an instance profile with the required S3 permissions.
- On ECS/EKS: use task roles or service account annotations.

### Fallback: Static Keys

- Store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`.
- Rotate every 90 days via IAM console.
- Restrict the key to minimal S3 permissions:
  `s3:GetObject`, `s3:PutObject`, `s3:HeadObject`, `s3:ListBucket`.

---

## 4. Rate-Limiter Redis Password (Optional)

If Flask-Limiter is backed by Redis:

```
RATELIMIT_STORAGE_URI=redis://:PASSWORD@localhost:6379/0
```

- Bind Redis to `127.0.0.1` only.
- Use `requirepass` in `redis.conf`.
- Rotate by updating Redis config and `.env`, then restarting both.

---

## 5. API Tokens (Future)

When Evident exposes a programmatic API:

- Tokens should be SHA-256 hashed at rest (store hash, not plaintext).
- Tokens should have explicit expiry (max 1 year).
- Implement `/api/tokens/rotate` endpoint.
- Log every token issuance and revocation in the audit stream.

---

## 6. Secret Hygiene Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `.env` file permissions are `600` (owner read/write only)
- [ ] No secrets appear in log output or error pages
- [ ] `DEBUG=False` in production (prevents stack traces with env vars)
- [ ] Secrets are not passed as CLI arguments (visible in `ps` output)
- [ ] Backup files containing secrets are encrypted at rest
- [ ] Team members with production access are logged and reviewed quarterly

---

## 7. Incident Response — Key Compromise

If a secret is suspected compromised:

1. **Rotate immediately** (instructions above per key type).
2. Review audit logs for unauthorized access:
   ```bash
   python scripts/audit_report.py activity --since YYYY-MM-DD
   ```
3. Check evidence integrity:
   ```bash
   python scripts/audit_report.py evidence --id <suspected_item>
   ```
4. Document the incident, timeline, and remediation in a post-mortem.
5. Notify affected parties as required by applicable data-breach regulations.
