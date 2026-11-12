# Despliegue en Streamlit Community Cloud

## Configuración

- Repositorio: `amartinezcsn/infotec`
- Rama: `main`
- Archivo principal: `streamlit_app.py`
- Python recomendado: `3.12`

En **Advanced settings > Secrets**, agregar:

```toml
ADMIN_TOKEN = "un-token-largo-y-seguro"
```

El archivo real `.streamlit/secrets.toml` nunca debe subirse a Git.

## Alcance del MVP

La aplicación conserva FastAPI y añade una interfaz Streamlit para catálogo, solicitud de pedidos, asistente y revisión humana. SQLite sirve únicamente para demostración: el sistema de archivos de Community Cloud no constituye persistencia productiva. Para producción, sustituirlo por Azure SQL o PostgreSQL y almacenar archivos en Azure Blob Storage.
