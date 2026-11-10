# Máquina de estados y control de transición

## Estados

`draft`, `requirements_incomplete`, `pending_availability_review`, `availability_approved`, `alternative_proposed`, `availability_rejected`, `quote_pending`, `quote_sent`, `awaiting_deposit`, `payment_proof_under_review`, `confirmed`, `in_design`, `in_production`, `ready_for_delivery`, `completed`, `cancelled`.

## Transiciones permitidas

| Origen | Destinos |
|---|---|
| draft | requirements_incomplete, pending_availability_review, cancelled |
| requirements_incomplete | pending_availability_review, cancelled |
| pending_availability_review | availability_approved, alternative_proposed, availability_rejected, cancelled |
| alternative_proposed | pending_availability_review, availability_rejected, cancelled |
| availability_approved | quote_pending, cancelled |
| quote_pending | quote_sent, cancelled |
| quote_sent | awaiting_deposit, cancelled |
| awaiting_deposit | payment_proof_under_review, cancelled |
| payment_proof_under_review | confirmed, awaiting_deposit, cancelled |
| confirmed | in_design, cancelled |
| in_design | in_production, cancelled |
| in_production | ready_for_delivery, cancelled |
| ready_for_delivery | completed, cancelled |

## Transiciones exclusivamente humanas

- `pending_availability_review` a cualquier decisión de disponibilidad.
- `quote_pending` a `quote_sent`.
- `payment_proof_under_review` a `confirmed` o de vuelta a `awaiting_deposit`.
- `confirmed` en adelante, incluida cancelación.

Un agente puede crear borradores, recopilar datos y abrir tareas. No puede simular al actor humano ni convertir ausencia de respuesta en aprobación.

## Registro mínimo

Guardar `resource_id`, estado anterior, estado nuevo, tipo e identificador del actor, fecha UTC, motivo, correlación e idempotencia. Una transición inválida no modifica datos.

