# Agentes y skills

| Agente | Skill | Decisiones permitidas |
|---|---|---|
| Orquestador | `skills/cupcake-orchestrate-orders` | Clasificar, delegar y consolidar |
| Atención y diseño | `skills/cupcake-capture-design` | Buscar productos y recopilar requisitos |
| Agenda | `skills/cupcake-review-capacity` | Calcular señal tentativa y crear revisión |
| Conocimiento | `skills/cupcake-answer-delivery` | Responder solo con evidencia aprobada |
| Documental | `skills/cupcake-review-payment-proof` | Analizar OCR y señalar alertas |

Las decisiones humanas se realizan en la API con un rol autorizado. El adaptador local usa reglas deterministas. El adaptador Foundry de `app/services/foundry.py` redacta resultados aprobados y conserva la salida local si Foundry falla.

