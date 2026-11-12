# Arquitectura

```text
Navegador ── FastAPI/App Service ── servicios deterministas
   │              │                   ├─ catálogo Kyte
   │              │                   ├─ calendario
   │              │                   ├─ máquina de estados
   │              │                   ├─ RAG de entrega
   │              │                   └─ comprobantes
   │              │
   │              ├─ SQLite local / Azure SQL
   │              ├─ archivos locales / Blob Storage
   │              └─ orquestador local / Microsoft Foundry
   │
   └─ Portal cliente y panel humano
```

El modo local implementa el mismo contrato sin depender de credenciales. Cuando existen `FOUNDRY_PROJECT_ENDPOINT` y `FOUNDRY_MODEL_NAME`, el resultado determinista se entrega a Foundry para redacción; el modelo no controla estados ni decisiones sensibles.

## Persistencia

SQLite contiene productos, sincronizaciones, solicitudes, agenda, revisiones, cotizaciones, comprobantes, conversaciones, tareas y auditoría. La migración a Azure SQL debe conservar estos contratos.

## Infraestructura

`infra/main.bicep` define App Service Linux, Azure SQL, Storage, Key Vault, AI Search, Document Intelligence, Content Safety, Application Insights y un proyecto Foundry opcional.

