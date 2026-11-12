# CUP&CAKE AI — Fase 2

MVP ejecutable para atención y pedidos de repostería creativa sobre pedido. Incluye catálogo Kyte sincronizado, captura de diseño, agenda tentativa, revisión humana, RAG de entrega, comprobantes y auditoría.

Tienda Kyte configurada: [https://cupcake.kyte.site/](https://cupcake.kyte.site/)

## Inicio rápido

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Portal: `http://127.0.0.1:8000`
- Personal: `http://127.0.0.1:8000/admin`
- OpenAPI: `http://127.0.0.1:8000/docs`
- Pruebas: `.\.venv\Scripts\python.exe -m pytest`

El modo local usa datos sintéticos y adaptadores seguros. Consulta `docs/open-decisions.md` antes de conectar sistemas reales o desplegar Azure.

