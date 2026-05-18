# vmkit-test-fullstack

A **VMKit test fixture** that exercises the happy path: a Python service that
needs Postgres and Redis and declares both in a manifest. Used by VMKit's
end-to-end test suite to verify that:

1. The repo scanner detects `asyncpg` and `redis` from `pyproject.toml` and
   reports `accessories_needed: ["postgres", "redis"]`.
2. The Kamal generator emits accessory blocks for both with the matching
   `_ACCESSORY_SPECS` defaults (postgres:16-alpine, redis:7-alpine).
3. The onboard PR ships a working Dockerfile, `config/deploy.<dest>.yml`,
   GH Actions workflow, and `.kamal/secrets.<dest>.tpl`.
4. Once merged + dispatched, the container boots, both accessories are
   reachable, and `GET /health` returns 200.

## What the app does

- `GET /health` opens a connection to each accessory and returns
  `{db: "ok", cache: "ok"}`. Used by Kamal's healthcheck (`/health` is the
  generator default).
- `GET /` returns a hello message — easy way to confirm the deploy URL
  responds without exercising the data path.

## Connection strings

The app reads `DATABASE_URL` and `REDIS_URL` from the environment. The
generated Kamal config wires both into the running container via the
secrets template (`STAGING_DATABASE_URL`, `STAGING_REDIS_URL` and friends);
locally you can run `docker compose up` against the bundled compose file
or `uvicorn app.main:app --reload` with both URLs in `.env`.

## VMKit manifest

`vmkit.yaml` at the repo root declares the accessories explicitly so the
scanner doesn't have to infer them. The static classifier still works on
this repo without the manifest (the deps give the answer away), but the
manifest is the v2 contract — once VMKit consumes it, scan time drops to
zero and the user has full control over accessory versions / images.
