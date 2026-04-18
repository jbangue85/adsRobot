# adsRobot

`adsRobot` es un servidor MCP en Python para operar Meta Ads, con una capa de flujo de trabajo para briefs de campaña, preparación de assets y validación de lanzamiento.

## Estructura del repositorio

- `src/meta_ads_mcp/`: servidor MCP, cliente de la API de Meta y módulos de herramientas.
- `campaigns/`: una carpeta por campaña con su `campana.yaml` y sus assets (videos/imágenes, en gitignore).
- `scripts/`: puntos de entrada para flujos de trabajo locales.
- `docs/workflows/`: runbooks de operación para los skills de Claude.

## Configuración local

1. Crear un virtualenv con Python 3.12.
2. Instalar el paquete en modo editable:

```bash
python -m pip install -e .
```

3. Copiar `.env.example` a `.env` y completar con credenciales válidas de Meta.

## Comandos comunes

```bash
python scripts/run_mcp.py
python scripts/validate_campaign.py campaigns/[nombre-campaña]/campana.yaml
docker compose up --build
```

## Flujo de trabajo

- Validar siempre con `scripts/validate_campaign.py` antes de lanzar una campaña.
- Usar el skill `/launch-campaign` para crear la estructura completa en Meta desde un YAML.
- Usar el skill `/generate-copy` para generar copy y prompts creativos desde un brief de producto.
