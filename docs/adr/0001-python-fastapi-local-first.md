# ADR 0001 — Backend Python y adaptadores locales

## Estado

Aceptado para el prototipo; revisar antes de producción.

## Contexto

El plan original proponía ASP.NET Core 8, pero el equipo de ejecución disponible no contiene .NET, npm ni Azure CLI. Sí dispone de Python 3.10 y el proyecto fue trasladado a `C:\Python\infotec`.

## Decisión

Implementar el MVP con FastAPI, frontend HTML/CSS/JavaScript sin compilación y SQLite para desarrollo. Mantener límites de servicio para sustituir SQLite por Azure SQL y el orquestador local por Microsoft Foundry. La infraestructura objetivo continúa siendo Azure App Service Linux, Azure SQL, Blob Storage, AI Search, Document Intelligence, Key Vault, Application Insights y Microsoft Foundry.

## Consecuencias

- El flujo puede ejecutarse y probarse sin credenciales.
- El despliegue Azure requiere instalar dependencias de `requirements-azure.txt` y configurar identidades.
- SQLite, el token administrativo local y el OCR degradado no son aceptables para producción.
- La desviación no cambia las reglas de aprobación humana ni el alcance funcional.

