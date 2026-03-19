import json
import re
from datetime import datetime, timezone
from io import BytesIO

from config.settings import (
    CLEAN_BUCKET,
    CURATED_BUCKET,
    DATA_LAKE_ACCESS_KEY,
    DATA_LAKE_ENABLED,
    DATA_LAKE_ENDPOINT,
    DATA_LAKE_SECRET_KEY,
    DATA_LAKE_SECURE,
    RAW_BUCKET,
)

try:
    from minio import Minio
    from minio.error import S3Error
except Exception:
    Minio = None

    class S3Error(Exception):
        pass


_client = (
    Minio(
        DATA_LAKE_ENDPOINT,
        access_key=DATA_LAKE_ACCESS_KEY,
        secret_key=DATA_LAKE_SECRET_KEY,
        secure=DATA_LAKE_SECURE,
    )
    if Minio is not None
    else None
)


def _ensure_bucket_exists(bucket_name: str) -> None:
    if _client is None:
        return
    if not _client.bucket_exists(bucket_name):
        _client.make_bucket(bucket_name)


def initialize_data_lake() -> dict:
    if not DATA_LAKE_ENABLED:
        return {"enabled": False, "created": []}

    if _client is None:
        return {"enabled": True, "created": [], "error": "minio-client-unavailable"}

    created = []
    try:
        for bucket_name in [RAW_BUCKET, CLEAN_BUCKET, CURATED_BUCKET]:
            if not _client.bucket_exists(bucket_name):
                _client.make_bucket(bucket_name)
                created.append(bucket_name)
        return {"enabled": True, "created": created}
    except S3Error as err:
        return {"enabled": True, "created": created, "error": str(err)}


def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """
    Parse une URI de la forme `s3://bucket/object/path.json` en (bucket, object_name).
    """
    if not s3_uri or not isinstance(s3_uri, str):
        raise ValueError("URI S3 invalide.")
    if not s3_uri.startswith("s3://"):
        raise ValueError("URI S3 invalide (attendu: s3://...).")

    remainder = s3_uri[len("s3://") :]
    bucket_name, _, object_name = remainder.partition("/")
    if not bucket_name or not object_name:
        raise ValueError("URI S3 invalide (bucket et object_name requis).")
    return bucket_name, object_name


def object_exists(s3_uri: str) -> bool:
    """
    Vérifie l'existence d'un objet dans Minio.

    Retourne `True` si Minio est désactivé (skip). Sinon, tente un `stat_object`.
    """
    if not DATA_LAKE_ENABLED:
        return True
    if _client is None:
        return False
    if not s3_uri:
        return False

    try:
        bucket_name, object_name = parse_s3_uri(s3_uri)
    except ValueError:
        return False

    try:
        _client.stat_object(bucket_name, object_name)
        return True
    except S3Error:
        return False


def _safe_filename(filename: str | None) -> str:
    if not filename:
        return "document.pdf"
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    return cleaned or "document.pdf"


def _dated_prefix() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}/{now.month:02d}/{now.day:02d}"


def _put_bytes(bucket_name: str, object_name: str, payload: bytes, content_type: str) -> str | None:
    if not DATA_LAKE_ENABLED or _client is None:
        return None

    try:
        _ensure_bucket_exists(bucket_name)
        _client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=BytesIO(payload),
            length=len(payload),
            content_type=content_type,
        )
        return f"s3://{bucket_name}/{object_name}"
    except S3Error:
        return None


def save_raw_document(file_bytes: bytes, filename: str | None, doc_id: str) -> str | None:
    safe_name = _safe_filename(filename)
    object_name = f"{_dated_prefix()}/{doc_id}/{safe_name}"
    return _put_bytes(RAW_BUCKET, object_name, file_bytes, "application/pdf")


def save_clean_text(doc_id: str, source_filename: str | None, ocr_text: str, metadata: dict) -> str | None:
    safe_name = _safe_filename(source_filename)
    payload = {
        "doc_id": doc_id,
        "source_file": safe_name,
        "ocr_text": ocr_text,
        "metadata": metadata,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    object_name = f"{_dated_prefix()}/{doc_id}/ocr.json"
    return _put_bytes(
        CLEAN_BUCKET,
        object_name,
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        "application/json",
    )


def save_curated_record(doc_id: str, curated_payload: dict) -> str | None:
    object_name = f"{_dated_prefix()}/{doc_id}/record.json"
    return _put_bytes(
        CURATED_BUCKET,
        object_name,
        json.dumps(curated_payload, ensure_ascii=False).encode("utf-8"),
        "application/json",
    )
