# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Comandos de desarrollo

```bash
# Instalar dependencias en el virtualenv local del proyecto
pyenv install 3.12.13
poetry config virtualenvs.in-project true --local
poetry env use "$(pyenv which python)"
poetry install

# Iniciar el servidor MCP localmente
poetry run python scripts/run_mcp.py

# Validar un YAML de campaña antes del lanzamiento
poetry run python scripts/validate_campaign.py campaigns/[nombre-campaña]/campana.yaml

# Ejecutar con Docker
docker compose up --build
```

## Arquitectura

El proyecto es un **servidor FastMCP HTTP** (puerto 8000) que envuelve la API de Meta Ads y expone 21 herramientas a clientes MCP (Codex, etc.).

```
Cliente MCP → Servidor FastMCP (server.py :8000/mcp)
               → tools/*.py (6 módulos por tipo de recurso)
                   → client.py (singleton FacebookAdsApi)
                       → Meta Ads API v25.0
```

- **`server.py`** — Punto de entrada; registra todas las herramientas e inicia el servidor HTTP.
- **`client.py`** — Singleton lazy: inicializa `FacebookAdsApi` una vez desde variables de entorno y cachea el objeto `AdAccount`.
- **`campaign_schema.py`** — Validador YAML que aplica los límites de Meta (headline ≤40 chars) y verifica la existencia de assets.
- **`tools/`** — Un módulo por recurso: `campaigns`, `ad_sets`, `ads`, `creatives`, `insights`, más `__init__.py`.

## Flujo de campaña

Cada campaña vive en su propia carpeta: `campaigns/[nombre-campaña]/campana.yaml` con sus assets en `assets/videos/` y `assets/images/` (en gitignore). El flujo de lanzamiento es siempre:

1. Validar YAML → `validate_campaign.py`
2. Crear campaña → ad set → (por cada anuncio) subir asset → crear creativo → crear anuncio

Ejecutar este flujo con las herramientas MCP disponibles, dejando los recursos en `PAUSED` salvo solicitud explícita.

Para tareas repetibles, usar estos skills locales de Codex cuando estén disponibles:

- `meta-ads-launch-campaign`: validar y lanzar una campaña desde YAML.
- `meta-ads-generate-copy`: generar copy y completar campos de anuncios en YAML.

## Poetry y virtualenv

El proyecto usa `pyenv` para fijar Python 3.12.13 y Poetry para crear el entorno virtual dentro del repo:

```bash
pyenv install 3.12.13
poetry config virtualenvs.in-project true --local
poetry env use "$(pyenv which python)"
poetry install
```

`.python-version` fija la versión de Python del proyecto. `poetry.toml` fuerza el virtualenv local en `.venv/`, manteniendo las dependencias aisladas y evitando instalar paquetes en el Python global/local del sistema.

## Variables de entorno

Se requieren cinco variables (ver `.env.example`): `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`, `META_PAGE_ID`.

## Configuración MCP

El nombre del conector MCP es `meta-ads-local` para evitar colisión con cualquier conector alojado.

`.codex/config.toml` usa `http://localhost:8000/mcp` cuando el cliente MCP corre en la misma máquina donde está levantado el servidor en el puerto `8000`.

Docker Compose publica el contenedor en el puerto host definido por `META_ADS_MCP_HOST_PORT`, con `8001` como valor por defecto para evitar colisiones con otros servicios de la Raspberry Pi. Si el servidor corre en la Raspberry Pi y Codex corre desde otra máquina de la red, configurar el cliente MCP contra:

```toml
[mcp_servers.meta-ads-local]
url = "http://192.168.1.100:8001/mcp"
```

El servidor puede levantarse localmente con `scripts/run_mcp.py` o mediante Docker Compose.
