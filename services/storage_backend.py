"""
Storage Backend Abstraction
============================
Defines a uniform interface for evidence file storage, with pluggable backends.

Backends:
  - LocalFSStore: local filesystem (default, development, single-node).
  - S3Store: AWS S3 / S3-compatible (production, multi-node, BWC scale).

Design principles:
  - Originals are NEVER overwritten (immutable storage).
  - Every write is verified by SHA-256 digest comparison.
  - All backends expose the same interface — callers never know which is active.
  - The backend is selected by configuration, not by import.
"""

import abc
import hashlib
import io
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Optional

logger = logging.getLogger(__name__)

HASH_BLOCK_SIZE = 1 << 16  # 64 KiB


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StorePutResult:
    """Result of a put (write) operation."""

    success: bool
    key: str              # canonical key in the store
    sha256: str           # verified SHA-256 of stored content
    size_bytes: int
    error: Optional[str] = None


@dataclass(frozen=True)
class StoreGetResult:
    """Result of a get (read) operation."""

    success: bool
    data: Optional[bytes] = None
    sha256: Optional[str] = None
    size_bytes: int = 0
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------


class StorageBackend(abc.ABC):
    """
    Uniform interface for evidence file storage.

    Keys are slash-delimited paths relative to the store root
    (e.g., ``originals/a1b2/a1b2c3d4.../video.mp4``).
    """

    @abc.abstractmethod
    def put(self, key: str, data: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        """
        Write data to the store under the given key.

        If expected_sha256 is provided, the stored data must match. On mismatch,
        the write is rolled back and an error is returned.
        """

    @abc.abstractmethod
    def get(self, key: str) -> StoreGetResult:
        """Read the full content at the given key."""

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """Return True if the key exists in the store."""

    @abc.abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete the key. Returns True if deleted, False if not found.

        WARNING: This exists for administrative cleanup only. Production
        evidence stores should NEVER delete originals.
        """

    @abc.abstractmethod
    def list_keys(self, prefix: str = "") -> list:
        """Return all keys under the given prefix."""

    @abc.abstractmethod
    def get_stream(self, key: str) -> Optional[BinaryIO]:
        """Return a readable binary stream for the key, or None."""

    @abc.abstractmethod
    def put_stream(self, key: str, stream: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        """
        Write a stream to the store. Like put(), but does not require loading
        the full content into memory. Essential for multi-GB files.
        """

    @abc.abstractmethod
    def size(self, key: str) -> Optional[int]:
        """Return the size in bytes, or None if key does not exist."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hash_stream(stream: BinaryIO) -> tuple:
    """Hash a stream, returning (sha256_hex, size_bytes, bytes_read_list)."""
    h = hashlib.sha256()
    size = 0
    chunks = []
    while True:
        chunk = stream.read(HASH_BLOCK_SIZE)
        if not chunk:
            break
        h.update(chunk)
        size += len(chunk)
        chunks.append(chunk)
    return h.hexdigest(), size, chunks


# ---------------------------------------------------------------------------
# LocalFSStore
# ---------------------------------------------------------------------------


class LocalFSStore(StorageBackend):
    """
    Filesystem-backed storage.

    Root directory is created on init. All keys are resolved relative to root.
    """

    def __init__(self, root: str = "evidence_store"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("LocalFSStore initialized at %s", self.root)

    def _resolve(self, key: str) -> Path:
        # Prevent directory traversal
        resolved = (self.root / key).resolve()
        if not str(resolved).startswith(str(self.root)):
            raise ValueError(f"Key escapes store root: {key}")
        return resolved

    def put(self, key: str, data: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        return self.put_stream(key, data, expected_sha256)

    def put_stream(self, key: str, stream: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        h = hashlib.sha256()
        size = 0
        tmp = path.with_suffix(".tmp")

        try:
            with open(tmp, "wb") as f:
                while True:
                    chunk = stream.read(HASH_BLOCK_SIZE)
                    if not chunk:
                        break
                    h.update(chunk)
                    f.write(chunk)
                    size += len(chunk)

            actual_sha256 = h.hexdigest()

            if expected_sha256 and actual_sha256 != expected_sha256:
                tmp.unlink(missing_ok=True)
                return StorePutResult(
                    success=False,
                    key=key,
                    sha256=actual_sha256,
                    size_bytes=size,
                    error=f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}",
                )

            # Atomic rename (as close as OS allows)
            if path.exists():
                tmp.unlink(missing_ok=True)
                return StorePutResult(
                    success=False,
                    key=key,
                    sha256=actual_sha256,
                    size_bytes=size,
                    error=f"Key already exists (immutability enforced): {key}",
                )

            tmp.rename(path)

            return StorePutResult(
                success=True,
                key=key,
                sha256=actual_sha256,
                size_bytes=size,
            )

        except Exception as exc:
            tmp.unlink(missing_ok=True)
            return StorePutResult(
                success=False,
                key=key,
                sha256="",
                size_bytes=0,
                error=str(exc),
            )

    def get(self, key: str) -> StoreGetResult:
        path = self._resolve(key)
        if not path.exists():
            return StoreGetResult(success=False, error=f"Not found: {key}")
        data = path.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        return StoreGetResult(
            success=True, data=data, sha256=sha256, size_bytes=len(data)
        )

    def get_stream(self, key: str) -> Optional[BinaryIO]:
        path = self._resolve(key)
        if not path.exists():
            return None
        return open(path, "rb")

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    def delete(self, key: str) -> bool:
        path = self._resolve(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_keys(self, prefix: str = "") -> list:
        base = self._resolve(prefix) if prefix else self.root
        if not base.exists():
            return []
        results = []
        for p in sorted(base.rglob("*")):
            if p.is_file():
                results.append(str(p.relative_to(self.root)).replace("\\", "/"))
        return results

    def size(self, key: str) -> Optional[int]:
        path = self._resolve(key)
        return path.stat().st_size if path.exists() else None


# ---------------------------------------------------------------------------
# S3Store
# ---------------------------------------------------------------------------


class S3Store(StorageBackend):
    """
    AWS S3 (or S3-compatible) storage backend.

    Requires ``boto3`` installed and configured (env vars or AWS profiles).

    Constructor args:
        bucket: S3 bucket name.
        prefix: Optional key prefix (e.g., "evidence/").
        region: AWS region (default: from env).
        endpoint_url: For S3-compatible stores (MinIO, R2, etc.).
    """

    def __init__(
        self,
        bucket: str,
        prefix: str = "",
        region: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3Store. Install: pip install boto3"
            )

        self.bucket = bucket
        self.prefix = prefix.rstrip("/") + "/" if prefix else ""

        kwargs = {}
        if region:
            kwargs["region_name"] = region
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url

        self._s3 = boto3.client("s3", **kwargs)
        logger.info(
            "S3Store initialized: bucket=%s, prefix=%s", bucket, self.prefix
        )

    def _full_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def put(self, key: str, data: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        return self.put_stream(key, data, expected_sha256)

    def put_stream(self, key: str, stream: BinaryIO, expected_sha256: Optional[str] = None) -> StorePutResult:
        full_key = self._full_key(key)

        # Hash while reading
        h = hashlib.sha256()
        buf = io.BytesIO()
        size = 0
        while True:
            chunk = stream.read(HASH_BLOCK_SIZE)
            if not chunk:
                break
            h.update(chunk)
            buf.write(chunk)
            size += len(chunk)

        actual_sha256 = h.hexdigest()

        if expected_sha256 and actual_sha256 != expected_sha256:
            return StorePutResult(
                success=False,
                key=key,
                sha256=actual_sha256,
                size_bytes=size,
                error=f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}",
            )

        # Check immutability
        try:
            self._s3.head_object(Bucket=self.bucket, Key=full_key)
            return StorePutResult(
                success=False,
                key=key,
                sha256=actual_sha256,
                size_bytes=size,
                error=f"Key already exists (immutability enforced): {key}",
            )
        except self._s3.exceptions.ClientError:
            pass  # Expected — key does not exist

        buf.seek(0)
        try:
            self._s3.upload_fileobj(
                buf,
                self.bucket,
                full_key,
                ExtraArgs={"Metadata": {"sha256": actual_sha256}},
            )
        except Exception as exc:
            return StorePutResult(
                success=False,
                key=key,
                sha256=actual_sha256,
                size_bytes=size,
                error=str(exc),
            )

        return StorePutResult(
            success=True, key=key, sha256=actual_sha256, size_bytes=size
        )

    def get(self, key: str) -> StoreGetResult:
        full_key = self._full_key(key)
        try:
            resp = self._s3.get_object(Bucket=self.bucket, Key=full_key)
            data = resp["Body"].read()
            sha256 = hashlib.sha256(data).hexdigest()
            return StoreGetResult(
                success=True, data=data, sha256=sha256, size_bytes=len(data)
            )
        except Exception as exc:
            return StoreGetResult(success=False, error=str(exc))

    def get_stream(self, key: str) -> Optional[BinaryIO]:
        full_key = self._full_key(key)
        try:
            resp = self._s3.get_object(Bucket=self.bucket, Key=full_key)
            return resp["Body"]
        except Exception:
            return None

    def exists(self, key: str) -> bool:
        full_key = self._full_key(key)
        try:
            self._s3.head_object(Bucket=self.bucket, Key=full_key)
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        full_key = self._full_key(key)
        try:
            self._s3.delete_object(Bucket=self.bucket, Key=full_key)
            return True
        except Exception:
            return False

    def list_keys(self, prefix: str = "") -> list:
        full_prefix = self._full_key(prefix)
        results = []
        paginator = self._s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
            for obj in page.get("Contents", []):
                # Strip the store prefix to return relative keys
                key = obj["Key"]
                if self.prefix and key.startswith(self.prefix):
                    key = key[len(self.prefix):]
                results.append(key)
        return results

    def size(self, key: str) -> Optional[int]:
        full_key = self._full_key(key)
        try:
            resp = self._s3.head_object(Bucket=self.bucket, Key=full_key)
            return resp["ContentLength"]
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_storage_backend(config: Optional[dict] = None) -> StorageBackend:
    """
    Create a storage backend from configuration.

    Config keys (from app.config or dict):
        STORAGE_BACKEND: "local" (default) or "s3"
        STORAGE_ROOT: filesystem path (for local)
        S3_BUCKET: bucket name (for s3)
        S3_PREFIX: key prefix (for s3)
        S3_REGION: AWS region (for s3)
        S3_ENDPOINT_URL: endpoint (for S3-compatible stores)
    """
    if config is None:
        config = {}

    backend = config.get("STORAGE_BACKEND", "local").lower()

    if backend == "s3":
        bucket = config.get("S3_BUCKET")
        if not bucket:
            raise ValueError("S3_BUCKET is required for S3 storage backend")
        return S3Store(
            bucket=bucket,
            prefix=config.get("S3_PREFIX", ""),
            region=config.get("S3_REGION"),
            endpoint_url=config.get("S3_ENDPOINT_URL"),
        )

    # Default: local filesystem
    root = config.get("STORAGE_ROOT", "evidence_store")
    return LocalFSStore(root=root)
