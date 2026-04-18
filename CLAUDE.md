# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos de desarrollo

```bash
# Instalar en modo editable (usar virtualenv, nunca global)
python -m pip install -e .

# Iniciar el servidor MCP localmente
python scripts/run_mcp.py

# Validar un YAML de campaña antes del lanzamiento
python scripts/validate_campaign.py campaigns/ejemplos/campana_ejemplo.yaml

# Ejecutar con Docker
docker compose up --build
```

## Arquitectura

El proyecto es un **servidor FastMCP HTTP** (puerto 8000) que envuelve la API de Meta Ads y expone 21 herramientas a clientes MCP (Claude, etc.).

```
Cliente MCP → Servidor FastMCP (server.py :8000/mcp)
               → tools/*.py (6 módulos por tipo de recurso)
                   → client.py (singleton FacebookAdsApi)
                       → Meta Ads API v25.0
```

- **`server.py`** — Punto de entrada; registra todas las herramientas e inicia el servidor HTTP.
- **`client.py`** — Singleton lazy: inicializa `FacebookAdsApi` una vez desde variables de entorno y cachea el objeto `AdAccount`.
- **`campaign_schema.py`** — Validador YAML que aplica los límites de Meta (headline ≤40 chars, body ≤125 chars) y verifica la existencia de assets.
- **`tools/`** — Un módulo por recurso: `campaigns`, `ad_sets`, `ads`, `creatives`, `insights`, más `__init__.py`.

## Flujo de campaña

Las campañas se definen como archivos YAML en `campaigns/`. Los assets (videos, imágenes) van en `campaigns/assets/` (en gitignore). El flujo de lanzamiento es siempre:

1. Validar YAML → `validate_campaign.py`
2. Crear campaña → ad set → (por cada anuncio) subir asset → crear creativo → crear anuncio

Usar el skill `/launch-campaign` para ejecutar este flujo.

## Variables de entorno

Se requieren cinco variables (ver `.env.example`): `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`, `META_PAGE_ID`.

## Configuración MCP

`.mcp.json` apunta a `http://localhost:8000/mcp`. El servidor corre localmente con `scripts/run_mcp.py` o mediante Docker. El nombre del conector MCP es `meta-ads-local` para evitar colisión con cualquier conector alojado.
