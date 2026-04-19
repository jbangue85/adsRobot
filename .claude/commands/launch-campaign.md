Lee el archivo YAML de campaña indicado (o pide al usuario que especifique cuál) y crea toda la estructura en Meta Ads usando las herramientas MCP disponibles.

## Flujo de ejecución

Sigue este orden exacto — cada paso depende del anterior:

### 1. Leer y validar el YAML
- Lee el archivo de campaña (el usuario debe indicar la ruta, ej: `campaigns/mi_campana.yaml`)
- Verifica que todos los campos requeridos estén presentes
- Lista todos los `ads` con su `type` (video/image) y `file`
- Confirma con el usuario antes de continuar si hay campos vacíos o archivos faltantes

### 2. Crear la campaña
- Llama `create_campaign` con los parámetros del bloque `campaign:`
- Guarda el `campaign_id` devuelto
- Informa: "✓ Campaña creada: [nombre] (ID: [id])"

### 3. Crear el ad set
- Llama `create_ad_set` con los parámetros del bloque `ad_set:` + el `campaign_id`
- Si el YAML tiene `promoted_object.pixel_id: "${META_PIXEL_ID}"`, reemplazar por el valor de la variable de entorno `META_PIXEL_ID` antes de enviar
- El ad set **NO debe tener `daily_budget`** si la campaña ya tiene presupuesto a nivel de campaña (CBO)
- Guarda el `ad_set_id` devuelto
- Informa: "✓ Ad Set creado: [nombre] (ID: [id])"

### 4. Subir assets y crear creativos (por cada ad en la lista)

Para cada ad en `ads:`:

**Si `type: image`:**
1. Antes de subir: si el nombre del archivo contiene indicios de generación por IA (ej. "Gemini_Generated", "DALL-E", "midjourney", "generated", etc.), renombrarlo a un nombre descriptivo neutral (ej. `antes_despues_beneficios.png`) usando el contenido visual como referencia.
2. `upload_image(file)` → obtén `image_hash`
2. El ad usa campos en plural cuando están presentes en el YAML:
   - Si el YAML tiene `headlines` (lista) y/o `bodies` (lista) → usar esos directamente
   - Si el YAML tiene `headline` y `body` (strings simples) → pasarlos como listas de un elemento
   - `create_ad_creative_image(name, image_hash, headlines=..., bodies=..., link, call_to_action, descriptions=...)` → obtén `creative_id`
3. `create_ad(ad_set_id, creative_id, name)` → obtén `ad_id`
4. Informa: "✓ [nombre] — imagen subida, creativo y anuncio creados"

**Si `type: video`:**
1. `upload_video(file, title=name)` → obtén `video_id`
2. Extraer thumbnail con ffmpeg (primer fotograma) → `upload_image(thumb)` → obtén `image_hash`
3. El ad usa campos en plural cuando están presentes en el YAML:
   - Si el YAML tiene `headlines` (lista) y/o `bodies` (lista) → usar esos directamente
   - Si el YAML tiene `headline` y `body` (strings simples) → pasarlos como listas de un elemento
   - `create_ad_creative_video(name, video_id, headlines=..., bodies=..., link, call_to_action, descriptions=..., image_hash=...)` → obtén `creative_id`
4. `create_ad(ad_set_id, creative_id, name)` → obtén `ad_id`
5. Informa: "✓ [nombre] — video subido, creativo y anuncio creados"

### 5. Resumen final

Al terminar, muestra una tabla con:

| # | Nombre | Tipo | Creative ID | Ad ID | Estado |
|---|--------|------|-------------|-------|--------|
| 1 | V1 — Hero | video | 123... | 456... | ✓ |
| 2 | I1 — Lifestyle | image | 789... | 012... | ✓ |
...

Y al final:
- Campaign ID: `[id]`
- Ad Set ID: `[id]`
- Total anuncios creados: N
- Estado: PAUSED (listos para revisar y activar)

### Manejo de errores

- Si falla un upload: informa el error, pregunta si continuar con el siguiente o abortar
- Si falla un creativo: muestra el mensaje de error de Meta (suele indicar qué campo está mal)
- Si falla el ad: verifica que el creative_id sea válido y reintenta una vez

## Notas importantes

- Todos los anuncios se crean en estado `PAUSED` — el usuario debe activarlos manualmente o con `update_campaign_status`
- Los archivos de video/imagen deben existir en las rutas especificadas en el YAML
- Los budgets están en **centavos**: 5000 = $50.00 USD
- Si el campo `META_PAGE_ID` no está en el `.env`, pide al usuario que lo agregue antes de continuar
- Variables de entorno disponibles: `META_PAGE_ID`, `META_PIXEL_ID` — leerlas del `.env` para reemplazar placeholders en el YAML (`${META_PIXEL_ID}`, etc.)
