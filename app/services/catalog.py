from __future__ import annotations

import hashlib
import json
import uuid
from decimal import Decimal
from typing import Iterable

from ..db import connect, fetch_all, utc_now
from ..schemas import ProductImport


def _hash_product(item: ProductImport) -> str:
    payload = item.model_dump(mode="json")
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def import_products(items: Iterable[ProductImport]) -> dict:
    started = utc_now()
    run_id = str(uuid.uuid4())
    accepted = 0
    with connect() as connection:
        connection.execute(
            "INSERT INTO catalog_sync_runs VALUES (?, ?, NULL, 'running', '{}', NULL)",
            (run_id, started),
        )
        for item in items:
            product_hash = _hash_product(item)
            existing = connection.execute("SELECT id FROM products WHERE source_id = ?", (item.source_id,)).fetchone()
            product_id = existing["id"] if existing else str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO products (id, source_id, name, category, description, base_price, currency, image_url, kyte_url,
                                      variants_json, published, source_hash, last_synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    name=excluded.name, category=excluded.category, description=excluded.description,
                    base_price=excluded.base_price, currency=excluded.currency, image_url=excluded.image_url,
                    kyte_url=excluded.kyte_url, variants_json=excluded.variants_json, published=excluded.published,
                    source_hash=excluded.source_hash, last_synced_at=excluded.last_synced_at
                """,
                (
                    product_id,
                    item.source_id,
                    item.name,
                    item.category,
                    item.description,
                    str(item.base_price),
                    item.currency,
                    str(item.image_url) if item.image_url else None,
                    str(item.product_url),
                    json.dumps(item.variants, ensure_ascii=False),
                    int(item.published),
                    product_hash,
                    item.source_updated_at.isoformat(),
                ),
            )
            accepted += 1
        finished = utc_now()
        counters = json.dumps({"accepted": accepted, "rejected": 0})
        connection.execute(
            "UPDATE catalog_sync_runs SET finished_at=?, status='completed', counters_json=? WHERE id=?",
            (finished, counters, run_id),
        )
    return {"run_id": run_id, "accepted": accepted, "rejected": 0}


def list_products(query: str | None = None, category: str | None = None, limit: int = 20) -> list[dict]:
    clauses = ["published = 1"]
    params: list[object] = []
    if category:
        clauses.append("category = ?")
        params.append(category)
    if query:
        clauses.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ?)")
        term = f"%{query.lower()}%"
        params.extend([term, term])
    params.append(min(max(limit, 1), 50))
    rows = fetch_all(
        f"SELECT * FROM products WHERE {' AND '.join(clauses)} ORDER BY name LIMIT ?",
        params,
    )
    for row in rows:
        row["variants"] = json.loads(row.pop("variants_json"))
        row["base_price"] = str(Decimal(row["base_price"]))
        row["published"] = bool(row["published"])
    return rows

