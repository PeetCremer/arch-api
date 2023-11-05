# Two staged docker file which results in a slim image with a clean .venv
# Bigger builder image
FROM python:3.11.5-bullseye as builder

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --no-root

# Slim runner image
FROM python:3.11.5-slim-bullseye as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
# Only copy the arch_api package, not the tests or auxiliary files
COPY arch_api/ /app/arch_api

ENV UVICORN_HOST="0.0.0.0"
EXPOSE 8000

ENTRYPOINT ["python", "/app/arch_api"]
