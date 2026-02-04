"""
Production Performance Optimizations
Caching, compression, and request optimization utilities
"""

import gzip
import hashlib
import io
import json
import time
from functools import wraps
from typing import Any, Dict, Optional

from flask import g, make_response, request


def add_cache_headers(max_age=3600):
    """Decorator to add cache headers to responses"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers["Cache-Control"] = f"public, max-age={max_age}"
            return response

        return decorated_function

    return decorator


def compress_response(f):
    """Decorator to add gzip compression to responses"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))

        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response

        # Skip if response is too small or already compressed
        if len(response.data) < 500 or response.headers.get("Content-Encoding"):
            return response

        # Compress response
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(response.data)

        response.data = gzip_buffer.getvalue()
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = len(response.data)

        return response

    return decorated_function


def add_request_id(f):
    """Add unique request ID for tracking"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.request_id = hashlib.md5(f"{time.time()}{id(request)}".encode()).hexdigest()[:12]
        return f(*args, **kwargs)

    return decorated_function


def add_timing_headers(f):
    """Add server timing headers for performance monitoring"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        response = make_response(f(*args, **kwargs))
        elapsed = (time.time() - start_time) * 1000
        response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
        return response

    return decorated_function


class SimpleCache:
    """Simple in-memory cache with TTL"""

    def __init__(self, default_ttl=300):
        self.cache = {}
        self.default_ttl = default_ttl

    def get(self, key):
        """Get value from cache"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value, ttl=None):
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)

    def delete(self, key):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()

    def cleanup(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [k for k, (v, exp) in self.cache.items() if now >= exp]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)


# Global cache instance
simple_cache = SimpleCache(default_ttl=300)


def cached(ttl=300, key_prefix=None):
    """Decorator to cache function results"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or f.__name__]
            cache_key_parts.extend(str(arg) for arg in args)
            cache_key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(cache_key_parts).encode()).hexdigest()

            # Try to get from cache
            result = simple_cache.get(cache_key)
            if result is not None:
                return result

            # Execute function
            result = f(*args, **kwargs)

            # Cache result
            simple_cache.set(cache_key, result, ttl=ttl)
            return result

        return decorated_function

    return decorator


def paginated_query(query, page=1, per_page=20, max_per_page=100):
    """
    Paginate SQLAlchemy query efficiently

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum allowed items per page

    Returns:
        dict with items, total, page, pages, has_next, has_prev
    """
    # Validate and cap per_page
    per_page = min(per_page, max_per_page)

    # Calculate total count (cached for same query)
    total = query.count()

    # Calculate pages
    pages = (total + per_page - 1) // per_page
    page = max(1, min(page, pages)) if pages > 0 else 1

    # Get items with offset/limit
    offset = (page - 1) * per_page
    items = query.limit(per_page).offset(offset).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }


def stream_file_hash(file_path, chunk_size=8192):
    """
    Calculate file hash in chunks to avoid loading entire file into memory

    Args:
        file_path: Path to file
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        SHA-256 hash hexdigest
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def batch_query(model, ids, batch_size=100):
    """
    Query records in batches to avoid loading too many at once

    Args:
        model: SQLAlchemy model class
        ids: List of IDs to query
        batch_size: Number of records per batch

    Yields:
        Batches of records
    """
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i : i + batch_size]
        yield model.query.filter(model.id.in_(batch_ids)).all()


def jsonify_optimized(data, indent=None):
    """
    Optimized JSON serialization

    Args:
        data: Data to serialize
        indent: Indentation (None for production, 2 for dev)

    Returns:
        JSON response
    """
    from flask import jsonify

    # Use compact separators in production
    if indent is None:
        import json

        response = make_response(json.dumps(data, separators=(",", ":")))
        response.headers["Content-Type"] = "application/json"
        return response

    return jsonify(data)


