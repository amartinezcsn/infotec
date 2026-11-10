# Contrato de solicitud personalizada

## Campos

```json
{
  "product": {
    "product_id": "uuid",
    "source_id": "string",
    "category": "pasteles-personalizados|cupcakes|galletas-decoradas",
    "name": "string",
    "base_price": 0.0,
    "currency": "MXN",
    "kyte_url": "https://...",
    "last_synced_at": "ISO-8601"
  },
  "quantity_or_portions": "string",
  "flavor": "string",
  "filling": "string|null",
  "theme": "string",
  "colors": ["string"],
  "inscription": "string|null",
  "reference_image_ids": ["uuid"],
  "dietary_notes": ["string"],
  "budget": {"amount": 0.0, "currency": "MXN"},
  "requested_at": "ISO-8601",
  "fulfillment_mode": "delivery|pickup",
  "delivery_zone_or_postal_code": "string|null",
  "customer_notes": "string|null",
  "customer_confirmed_summary": false
}
```

## Validación

Son obligatorios: producto válido, cantidad o porciones, sabor, tema, fecha, modalidad y confirmación del resumen. `filling` puede ser nulo para productos donde no corresponda. La dirección completa se solicita más tarde y no debe exponerse en prompts o trazas.

Las notas alimentarias son requisitos declarados por el cliente, no certificaciones de seguridad. Toda solicitud requiere revisión humana de viabilidad.

