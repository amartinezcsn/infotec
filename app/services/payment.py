from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from ..db import connect, fetch_one, utc_now
from ..settings import UPLOAD_DIR, ensure_runtime_dirs


ALLOWED_SIGNATURES = {
    b"%PDF": "application/pdf",
    b"\x89PNG": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


def _detect_type(content: bytes) -> str | None:
    for signature, mime in ALLOWED_SIGNATURES.items():
        if content.startswith(signature):
            return mime
    return None


def save_and_analyze(request_id: str, file_name: str, content: bytes) -> dict:
    ensure_runtime_dirs()
    if len(content) > 8 * 1024 * 1024:
        raise ValueError("El archivo excede 8 MB")
    mime = _detect_type(content)
    if not mime:
        raise ValueError("Solo se aceptan PDF, PNG o JPG válidos")
    digest = hashlib.sha256(content).hexdigest()
    duplicate = fetch_one("SELECT id FROM payment_proofs WHERE file_hash = ?", (digest,))
    proof_id = str(uuid.uuid4())
    safe_path = UPLOAD_DIR / f"{proof_id}{Path(file_name).suffix.lower()}"
    safe_path.write_bytes(content)
    extracted = {
        "adapter": "local_safe_fallback",
        "fields": {"transaction_date": None, "amount": None, "currency": None, "reference": None, "institution": None},
        "confidence": {},
        "note": "Document Intelligence no está configurado; se requiere revisión humana.",
    }
    status = "duplicate_suspected" if duplicate else "low_confidence"
    with connect() as connection:
        connection.execute(
            "INSERT INTO payment_proofs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (proof_id, request_id, file_name, str(safe_path), digest, json.dumps(extracted, ensure_ascii=False), 1.0 if duplicate else 0.0, status, utc_now()),
        )
        task_id = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO human_tasks VALUES (?, 'payment_review', ?, 'high', 'open', ?, NULL, ?, NULL)",
            (task_id, proof_id, f"Revisar comprobante {file_name}: {status}", utc_now()),
        )
    return {
        "document_id": proof_id,
        "file_hash": digest,
        "mime_type": mime,
        "extracted_fields": extracted["fields"],
        "confidence": extracted["confidence"],
        "duplicate_signals": {"hash_match": bool(duplicate), "matching_document_id": duplicate["id"] if duplicate else None},
        "preliminary_status": status,
        "requires_human_review": True,
        "human_task_id": task_id,
    }

