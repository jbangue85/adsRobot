FROM python:3.12-slim

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --no-cache-dir "poetry>=2.0,<3.0"

COPY pyproject.toml poetry.lock README.md .
COPY src/ src/
COPY scripts/ scripts/

RUN poetry install --only main --no-ansi

CMD ["poetry", "run", "meta-ads-mcp"]
