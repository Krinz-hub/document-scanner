"""Storage module supporting MinIO / S3 and local file fallback."""

import os
import boto3
from botocore.exceptions import ClientError
from backend.app.config import get_settings
from backend.app.logging import setup_logging

settings = get_settings()

LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


class StorageManager:
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.bucket = settings.STORAGE_BUCKET_DOCUMENTS
        self._s3_client = None

        if self.provider in ("minio", "s3"):
            try:
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.STORAGE_ENDPOINT if self.provider == "minio" else None,
                    aws_access_key_id=settings.STORAGE_ACCESS_KEY,
                    aws_secret_access_key=settings.STORAGE_SECRET_KEY,
                    region_name="us-east-1",
                )
                self._ensure_bucket()
            except Exception:
                # Fallback to local storage if MinIO is unreachable
                self.provider = "local"

    def _ensure_bucket(self):
        if not self._s3_client:
            return
        try:
            self._s3_client.head_bucket(Bucket=self.bucket)
        except ClientError:
            try:
                self._s3_client.create_bucket(Bucket=self.bucket)
            except Exception:
                pass

    def save_file(self, file_bytes: bytes, object_key: str, content_type: str = "image/jpeg") -> str:
        """Save file bytes and return object reference string."""
        if self.provider in ("minio", "s3") and self._s3_client:
            try:
                self._s3_client.put_object(
                    Bucket=self.bucket,
                    Key=object_key,
                    Body=file_bytes,
                    ContentType=content_type,
                )
                return f"s3://{self.bucket}/{object_key}"
            except Exception:
                # Fallback to local on upload error
                pass

        # Local storage fallback
        local_path = os.path.join(LOCAL_STORAGE_DIR, object_key.replace("/", "_"))
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        return f"local://{object_key}"

    def get_file(self, object_ref: str) -> bytes:
        """Retrieve file bytes by object reference."""
        if object_ref.startswith("s3://") and self._s3_client:
            # Extract key from s3://bucket/key
            parts = object_ref.replace("s3://", "").split("/", 1)
            if len(parts) == 2:
                bucket, key = parts
                response = self._s3_client.get_object(Bucket=bucket, Key=key)
                return response["Body"].read()

        # Local fallback
        key = object_ref.replace("local://", "").replace("/", "_")
        local_path = os.path.join(LOCAL_STORAGE_DIR, key)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"Object {object_ref} not found")


storage_manager = StorageManager()
