# Reporte de evaluación

## Resultado local — 11 de noviembre de 2026

La suite automatizada cubre catálogo, categorías prohibidas, preguntas de inventario, RAG con citas, autorización de revisión, cotización humana, máquina de estados, capacidad tentativa, duplicado de comprobante, páginas y enrutamiento de intenciones.

- Resultado: **12 pruebas aprobadas, 0 fallidas**.
- Compilación Python: correcta.
- Validación visual: portal de cliente y panel del personal comprobados en navegador.
- Recorrido observado: consulta RAG, creación de solicitud, aprobación de fecha, creación y aprobación de cotización, y auditoría.
- Advertencia no bloqueante: el cliente de pruebas de Starlette señala una futura migración de `httpx` a `httpx2`.

Ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

La evaluación con un modelo Foundry queda pendiente de endpoint, despliegue de modelo y credenciales Entra.

