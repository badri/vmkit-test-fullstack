# syntax=docker/dockerfile:1.7
FROM python:3.12.7-slim-bookworm AS build

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12.7-slim-bookworm AS runtime

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN groupadd -g 1000 app && useradd -u 1000 -g 1000 -m app

COPY --from=build /app /app

USER 1000:1000
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\")"]
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
