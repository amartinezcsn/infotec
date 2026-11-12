# Despliegue

## Local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000`. El panel está en `/admin` y usa el token local configurado por `DEMO_ADMIN_TOKEN`.

## Azure

1. Instalar Azure CLI o usar Cloud Shell.
2. Crear un grupo de recursos autorizado.
3. Copiar `infra/main.bicepparam.example` a un archivo no versionado y establecer un secreto SQL seguro.
4. Validar y desplegar `infra/main.bicep`.
5. Desplegar el repositorio a App Service con build de Python.
6. Instalar `requirements-azure.txt` en el artefacto Azure.
7. Configurar `FOUNDRY_PROJECT_ENDPOINT` y `FOUNDRY_MODEL_NAME`.
8. Crear asignaciones RBAC y sustituir adaptadores locales.
9. Ejecutar smoke tests y evaluación.

No se realizó el despliegue porque este equipo no tiene Azure CLI, sesión, suscripción, modelo ni autorización de costos.

