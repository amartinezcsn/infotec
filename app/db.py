from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .settings import DB_PATH, ensure_runtime_dirs


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    base_price TEXT NOT NULL,
    currency TEXT NOT NULL,
    image_url TEXT,
    kyte_url TEXT NOT NULL,
    variants_json TEXT NOT NULL DEFAULT '[]',
    published INTEGER NOT NULL DEFAULT 1,
    source_hash TEXT NOT NULL,
    last_synced_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS catalog_sync_runs (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    counters_json TEXT NOT NULL,
    error_summary TEXT
);

CREATE TABLE IF NOT EXISTS order_requests (
    id TEXT PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    product_id TEXT NOT NULL REFERENCES products(id),
    requirements_json TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    fulfillment_mode TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capacity_slots (
    slot_date TEXT PRIMARY KEY,
    capacity_minutes INTEGER NOT NULL,
    reserved_minutes INTEGER NOT NULL DEFAULT 0,
    blocked INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS availability_reviews (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES order_requests(id),
    decision TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    comment TEXT,
    alternative_at TEXT,
    decided_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quotes (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES order_requests(id),
    version INTEGER NOT NULL,
    base_amount TEXT NOT NULL,
    adjustments_json TEXT NOT NULL,
    total TEXT NOT NULL,
    status TEXT NOT NULL,
    approved_by TEXT,
    valid_until TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_proofs (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES order_requests(id),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    extracted_json TEXT NOT NULL,
    duplicate_score REAL NOT NULL,
    review_status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS human_tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    related_id TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT NOT NULL,
    assignee_id TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    actor_type TEXT NOT NULL,
    content TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: Path | None = None) -> sqlite3.Connection:
    ensure_runtime_dirs()
    connection = sqlite3.connect(path or DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with connect() as connection:
        connection.executescript(SCHEMA)


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    with connect() as connection:
        return [dict(row) for row in connection.execute(query, tuple(params)).fetchall()]


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    with connect() as connection:
        row = connection.execute(query, tuple(params)).fetchone()
        return dict(row) if row else None


def audit(actor: str, action: str, resource_type: str, resource_id: str, details: dict[str, Any], correlation_id: str) -> None:
    import uuid

    with connect() as connection:
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), actor, action, resource_type, resource_id, json.dumps(details, ensure_ascii=False), correlation_id, utc_now()),
        )

