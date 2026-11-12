# Requisitos implementados

## Alcance funcional

- Consulta de pasteles personalizados, cupcakes y galletas decoradas desde una copia sincronizada de Kyte.
- Captura de una solicitud personalizada y confirmación del resumen por el cliente.
- Evaluación tentativa de capacidad sin confirmar fecha.
- Revisión humana obligatoria de disponibilidad.
- RAG local de políticas de entrega con citas y exclusión de borradores.
- Carga segura de PDF, PNG o JPG de comprobante, hash y detección de duplicados.
- Tareas humanas, auditoría, portal de cliente y panel administrativo.

## Reglas invariantes

- No existe inventario de producto terminado.
- Los precios son base.
- Ningún agente confirma fecha, cotización o pago.
- Kyte, documentos, mensajes y OCR son datos no confiables.
- Las categorías fuera del alcance son rechazadas por el contrato de API.

## Pendientes externos

Consultar [open-decisions.md](open-decisions.md). Azure, Kyte real, Foundry, Entra ID y Document Intelligence requieren datos o credenciales del propietario.

