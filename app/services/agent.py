from __future__ import annotations

import re

from .catalog import list_products
from .foundry import maybe_render
from .knowledge import search_delivery_knowledge


PRODUCT_TERMS = {
    "pastel": "pasteles-personalizados",
    "pasteles": "pasteles-personalizados",
    "cupcake": "cupcakes",
    "cupcakes": "cupcakes",
    "galleta": "galletas-decoradas",
    "galletas": "galletas-decoradas",
}


def respond(message: str) -> dict:
    lowered = message.lower()
    if any(term in lowered for term in ("existencia", "stock", "disponible en almacén")):
        return maybe_render(message, {
            "intent": "inventory_question",
            "answer": "CUP&CAKE trabaja exclusivamente sobre pedido. Podemos revisar una fecha tentativa, pero el equipo debe confirmar la capacidad de elaboración.",
            "sources": [],
            "requires_human_review": False,
        })
    if any(term in lowered for term in ("entrega", "domicilio", "código postal", "zona", "recolección")):
        result = search_delivery_knowledge(message)
        return maybe_render(message, {
            "intent": "delivery_policy",
            **result,
            "requires_human_review": result["needs_human_review"],
        })
    for term, category in PRODUCT_TERMS.items():
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            products = list_products(category=category, limit=3)
            return maybe_render(message, {
                "intent": "product_search",
                "answer": "Estos productos provienen del catálogo sincronizado de Kyte. Los precios son base y la disponibilidad requiere revisión humana.",
                "products": products,
                "requires_human_review": False,
            })
    return maybe_render(message, {
        "intent": "human_handoff",
        "answer": "Puedo ayudarte con pasteles personalizados, cupcakes, galletas decoradas, entregas o el estado de una solicitud. Para otro tema crearé una revisión humana.",
        "requires_human_review": True,
    })

