"""
Structured JSON Logging
========================
Configures Python's logging to emit JSON-structured log lines suitable
for production log aggregators (CloudWatch, Datadog, ELK, etc.).

Usage:
    from services.structured_logging import init_logging
    init_logging(app)

Each log line contains:
  - timestamp (ISO-8601 UTC)
  - level
  - logger (module name)
  - message
  - request_id (if inside a Flask request context)
  - method / path / remote_addr (if inside a Flask request context)

Design choice: deterministic, no third-party logging libraries.
Uses stdlib ``logging`` with a custom ``Formatter``.
"""

import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

from flask import Flask, g, has_request_context, request


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach request context when available
        if has_request_context():
            payload["request_id"] = getattr(g, "request_id", None)
            payload["method"] = request.method
            payload["path"] = request.path
            payload["remote_addr"] = request.remote_addr

        # Attach exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def _assign_request_id() -> None:
    """Assign a unique request_id at the start of every request."""
    g.request_id = uuid.uuid4().hex


def _log_request_start() -> None:
    """Log the beginning of each request."""
    logger = logging.getLogger("evident.http")
    logger.info(
        "request_start %s %s",
        request.method,
        request.path,
    )


def _log_request_end(response):
    """Log the end of each request with status code."""
    logger = logging.getLogger("evident.http")
    logger.info(
        "request_end %s %s status=%d",
        request.method,
        request.path,
        response.status_code,
    )
    # Propagate request_id in response header for traceability
    request_id = getattr(g, "request_id", None)
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response


def init_logging(app: Flask, *, level: Optional[str] = None) -> None:
    """
    Attach structured JSON logging to the Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application instance.
    level : str, optional
        Override log level (DEBUG, INFO, WARNING, ERROR).
        Defaults to INFO in production, DEBUG otherwise.
    """
    env = os.environ.get("FLASK_ENV", "development")
    is_production = env == "production"

    if level is None:
        level = "INFO" if is_production else "DEBUG"

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicate output
    for handler in root.handlers[:]:
        root.handlers.remove(handler)

    handler = logging.StreamHandler(sys.stdout)

    if is_production:
        handler.setFormatter(_JSONFormatter())
    else:
        # Human-readable format for development
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(handler)

    # Flask request lifecycle hooks
    app.before_request(_assign_request_id)
    app.before_request(_log_request_start)
    app.after_request(_log_request_end)

    logging.getLogger("evident").info(
        "Structured logging initialised (level=%s, json=%s)",
        level,
        is_production,
    )
