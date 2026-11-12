# Seguridad

## Controles implementados

- Contratos Pydantic y categorías cerradas.
- Aprobaciones humanas protegidas por un adaptador de rol local.
- Máquina de estados explícita.
- Límite de 8 MB y validación por firma para comprobantes.
- Hash SHA-256 y detección de duplicados.
- Escapado de contenido en el navegador.
- RAG limitado a documentos `approved` y filtrado de patrones de instrucciones incrustadas.
- Auditoría de creación de solicitudes, sincronización y revisiones.

## Sustituciones obligatorias en Azure

- Reemplazar `X-Demo-Admin` por Microsoft Entra ID y RBAC.
- Guardar secretos en Key Vault y usar Managed Identities.
- Incorporar análisis antimalware de Blob Storage.
- Usar Azure SQL con Entra-only authentication.
- Configurar redes privadas o restricciones de acceso según riesgo.
- Redactar telemetría antes de Application Insights.

