# adsRobot

`adsRobot` es un servidor MCP en Python para operar Meta Ads, con una capa de flujo de trabajo para briefs de campaña, preparación de assets y validación de lanzamiento.

## Estructura del repositorio

- `src/meta_ads_mcp/`: servidor MCP, cliente de la API de Meta y módulos de herramientas.
- `campaigns/`: una carpeta por campaña con su `campana.yaml` y sus assets (videos/imágenes, en gitignore).
- `scripts/`: puntos de entrada para flujos de trabajo locales.

## Configuración local

1. Instalar `pyenv` y Poetry.
2. Instalar la versión de Python fijada para el proyecto:

```bash
pyenv install 3.12.13
```

3. Configurar Poetry para crear el virtualenv dentro del proyecto:

```bash
poetry config virtualenvs.in-project true --local
```

4. Crear el virtualenv con el Python de `pyenv` e instalar dependencias en `.venv/`:

```bash
poetry env use "$(pyenv which python)"
poetry install
```

5. Copiar `.env.example` a `.env` y completar con credenciales válidas de Meta.

## Comandos comunes

```bash
poetry run python scripts/run_mcp.py
poetry run python scripts/validate_campaign.py campaigns/[nombre-campaña]/campana.yaml
poetry run meta-ads-mcp
docker compose up --build
```

## Flujo de trabajo

- Validar siempre con `scripts/validate_campaign.py` antes de lanzar una campaña.
- Crear la estructura en Meta desde el YAML en este orden: campaña, ad set, assets, creativos y anuncios.
- Dejar campañas y anuncios en `PAUSED` salvo que se solicite activarlos explícitamente.

## Rate limiting de Meta

El servidor MCP incluye un limitador local de puntos para evitar exceder el rate limit de Meta Marketing API, especialmente cuando la app está en Development tier. Por defecto usa:

```env
META_API_RATE_LIMIT_ENABLED=true
META_API_RATE_LIMIT_MAX_SCORE=60
META_API_RATE_LIMIT_DECAY_SECONDS=300
```

El MCP cuenta cada lectura como 1 punto y cada escritura como 3 puntos. Si no hay puntos suficientes, espera antes de hacer la llamada a Meta. Para Standard tier se puede subir `META_API_RATE_LIMIT_MAX_SCORE`, pero en Raspberry Pi conviene mantener el default mientras la app esté en Development tier.

## Campañas a WhatsApp

Para campañas que abren WhatsApp en lugar de una landing, usar `destination_type: WHATSAPP` en el ad set y poner el número en `ad_set.promoted_object.whatsapp_phone_number`. Meta decide el destino desde el conjunto de anuncios, no desde el creativo. No omitir ese campo: si solo se envía `page_id`, Meta puede resolver el WhatsApp conectado a la página y enviar tráfico al número equivocado.

Para que Ads Manager muestre vista previa con imagen, los creativos WhatsApp se crean con `object_story_spec.link_data` y `WHATSAPP_MESSAGE`. Meta rechazó combinar ese formato con múltiples textos en `asset_feed_spec`; si se necesitan variaciones reales, crear anuncios separados por variación.

```yaml
campaign:
  name: "Producto — WhatsApp"
  objective: OUTCOME_SALES
  daily_budget: 60000
  status: PAUSED
  special_ad_categories: []

ad_set:
  name: "Producto — WhatsApp — Ad Set"
  optimization_goal: CONVERSATIONS
  billing_event: IMPRESSIONS
  destination_type: WHATSAPP
  promoted_object:
    page_id: "${META_PAGE_ID}"
    whatsapp_phone_number: "573161234567"
  targeting:
    geo_locations:
      countries: ["CO"]

ads:
  - name: "Video 01 — WhatsApp"
    type: video
    file: assets/videos/video1.mp4
    headline: "Compra por WhatsApp"
    body: "Escríbenos y te ayudamos con tu pedido."
    destination: whatsapp
    call_to_action: WHATSAPP_MESSAGE
    whatsapp_prefilled_message: "Hola, quiero más información del producto."
```

## Configuración MCP

La configuración para Codex vive en `.codex/config.toml` y apunta al servidor MCP desplegado en la Raspberry Pi:

```toml
[mcp_servers.meta-ads-local]
url = "http://192.168.1.100:8001/mcp"
```

`scripts/run_mcp.py` queda como opción de desarrollo local, pero el flujo normal usa la Raspberry Pi.

## Skills de Codex

Los flujos antiguos de comandos se migraron a skills locales de Codex:

- `meta-ads-launch-campaign`: valida y lanza campañas desde `campaigns/*/campana.yaml`.
- `meta-ads-generate-copy`: genera copy para anuncios y completa campos YAML.

Ejemplos de uso:

```text
Usa $meta-ads-launch-campaign para lanzar campaigns/mi_campana/campana.yaml
Usa $meta-ads-generate-copy para completar el copy de campaigns/mi_campana/campana.yaml
```
