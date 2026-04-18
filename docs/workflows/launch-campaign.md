# Flujo: Lanzar Campaña

Usa este runbook para crear una campaña de Meta a partir de un archivo YAML a través del servidor MCP.

## Precondiciones

- `.env` contiene credenciales válidas de Meta, incluyendo `META_PAGE_ID`.
- Los archivos de assets referenciados en el YAML existen localmente.
- El archivo pasa `python scripts/validate_campaign.py <archivo>`.

## Orden de ejecución

1. Leer el YAML y confirmar que el bloque de campaña, ad set y lista de anuncios estén completos.
2. Crear la campaña desde el bloque `campaign:`.
3. Crear el ad set desde el bloque `ad_set:`, vinculado a la campaña creada.
4. Por cada anuncio:
   - Subir el asset de imagen o video.
   - Crear el creativo correspondiente.
   - Crear el anuncio dentro del ad set.
5. Devolver un resumen con campaign ID, ad set ID y estado de creación por anuncio.

## Manejo de errores

- Si falta un asset, detener antes de cualquier mutación en la API.
- Si falla un upload, capturar el error de Meta y decidir si continuar con el siguiente anuncio.
- Si falla la creación del creativo, mostrar el campo inválido en lugar de reintentar a ciegas.

## Postcondiciones

- Dejar campañas y anuncios en `PAUSED` a menos que el usuario solicite activarlos explícitamente.
- Guardar cualquier YAML corregido en `campaigns/` para lanzamientos repetibles.
