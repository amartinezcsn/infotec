# Limitaciones conocidas

- La URL real de Kyte está configurada, pero los productos y precios incluidos siguen siendo sintéticos hasta recibir una exportación o API autorizada.
- El token administrativo local no sustituye Entra ID.
- SQLite no es el almacenamiento objetivo de Azure.
- El RAG local es lexical; Azure AI Search queda preparado en infraestructura.
- El OCR local no extrae campos: valida el archivo, calcula hash y exige revisión. Document Intelligence requiere credenciales.
- Foundry solo se activa con endpoint, modelo, SDK y credenciales Entra.
- WhatsApp no está implementado porque requiere cuenta y autorización externas.
- El Bicep debe validarse con Azure CLI en la suscripción destino y puede requerir ajustes regionales o de API preview.

