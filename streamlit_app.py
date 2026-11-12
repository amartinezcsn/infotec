from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

import streamlit as st

from app.db import connect, fetch_all, fetch_one, init_db, utc_now
from app.schemas import ProductImport
from app.services.agent import respond
from app.services.catalog import import_products, list_products
from app.settings import ROOT


st.set_page_config(page_title="CUP&CAKE AI", page_icon="🧁", layout="wide")


@st.cache_resource
def prepare_demo() -> bool:
    init_db()
    seed = ROOT / "data" / "synthetic" / "catalog.json"
    if seed.exists() and not fetch_one("SELECT id FROM products LIMIT 1"):
        items = [ProductImport.model_validate(item) for item in json.loads(seed.read_text(encoding="utf-8"))]
        import_products(items)
    return True


def create_order(customer: str, product_id: str, quantity: str, flavor: str, theme: str,
                 requested_at: datetime, fulfillment: str, notes: str) -> str:
    request_id = str(uuid.uuid4())
    now = utc_now()
    requirements = {
        "quantity_or_portions": quantity,
        "flavor": flavor,
        "theme": theme,
        "customer_notes": notes,
        "customer_confirmed_summary": True,
    }
    with connect() as connection:
        connection.execute(
            "INSERT INTO order_requests VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_availability_review', ?, ?)",
            (request_id, str(uuid.uuid4()), customer, product_id, json.dumps(requirements, ensure_ascii=False),
             requested_at.isoformat(), fulfillment, now, now),
        )
        connection.execute(
            "INSERT INTO human_tasks VALUES (?, 'availability_review', ?, 'high', 'open', ?, NULL, ?, NULL)",
            (str(uuid.uuid4()), request_id, "Revisar calendario, capacidad humana, complejidad y precio", now),
        )
    return request_id


def review_order(request_id: str, decision: str, comment: str) -> None:
    now = utc_now()
    with connect() as connection:
        connection.execute(
            "INSERT INTO availability_reviews VALUES (?, ?, ?, 'streamlit-admin', ?, NULL, ?)",
            (str(uuid.uuid4()), request_id, decision, comment, now),
        )
        connection.execute("UPDATE order_requests SET status=?, updated_at=? WHERE id=?", (decision, now, request_id))
        connection.execute(
            "UPDATE human_tasks SET status='completed', completed_at=? WHERE related_id=? AND task_type='availability_review'",
            (now, request_id),
        )


prepare_demo()
st.title("🧁 CUP&CAKE AI")
st.caption("Repostería creativa sobre pedido · Catálogo Kyte · Disponibilidad confirmada por personas")

client_tab, assistant_tab, staff_tab = st.tabs(["Catálogo y solicitud", "Asistente", "Supervisión humana"])

with client_tab:
    st.subheader("Productos elaborados sobre pedido")
    st.info("No manejamos existencias. Toda fecha y capacidad de producción debe ser confirmada por el equipo.")
    products = list_products(limit=20)
    columns = st.columns(3)
    for index, product in enumerate(products):
        with columns[index % 3]:
            if product.get("image_url"):
                st.image(product["image_url"], use_container_width=True)
            st.markdown(f"### {product['name']}")
            st.write(product["description"])
            st.write(f"Precio base: **${product['base_price']} {product['currency']}**")
            st.link_button("Ver en Kyte", product["kyte_url"], use_container_width=True)

    st.divider()
    st.subheader("Solicitar revisión de fecha")
    if products:
        product_map = {p["name"]: p["id"] for p in products}
        with st.form("order-form", clear_on_submit=True):
            customer = st.text_input("Nombre")
            selected = st.selectbox("Producto", list(product_map))
            quantity = st.text_input("Cantidad o porciones")
            flavor = st.text_input("Sabor")
            theme = st.text_input("Tema y colores")
            requested_date = st.date_input("Fecha solicitada", min_value=datetime.now().date() + timedelta(days=1))
            fulfillment = st.radio("Entrega", ["pickup", "delivery"], format_func=lambda x: "Recolección" if x == "pickup" else "Entrega a domicilio")
            notes = st.text_area("Notas")
            confirmed = st.checkbox("Confirmo que el pedido está sujeto a revisión humana de calendario y precio")
            submitted = st.form_submit_button("Enviar solicitud", type="primary")
        if submitted:
            if not all([customer.strip(), quantity.strip(), flavor.strip(), theme.strip(), confirmed]):
                st.error("Completa los campos obligatorios y confirma el resumen.")
            else:
                request_id = create_order(customer, product_map[selected], quantity, flavor, theme,
                                          datetime.combine(requested_date, datetime.min.time()), fulfillment, notes)
                st.success(f"Solicitud recibida: {request_id}. El equipo revisará calendario y capacidad.")

with assistant_tab:
    st.subheader("Asistente de atención")
    st.write("Consulta productos, personalización y políticas de entrega. Las decisiones críticas se escalan al equipo.")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    if prompt := st.chat_input("¿Qué deseas preparar?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        result = respond(prompt)
        answer = result["answer"]
        if result.get("products"):
            answer += "\n\n" + "\n".join(f"- [{p['name']}]({p['kyte_url']}) desde ${p['base_price']} MXN" for p in result["products"])
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

with staff_tab:
    st.subheader("Panel de supervisión humana")
    try:
        configured_token = st.secrets["ADMIN_TOKEN"]
    except (KeyError, FileNotFoundError):
        configured_token = ""
    supplied_token = st.text_input("Token de administración", type="password")
    if not configured_token:
        st.warning("Configura ADMIN_TOKEN en los secretos de Streamlit para habilitar este panel.")
    elif supplied_token != configured_token:
        st.info("Ingresa el token configurado para revisar solicitudes.")
    else:
        orders = fetch_all(
            "SELECT r.id, r.customer_name, r.requested_at, r.fulfillment_mode, r.status, p.name product_name "
            "FROM order_requests r JOIN products p ON p.id=r.product_id ORDER BY r.created_at DESC"
        )
        st.metric("Solicitudes", len(orders))
        for order in orders:
            with st.expander(f"{order['customer_name']} · {order['product_name']} · {order['status']}"):
                st.json(order)
                if order["status"] == "pending_availability_review":
                    comment = st.text_input("Comentario", key=f"comment-{order['id']}")
                    left, right = st.columns(2)
                    if left.button("Aprobar disponibilidad", key=f"approve-{order['id']}", type="primary"):
                        review_order(order["id"], "availability_approved", comment)
                        st.rerun()
                    if right.button("Rechazar disponibilidad", key=f"reject-{order['id']}"):
                        review_order(order["id"], "availability_rejected", comment)
                        st.rerun()

st.divider()
st.caption("MVP demostrativo. Los datos guardados en SQLite dentro de Streamlit Community Cloud pueden reiniciarse al redesplegar.")
