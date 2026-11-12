# Runbook operativo

## Salud

- `GET /api/health`: proceso disponible y modo de adaptadores.
- `GET /api/ready`: persistencia inicializada.
- Revisar tareas humanas y auditoría en `/admin`.

## Incidentes

- Foundry falla: la aplicación conserva el resultado determinista y marca `agent_warning`.
- Sin evidencia RAG: no responde la política y crea revisión humana.
- Sin OCR: conserva el archivo, marca baja confianza y crea tarea.
- Sincronización Kyte falla: conservar última versión válida y registrar el fallo.

## Apagado

Detener App Service o escalar a cero cuando el plan lo permita. Para una entrega académica, exportar evidencia antes de eliminar el grupo de recursos. La eliminación requiere aprobación explícita y verificación del nombre del grupo.

