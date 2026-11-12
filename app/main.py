from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import audit, connect, fetch_all, fetch_one, init_db, utc_now
from .schemas import AvailabilityReview, CalendarBlock, CapacityCheck, ChatMessage, OrderRequestCreate, ProductImport, QuoteCreate
from .services.agent import respond
from .services.capacity import check_tentative_capacity
from .services.catalog import import_products, list_products
from .services.knowledge import search_delivery_knowledge
from .services.payment import save_and_analyze
from .services.state_machine import validate_transition
from .settings import DEMO_ADMIN_TOKEN, ROOT


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_path = ROOT / "data" / "synthetic" / "catalog.json"
    if seed_path.exists() and not fetch_one("SELECT id FROM products LIMIT 1"):
        items = [ProductImport.model_validate(item) for item in json.loads(seed_path.read_text(encoding="utf-8"))]
        import_products(items)
    yield


app = FastAPI(
    title="CUP&CAKE AI",
    version="0.1.0",
    description="MVP de pedidos creativos con revisión humana",
    lifespan=lifespan,
)
STATIC_DIR = ROOT / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def require_staff(x_demo_admin: str | None = Header(default=None)) -> str:
    if x_demo_admin != DEMO_ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Se requiere un usuario de personal autorizado")
    return "demo-human-staff"


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "admin.html")


@app.get("/api/health")
def health() -> dict:
    return {"status": "healthy", "mode": "local-adapters"}


@app.get("/api/ready")
def ready() -> dict:
    init_db()
    return {"status": "ready"}


@app.get("/api/products")
def products(query: str | None = None, category: str | None = None, limit: int = Query(20, ge=1, le=50)) -> list[dict]:
    return list_products(query, category, limit)


@app.get("/api/products/{product_id}")
def product(product_id: str) -> dict:
    item = fetch_one("SELECT * FROM products WHERE id = ? AND published = 1", (product_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    item["variants"] = json.loads(item.pop("variants_json"))
    return item


@app.post("/api/catalog/import")
def catalog_import(items: list[ProductImport], staff: str = Depends(require_staff)) -> dict:
    result = import_products(items)
    audit(staff, "catalog_import", "catalog_sync_run", result["run_id"], result, str(uuid.uuid4()))
    return result


@app.get("/api/catalog/sync-runs")
def catalog_runs(staff: str = Depends(require_staff)) -> list[dict]:
    return fetch_all("SELECT * FROM catalog_sync_runs ORDER BY started_at DESC LIMIT 20")


@app.post("/api/chat/sessions")
def create_chat() -> dict:
    session_id = str(uuid.uuid4())
    with connect() as connection:
        connection.execute("INSERT INTO conversations VALUES (?, 'web', 'open', ?)", (session_id, utc_now()))
    return {"session_id": session_id, "channel": "web"}


@app.post("/api/chat/sessions/{session_id}/messages")
def chat_message(session_id: str, payload: ChatMessage) -> dict:
    if not fetch_one("SELECT id FROM conversations WHERE id = ?", (session_id,)):
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    correlation_id = str(uuid.uuid4())
    result = respond(payload.content)
    with connect() as connection:
        connection.execute("INSERT INTO messages VALUES (?, ?, 'customer', ?, ?, ?)", (str(uuid.uuid4()), session_id, payload.content, correlation_id, utc_now()))
        connection.execute("INSERT INTO messages VALUES (?, ?, 'agent', ?, ?, ?)", (str(uuid.uuid4()), session_id, result["answer"], correlation_id, utc_now()))
        if result.get("requires_human_review"):
            connection.execute(
                "INSERT INTO human_tasks VALUES (?, 'conversation_handoff', ?, 'medium', 'open', ?, NULL, ?, NULL)",
                (str(uuid.uuid4()), session_id, f"Revisar conversación: {result['intent']}", utc_now()),
            )
    return {"correlation_id": correlation_id, **result}


@app.post("/api/order-requests")
def create_order_request(payload: OrderRequestCreate) -> dict:
    existing = fetch_one("SELECT * FROM order_requests WHERE idempotency_key = ?", (payload.idempotency_key,))
    if existing:
        return existing
    if not fetch_one("SELECT id FROM products WHERE id = ? AND published = 1", (payload.product_id,)):
        raise HTTPException(status_code=400, detail="Producto no válido o no publicado")
    request_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    now = utc_now()
    requirements = payload.model_dump(mode="json")
    with connect() as connection:
        connection.execute(
            "INSERT INTO order_requests VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_availability_review', ?, ?)",
            (request_id, payload.idempotency_key, payload.customer_name, payload.product_id, json.dumps(requirements, ensure_ascii=False), payload.requested_at.isoformat(), payload.fulfillment_mode, now, now),
        )
        connection.execute(
            "INSERT INTO human_tasks VALUES (?, 'availability_review', ?, 'high', 'open', ?, NULL, ?, NULL)",
            (task_id, request_id, "Revisar fecha, complejidad, personal y precio base", now),
        )
    audit("customer", "order_request_created", "order_request", request_id, {"task_id": task_id}, request_id)
    return {"id": request_id, "status": "pending_availability_review", "human_task_id": task_id}


@app.get("/api/order-requests/{request_id}")
def get_order_request(request_id: str) -> dict:
    item = fetch_one("SELECT * FROM order_requests WHERE id = ?", (request_id,))
    if not item:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    item["requirements"] = json.loads(item.pop("requirements_json"))
    return item


@app.post("/api/order-requests/{request_id}/capacity-check")
def capacity_check(request_id: str, payload: CapacityCheck) -> dict:
    if not fetch_one("SELECT id FROM order_requests WHERE id = ?", (request_id,)):
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return check_tentative_capacity(payload.requested_at, payload.requested_minutes)


@app.post("/api/order-requests/{request_id}/availability-review")
def availability_review(request_id: str, payload: AvailabilityReview, staff: str = Depends(require_staff)) -> dict:
    request = fetch_one("SELECT * FROM order_requests WHERE id = ?", (request_id,))
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    valid, reason = validate_transition(request["status"], payload.decision, "human_staff")
    if not valid:
        raise HTTPException(status_code=409, detail=reason)
    review_id = str(uuid.uuid4())
    now = utc_now()
    with connect() as connection:
        connection.execute(
            "INSERT INTO availability_reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
            (review_id, request_id, payload.decision, payload.reviewer_id, payload.comment, payload.alternative_at.isoformat() if payload.alternative_at else None, now),
        )
        connection.execute("UPDATE order_requests SET status=?, updated_at=? WHERE id=?", (payload.decision, now, request_id))
        connection.execute("UPDATE human_tasks SET status='completed', completed_at=? WHERE related_id=? AND task_type='availability_review'", (now, request_id))
    audit(staff, "availability_reviewed", "order_request", request_id, payload.model_dump(mode="json"), review_id)
    return {"review_id": review_id, "request_id": request_id, "status": payload.decision}


@app.post("/api/order-requests/{request_id}/quotes")
def create_quote(request_id: str, payload: QuoteCreate, staff: str = Depends(require_staff)) -> dict:
    request = fetch_one("SELECT * FROM order_requests WHERE id = ?", (request_id,))
    if not request or request["status"] != "availability_approved":
        raise HTTPException(status_code=409, detail="La disponibilidad debe estar aprobada")
    quote_id = str(uuid.uuid4())
    version_row = fetch_one("SELECT COALESCE(MAX(version), 0) AS version FROM quotes WHERE request_id=?", (request_id,))
    version = int(version_row["version"]) + 1
    with connect() as connection:
        connection.execute(
            "INSERT INTO quotes VALUES (?, ?, ?, ?, ?, ?, 'quote_pending', NULL, ?, ?)",
            (quote_id, request_id, version, str(payload.base_amount), json.dumps(payload.adjustments, ensure_ascii=False), str(payload.total), payload.valid_until.isoformat() if payload.valid_until else None, utc_now()),
        )
        connection.execute("UPDATE order_requests SET status='quote_pending', updated_at=? WHERE id=?", (utc_now(), request_id))
    return {"quote_id": quote_id, "version": version, "status": "quote_pending", "requires_human_approval": True}


@app.post("/api/quotes/{quote_id}/approve")
def approve_quote(quote_id: str, staff: str = Depends(require_staff)) -> dict:
    quote = fetch_one("SELECT * FROM quotes WHERE id = ?", (quote_id,))
    if not quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    request = fetch_one("SELECT * FROM order_requests WHERE id = ?", (quote["request_id"],))
    valid, reason = validate_transition(request["status"], "quote_sent", "human_staff")
    if not valid:
        raise HTTPException(status_code=409, detail=reason)
    now = utc_now()
    with connect() as connection:
        connection.execute("UPDATE quotes SET status='quote_sent', approved_by=? WHERE id=?", (staff, quote_id))
        connection.execute("UPDATE order_requests SET status='quote_sent', updated_at=? WHERE id=?", (now, request["id"]))
    audit(staff, "quote_approved", "quote", quote_id, {"request_id": request["id"]}, quote_id)
    return {"quote_id": quote_id, "request_id": request["id"], "status": "quote_sent"}


@app.get("/api/calendar")
def calendar(staff: str = Depends(require_staff)) -> list[dict]:
    return fetch_all("SELECT * FROM capacity_slots ORDER BY slot_date")


@app.post("/api/calendar/blocks")
def upsert_calendar(payload: CalendarBlock, staff: str = Depends(require_staff)) -> dict:
    with connect() as connection:
        connection.execute(
            "INSERT INTO capacity_slots VALUES (?, ?, ?, ?, ?) ON CONFLICT(slot_date) DO UPDATE SET capacity_minutes=excluded.capacity_minutes, reserved_minutes=excluded.reserved_minutes, blocked=excluded.blocked, notes=excluded.notes",
            (payload.slot_date, payload.capacity_minutes, payload.reserved_minutes, int(payload.blocked), payload.notes),
        )
    return {"slot_date": payload.slot_date, "updated": True}


@app.get("/api/delivery-knowledge")
def delivery_knowledge(query: str) -> dict:
    return search_delivery_knowledge(query)


@app.post("/api/payment-proofs/{request_id}/analyze")
async def analyze_payment_proof(request_id: str, file: UploadFile = File(...)) -> dict:
    if not fetch_one("SELECT id FROM order_requests WHERE id = ?", (request_id,)):
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    content = await file.read()
    try:
        result = save_and_analyze(request_id, file.filename or "comprobante", content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    with connect() as connection:
        connection.execute("UPDATE order_requests SET status='payment_proof_under_review', updated_at=? WHERE id=?", (utc_now(), request_id))
    return result


@app.get("/api/admin/tasks")
def admin_tasks(staff: str = Depends(require_staff)) -> list[dict]:
    return fetch_all("SELECT * FROM human_tasks ORDER BY created_at DESC")


@app.get("/api/admin/order-requests")
def admin_order_requests(staff: str = Depends(require_staff)) -> list[dict]:
    return fetch_all(
        """
        SELECT r.id, r.customer_name, r.requested_at, r.fulfillment_mode, r.status,
               p.name AS product_name, p.base_price,
               q.id AS quote_id, q.total AS quote_total, q.status AS quote_status
        FROM order_requests r
        JOIN products p ON p.id = r.product_id
        LEFT JOIN quotes q ON q.id = (
            SELECT q2.id FROM quotes q2 WHERE q2.request_id = r.id ORDER BY q2.version DESC LIMIT 1
        )
        ORDER BY r.created_at DESC
        """
    )


@app.get("/api/admin/audit")
def admin_audit(staff: str = Depends(require_staff)) -> list[dict]:
    return fetch_all("SELECT * FROM audit_events ORDER BY created_at DESC LIMIT 100")
