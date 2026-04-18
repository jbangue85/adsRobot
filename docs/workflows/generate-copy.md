# Flujo: Generar Copy

Usa este skill para escribir el copy publicitario de assets que ya tienes (videos o imágenes).

## Cuándo usarlo

- Tienes un video o imagen listo y necesitas headline, body, descripción y CTA.
- Tienes varios assets y quieres generar el copy de todos en un batch.
- Quieres completar el copy de un YAML de campaña existente.

## Inputs

- Descripción del producto y propuesta de valor
- Descripción breve de cada asset (qué se ve en el video/imagen)
- URL de destino
- Ruta YAML opcional: `campaigns/mi_campana.yaml`

## Output

Copy listo para insertar en el YAML de campaña:

- Por cada asset: `headline` (≤40 chars), `body` (≤125 chars), `description` (≤30 chars), `call_to_action`, `tone`
- 3 variaciones (A empática, B aspiracional, C social proof)
- 5 títulos alternativos por asset

## Modos

- **Individual** — un solo asset
- **Batch** — varios assets; mapea ángulos primero para evitar canibalización en Andromeda

## Secuencia

1. Describir el producto una sola vez.
2. Describir cada asset (tipo + contenido).
3. Aprobar la tabla de ángulos antes de generar.
4. Recibir copy asset por asset.
5. Guardar en YAML (el skill ofrece hacerlo automáticamente).

## Siguiente paso

Una vez guardado el YAML:
```bash
python scripts/validate_campaign.py campaigns/mi_campana.yaml
# luego:
/launch-campaign campaigns/mi_campana.yaml
```
