# Backend development image
FROM python:3.14-slim AS backend

LABEL org.opencontainers.image.title="puckhate-backend"
LABEL org.opencontainers.image.description="puckhate backend development image"

# Build dependencies
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config; \
    rm -rf /var/lib/apt/lists/*

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Keep the virtualenv outside /app so /app can be bind mounted
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install python dependencies
COPY pyproject.toml uv.lock ./
RUN set -eux; uv sync --frozen --no-install-project

COPY . .
RUN set -eux; uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
