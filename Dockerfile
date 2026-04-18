FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY scripts/ scripts/

# Install dependencies (no dev deps, use system python in Docker)
RUN uv sync --no-dev

# Run the MCP server via stdio
CMD ["uv", "run", "meta-ads-mcp"]
