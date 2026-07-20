# Production monorepo image

# ── Stage 1: build the frontend ─────────────────────────────
FROM node:lts AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN set -eux; npm install
COPY frontend/ ./
RUN set -eux; npm run build

# ── Stage 2: build the backend ─────────────────────────────
FROM python:3.14-slim AS app
LABEL org.opencontainers.image.title="puckhate"
LABEL org.opencontainers.image.description="puckhate production monorepo image"

# Build dependencies for mysqlclient
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config; \
    rm -rf /var/lib/apt/lists/*

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_DEBUG=0

WORKDIR /app

# Install python dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN set -eux; uv sync --frozen --no-install-project

# Include backend source and frontend from build stage 1
COPY backend/ ./
COPY --from=frontend-builder /backend/spa ./spa
RUN set -eux; uv sync --frozen
# throwaway key for this build step so collectstatic will run
RUN set -eux; \
    DJANGO_SECRET_KEY="build-time-collectstatic-placeholder" \
    uv run python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "puckhate.wsgi:application", "--bind", "0.0.0.0:8000"]
