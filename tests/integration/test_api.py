from __future__ import annotations

from datetime import datetime, timedelta, timezone


def test_catalog_contains_only_allowed_categories(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 3
    assert {item["category"] for item in products} == {
        "pasteles-personalizados",
        "cupcakes",
        "galletas-decoradas",
    }


def test_disallowed_category_is_rejected(client, admin_headers):
    payload = [{
        "source_id": "invalid-1",
        "name": "Producto fuera de alcance",
        "category": "paquetes-eventos",
        "description": "No permitido",
        "base_price": 100,
        "currency": "MXN",
        "variants": [],
        "product_url": "https://example.com/product",
        "published": True,
        "source_updated_at": "2026-11-11T12:00:00Z",
    }]
    response = client.post("/api/catalog/import", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_inventory_question_explains_made_to_order(client):
    session = client.post("/api/chat/sessions").json()["session_id"]
    response = client.post(f"/api/chat/sessions/{session}/messages", json={"content": "¿Tienen existencias de pastel?"})
    assert response.status_code == 200
    result = response.json()
    assert result["intent"] == "inventory_question"
    assert "sobre pedido" in result["answer"]


def test_delivery_answer_has_approved_citation(client):
    session = client.post("/api/chat/sessions").json()["session_id"]
    result = client.post(f"/api/chat/sessions/{session}/messages", json={"content": "¿Cómo funciona la entrega en zona centro?"}).json()
    assert result["intent"] == "delivery_policy"
    assert result["evidence_status"] == "sufficient"
    assert result["citations"][0]["status"] == "approved"


def _create_request(client):
    product_id = client.get("/api/products").json()[0]["id"]
    requested_at = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
    payload = {
        "idempotency_key": "request-test-0001",
        "customer_name": "Cliente Demo",
        "product_id": product_id,
        "quantity_or_portions": "20 porciones",
        "flavor": "vainilla",
        "filling": "frutos rojos",
        "theme": "espacio",
        "colors": ["azul"],
        "dietary_notes": [],
        "requested_at": requested_at,
        "fulfillment_mode": "pickup",
        "customer_confirmed_summary": True,
    }
    response = client.post("/api/order-requests", json=payload)
    assert response.status_code == 200
    return response.json()["id"], requested_at


def test_order_requires_human_review(client, admin_headers):
    request_id, _ = _create_request(client)
    order = client.get(f"/api/order-requests/{request_id}").json()
    assert order["status"] == "pending_availability_review"
    denied = client.post(
        f"/api/order-requests/{request_id}/availability-review",
        json={"decision": "availability_approved", "reviewer_id": "staff-1"},
    )
    assert denied.status_code == 403
    approved = client.post(
        f"/api/order-requests/{request_id}/availability-review",
        json={"decision": "availability_approved", "reviewer_id": "staff-1"},
        headers=admin_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "availability_approved"


def test_quote_requires_human_approval(client, admin_headers):
    request_id, _ = _create_request(client)
    client.post(
        f"/api/order-requests/{request_id}/availability-review",
        json={"decision": "availability_approved", "reviewer_id": "staff-1"},
        headers=admin_headers,
    )
    quote = client.post(
        f"/api/order-requests/{request_id}/quotes",
        json={"base_amount": "850.00", "adjustments": [], "total": "850.00"},
        headers=admin_headers,
    )
    assert quote.status_code == 200
    quote_id = quote.json()["quote_id"]
    denied = client.post(f"/api/quotes/{quote_id}/approve")
    assert denied.status_code == 403
    approved = client.post(f"/api/quotes/{quote_id}/approve", headers=admin_headers)
    assert approved.status_code == 200
    assert approved.json()["status"] == "quote_sent"


def test_payment_proof_duplicate_is_flagged(client):
    request_id, _ = _create_request(client)
    fake_pdf = b"%PDF-1.4\nsynthetic proof\n%%EOF"
    first = client.post(
        f"/api/payment-proofs/{request_id}/analyze",
        files={"file": ("proof.pdf", fake_pdf, "application/pdf")},
    )
    assert first.status_code == 200
    assert first.json()["requires_human_review"] is True
    second = client.post(
        f"/api/payment-proofs/{request_id}/analyze",
        files={"file": ("proof-again.pdf", fake_pdf, "application/pdf")},
    )
    assert second.status_code == 200
    assert second.json()["preliminary_status"] == "duplicate_suspected"

