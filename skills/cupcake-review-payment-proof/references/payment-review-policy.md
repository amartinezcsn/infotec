# Política de revisión de comprobantes

## Estados preliminares

- `ready_for_human_review`: campos principales presentes y sin alerta determinista.
- `low_confidence`: un campo crítico está por debajo del umbral configurado.
- `amount_mismatch`: importe o moneda no coincide con el anticipo esperado.
- `duplicate_suspected`: hash idéntico o combinación fuerte de referencia, importe y fecha.
- `unreadable`: no se recuperan importe, fecha o referencia con evidencia suficiente.
- `unsafe_file`: el archivo falla validaciones de seguridad.

Ninguno equivale a pago confirmado. El revisor humano puede aprobar el comprobante documental o solicitar corrección; la conciliación bancaria real queda fuera del MVP.

## Campos críticos

`transaction_date`, `amount`, `currency` y al menos uno entre `reference` o `tracking_key`. `institution` es deseable, no siempre obligatorio.

## Comparación

- Usar decimal, nunca punto flotante binario, en la aplicación.
- Comparar moneda explícita.
- No aceptar tolerancia monetaria salvo regla aprobada y versionada.
- Un hash idéntico siempre genera alerta de duplicado.

