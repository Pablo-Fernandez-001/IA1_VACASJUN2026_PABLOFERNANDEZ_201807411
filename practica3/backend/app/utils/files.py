import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def safe_upload_path(upload_dir: str, upload: UploadFile) -> Path:
    return safe_storage_path(upload_dir, upload.filename or "factura")


def safe_storage_path(upload_dir: str, original: str) -> Path:
    extension = Path(original).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato no permitido. Use PDF, JPG, JPEG o PNG.")
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", Path(original).stem).strip("_") or "factura"
    target_dir = Path(upload_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{stem}_{uuid.uuid4().hex[:10]}{extension}"
