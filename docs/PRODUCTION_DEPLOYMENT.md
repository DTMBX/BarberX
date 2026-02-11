# Production Deployment Guide

> Evident Technologies — Evidence Management Platform  
> Version: 0.5.0 (Phase 6)

---

## Prerequisites

| Component   | Minimum Version | Purpose                              |
|-------------|-----------------|--------------------------------------|
| Python      | 3.12            | Application runtime                  |
| PostgreSQL  | 15              | Production database                  |
| nginx       | 1.24            | Reverse proxy, TLS termination       |
| Redis       | 7.0             | Rate-limiter storage (optional)      |

---

## 1. System Preparation

```bash
# Create service user (no login shell)
sudo useradd -r -s /usr/sbin/nologin -d /opt/evident evident

# Create directories
sudo mkdir -p /opt/evident/{instance,uploads,evidence_store,logs}
sudo chown -R evident:evident /opt/evident
```

---

## 2. Application Installation

```bash
cd /opt/evident
sudo -u evident git clone https://github.com/your-org/evident.git .
sudo -u evident python3.12 -m venv venv
sudo -u evident venv/bin/pip install --upgrade pip
sudo -u evident venv/bin/pip install -r _backend/requirements.txt
sudo -u evident venv/bin/pip install flask-limiter flask-talisman gunicorn
```

---

## 3. Environment Configuration

```bash
sudo -u evident cp deploy/.env.template .env
sudo -u evident chmod 600 .env
# Edit .env — fill in SECRET_KEY, DATABASE_URL, etc.
sudo -u evident nano .env
```

### Required Environment Variables

| Variable           | Example                                          | Notes                                   |
|--------------------|--------------------------------------------------|-----------------------------------------|
| `FLASK_ENV`        | `production`                                     | Enables secure cookies, JSON logging    |
| `SECRET_KEY`       | 64-char random hex                               | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL`     | `postgresql://evident:PASS@localhost:5432/evident`| Production DB                           |
| `STORAGE_BACKEND`  | `local` or `s3`                                  | Evidence file storage                   |
| `STORAGE_ROOT`     | `/opt/evident/evidence_store`                    | Only when `STORAGE_BACKEND=local`       |

---

## 4. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createuser --pwprompt evident
sudo -u postgres createdb -O evident evident

# Run Alembic migrations
cd /opt/evident
sudo -u evident FLASK_ENV=production venv/bin/flask db upgrade
```

See [DATABASE_OPERATIONS.md](DATABASE_OPERATIONS.md) for backup/restore and
SQLite-to-PostgreSQL migration procedures.

---

## 5. Gunicorn (Application Server)

Configuration: [`deploy/gunicorn.conf.py`](../deploy/gunicorn.conf.py)

```bash
# Test manually
sudo -u evident venv/bin/gunicorn -c deploy/gunicorn.conf.py wsgi:app

# Install systemd unit
sudo cp deploy/evident.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now evident
sudo systemctl status evident
```

### Tuning

| Variable            | Default         | Guidance                              |
|---------------------|-----------------|---------------------------------------|
| `GUNICORN_WORKERS`  | CPU × 2 + 1    | Increase for high-concurrency         |
| `GUNICORN_THREADS`  | 2               | Useful for I/O-bound workloads        |
| `GUNICORN_TIMEOUT`  | 120 s           | Raise if large uploads timeout        |

---

## 6. nginx (Reverse Proxy)

Configuration template: [`deploy/nginx.conf`](../deploy/nginx.conf)

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/evident
sudo ln -s /etc/nginx/sites-available/evident /etc/nginx/sites-enabled/
# Edit server_name and SSL paths
sudo nano /etc/nginx/sites-available/evident
sudo nginx -t
sudo systemctl reload nginx
```

### TLS Certificates

```bash
sudo certbot --nginx -d evident.example.com
```

---

## 7. Health Checks

| Endpoint        | Method | Auth | Purpose                        |
|-----------------|--------|------|--------------------------------|
| `/health/live`  | GET    | No   | Process is running             |
| `/health/ready` | GET    | No   | Database connection functional |
| `/health/info`  | GET    | No   | Version, environment, uptime   |

Configure load-balancer health probes against `/health/ready`.

---

## 8. Structured Logging

In production (`FLASK_ENV=production`), all log output is JSON-structured:

```json
{
  "timestamp": "2025-01-15T12:00:00.000000+00:00",
  "level": "INFO",
  "logger": "evident.http",
  "message": "request_end GET /health/live status=200",
  "request_id": "a1b2c3d4e5f6...",
  "method": "GET",
  "path": "/health/live",
  "remote_addr": "127.0.0.1"
}
```

Every response includes an `X-Request-ID` header for end-to-end tracing.

In development, logging uses human-readable format.

---

## 9. Rate Limiting

Default: in-memory (sufficient for single-process). For multi-worker
production, point to Redis:

```
RATELIMIT_STORAGE_URI=redis://localhost:6379/0
```

Current limits:

| Route              | Limit   |
|--------------------|---------|
| Login              | 10/min  |
| Register           | 5/min   |
| Forgot password    | 3/min   |
| Reset password     | 5/min   |
| Global default     | 200/hr  |

---

## 10. Storage Configuration

### Local Filesystem (default)

```
STORAGE_BACKEND=local
STORAGE_ROOT=/opt/evident/evidence_store
```

Ensure the directory is owned by the `evident` user and has `750` permissions.

### S3-Compatible

```
STORAGE_BACKEND=s3
S3_BUCKET=evident-evidence
S3_PREFIX=prod
S3_REGION=us-east-1
```

Requires `boto3` (`pip install boto3`). IAM role or credentials must grant
`s3:GetObject`, `s3:PutObject`, `s3:HeadObject`, `s3:ListBucket`.

---

## 11. Backups

See [DATABASE_OPERATIONS.md](DATABASE_OPERATIONS.md) for detailed procedures.

Quick reference:

```bash
# PostgreSQL dump
pg_dump -Fc evident > evident_$(date +%Y%m%d_%H%M%S).dump

# Restore
pg_restore -d evident evident_20250115_120000.dump

# Evidence store (rsync to backup volume)
rsync -a --checksum /opt/evident/evidence_store/ /backup/evidence_store/
```

---

## 12. Security Checklist

- [ ] `SECRET_KEY` is a unique, random 64-character hex string
- [ ] `FLASK_ENV=production` is set
- [ ] `SESSION_COOKIE_SECURE=true`
- [ ] TLS certificate is valid and auto-renewed
- [ ] Database password is strong and unique
- [ ] `.env` file permissions are `600`
- [ ] Firewall allows only ports 80/443 externally
- [ ] Gunicorn binds to `127.0.0.1:8000` (nginx proxies)
- [ ] `FORWARDED_ALLOW_IPS` is set to `127.0.0.1`
- [ ] Redis (if used) is bound to localhost only
- [ ] Backups run on schedule and are tested periodically

---

## 13. Monitoring

### Recommended Stack

- **Metrics**: Prometheus + Grafana (scrape `/health/info`)
- **Logs**: JSON stdout → journald → log aggregator
- **Alerts**: `/health/ready` returning 503 triggers page

### Uptime Probes

Point an external monitor (UptimeRobot, Pingdom, etc.) at:

```
https://evident.example.com/health/live
```

Expected response: `{"status": "ok", ...}` with HTTP 200.

---

## 14. Operational Runbook

### Restart Application

```bash
sudo systemctl restart evident
```

### View Logs

```bash
sudo journalctl -u evident -f --output=cat
```

### Roll Back a Deployment

```bash
cd /opt/evident
sudo -u evident git checkout <previous-tag>
sudo -u evident venv/bin/pip install -r _backend/requirements.txt
sudo -u evident FLASK_ENV=production venv/bin/flask db upgrade
sudo systemctl restart evident
```

### Emergency: Database Migration Rollback

```bash
sudo -u evident FLASK_ENV=production venv/bin/flask db downgrade -1
```
