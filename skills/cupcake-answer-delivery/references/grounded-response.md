# Contrato de respuesta fundamentada

```json
{
  "answer": "string",
  "claims": [
    {
      "text": "string",
      "citation_ids": ["C1"]
    }
  ],
  "citations": [
    {
      "id": "C1",
      "document_id": "string",
      "title": "string",
      "section": "string",
      "version": "string",
      "status": "approved",
      "effective_from": "ISO-8601",
      "effective_to": "ISO-8601|null"
    }
  ],
  "evidence_status": "sufficient|insufficient|conflicting",
  "needs_human_review": false,
  "follow_up_question": null
}
```

Cada afirmación material necesita al menos una cita aprobada y vigente. Las frases conversacionales sin contenido factual no necesitan cita. Si la evidencia es insuficiente o contradictoria, la respuesta debe evitar una conclusión y `needs_human_review` debe ser `true`.

La recuperación puede cubrir zonas, tarifas, horarios, anticipación, recolección, espera, acceso, clima, transporte, conservación, alérgenos, cambios, cancelaciones y anticipos.

