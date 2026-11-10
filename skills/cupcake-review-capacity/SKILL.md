---
name: cupcake-review-capacity
description: Evaluar capacidad tentativa del calendario de CUP&CAKE y preparar una revisión humana de fecha, personal y complejidad. Usar al valorar una solicitud sobre pedido; no usar para reservar, asignar personal definitivamente ni confirmar disponibilidad.
---

# Revisar agenda CUP&CAKE

Produce una señal tentativa y una tarea humana. La agenda representa capacidad de producción y entrega, nunca inventario.

## Flujo

1. Verifica que la solicitud tenga producto, cantidad, complejidad preliminar y fecha solicitada.
2. Consulta slots, bloqueos, minutos disponibles, entregas y ausencias mediante herramientas autorizadas.
3. Lee [references/capacity-policy.md](references/capacity-policy.md) para interpretar el resultado.
4. Ejecuta `scripts/calculate_capacity.py` con la capacidad y esfuerzo estimado entregados por el servicio.
5. Si existe capacidad aparente, crea una tarea `availability_review`; no reserves automáticamente.
6. Si está limitado o bloqueado, solicita alternativas al servicio de calendario y preséntalas como opciones no confirmadas.
7. Registra datos consultados, reglas, resultado y responsable humano.

## Reglas

- No inventes duración de elaboración. Usa estimaciones configuradas y muestra su versión.
- Una fecha libre no implica viabilidad del diseño, personal o entrega.
- Solo un `human_staff` autorizado puede aprobar, rechazar o proponer formalmente otra fecha.
- No reveles horarios privados, nombres innecesarios o carga individual al cliente.
- Reintentos no deben duplicar tareas ni reservas.
- Si faltan datos o hay contradicción, devuelve `manual_review`.

## Salida

Devuelve `requested_at`, `tentative_status`, `capacity_basis`, `reason_codes`, `alternative_dates`, `requires_human_review: true`, `human_task_id` y un mensaje que indique explícitamente que falta confirmación.

