# Multi-stage so the runtime image carries only the wheels + app code.
FROM python:3.12-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

FROM python:3.12-slim
WORKDIR /app
# Copy the site-packages installed by uv plus the entry-point scripts so
# uvicorn is on PATH without re-running pip in the runtime stage.
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY app ./app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
