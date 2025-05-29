# Dockerfile

FROM python:3.13-slim-bullseye as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    # Poetry settings:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR="/opt/.cache"


ENV PATH="$POETRY_HOME/bin:$PATH"


RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./


RUN poetry install --no-root --sync

FROM python:3.13-slim-bullseye as runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/.venv/lib/python3.13/site-packages" \
    PATH="/app/.venv/bin:$PATH" \ 
    APP_HOST="0.0.0.0" \
    APP_PORT="8000"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/

EXPOSE ${APP_PORT}

CMD uvicorn src.main:app --host ${APP_HOST} --port ${APP_PORT}