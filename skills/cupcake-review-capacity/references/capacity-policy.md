# Política de capacidad tentativa

## Estados

- `apparently_available`: el slot no está bloqueado y el esfuerzo cabe con margen configurado.
- `limited`: el esfuerzo cabe, pero deja menos margen que el umbral.
- `blocked`: existe bloqueo explícito o el servicio está cerrado.
- `manual_review`: falta información, el esfuerzo rebasa capacidad o existen conflictos.

Todos los estados requieren revisión humana. Ninguno confirma el pedido.

## Entradas confiables

- Capacidad configurada del slot.
- Minutos ya reservados por solicitudes aprobadas.
- Esfuerzo estimado por una tabla versionada y aprobada por CUP&CAKE.
- Bloqueos, vacaciones y horarios.
- Ventana de entrega o recolección.

Las duraciones sintéticas usadas en demostración deben identificarse como tales y no migrar a producción sin aprobación.

## Privacidad

La respuesta al cliente puede mencionar disponibilidad general o una alternativa. No debe mostrar nombres del personal, causas privadas de ausencia, notas internas ni detalles de otros pedidos.

