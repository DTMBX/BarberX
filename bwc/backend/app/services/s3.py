"""S3/MinIO client — ensure bucket exists, presign URLs, download objects."""

from __future__ import annotations

import logging

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_s3_client():
    """Return a singleton boto3 S3 client pointed at MinIO."""
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=BotoConfig(
                signature_version="s3v4",
                connect_timeout=5,
                read_timeout=5,
                retries={"max_attempts": 1},
            ),
        )
    return _client


def ensure_bucket(bucket: str | None = None) -> None:
    """Create the evidence bucket if it does not exist, then apply immutable policy."""
    bucket = bucket or settings.s3_bucket
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket)
        logger.info("Bucket '%s' already exists.", bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)
        logger.info("Created bucket '%s'.", bucket)

    # Apply WORM-like policy: deny s3:DeleteObject on all keys
    if settings.s3_immutable_policy:
        _apply_immutable_policy(bucket)


def _apply_immutable_policy(bucket: str) -> None:
    """Apply a deny-delete bucket policy (WORM-like write-once behavior)."""
    import json

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyDeleteObject",
                "Effect": "Deny",
                "Principal": "*",
                "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            },
            {
                "Sid": "AllowReadWrite",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket}",
                    f"arn:aws:s3:::{bucket}/*",
                ],
            },
        ],
    }
    s3 = get_s3_client()
    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
    logger.info("Applied immutable (deny-delete) policy to bucket '%s'.", bucket)


def presigned_put_url(key: str, content_type: str, expires: int = 3600) -> str:
    """Generate a presigned PUT URL for uploading to MinIO."""
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires,
    )


def download_bytes(key: str) -> bytes:
    """Download an object's full body as bytes."""
    s3 = get_s3_client()
    resp = s3.get_object(Bucket=settings.s3_bucket, Key=key)
    return resp["Body"].read()
