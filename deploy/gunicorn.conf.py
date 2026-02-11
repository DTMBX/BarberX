"""
Gunicorn Production Configuration
===================================
Usage:
    gunicorn -c deploy/gunicorn.conf.py wsgi:app

Environment variables (all optional — sane defaults provided):
    GUNICORN_WORKERS   — number of worker processes  (default: CPU×2+1)
    GUNICORN_THREADS   — threads per worker           (default: 2)
    GUNICORN_BIND      — bind address                  (default: 0.0.0.0:8000)
    GUNICORN_TIMEOUT   — worker timeout in seconds     (default: 120)
    GUNICORN_LOG_LEVEL — log level                     (default: info)
"""

import multiprocessing
import os

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------
# Sync workers are the safest default for SQLAlchemy + SQLite.
# Switch to gevent/uvicorn for async workloads.
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get("GUNICORN_THREADS", 2))
worker_class = "sync"

# ---------------------------------------------------------------------------
# Timeouts
# ---------------------------------------------------------------------------
# 120 s accommodates large BWC file uploads and integrity-statement generation.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))
graceful_timeout = 30
keepalive = 5

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# Limit request sizes to match Flask MAX_CONTENT_LENGTH (3 GB)
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"  # stdout — let container/systemd capture
errorlog = "-"   # stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ---------------------------------------------------------------------------
# Forwarded headers (trust nginx reverse proxy only)
# ---------------------------------------------------------------------------
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
proxy_protocol = False

# ---------------------------------------------------------------------------
# Process naming
# ---------------------------------------------------------------------------
proc_name = "evident"

# ---------------------------------------------------------------------------
# Server hooks
# ---------------------------------------------------------------------------
def on_starting(server):
    """Log server start."""
    server.log.info("Evident starting — workers=%d, bind=%s", workers, bind)


def post_worker_init(worker):
    """Log worker initialisation."""
    worker.log.info("Worker %s initialised (pid=%s)", worker.age, worker.pid)
