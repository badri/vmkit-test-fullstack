"""vmkit-test-fullstack — minimal FastAPI app that pings Postgres + Redis.

The health endpoint is the load-bearing surface for VMKit's deploy gate:
Kamal-proxy hits /health every 3 seconds and rolls back the deploy if it
fails. Each backend probe is wrapped in its own try so a single broken
dependency reports specifically ('db: ok, cache: error') instead of
collapsing the whole response.
"""
from __future__ import annotations

import os

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI(title="vmkit-test-fullstack")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "vmkit-test-fullstack — see /health for backend status"}


async def _ping_postgres() -> str:
    if not DATABASE_URL:
        return "unconfigured"
    try:
        conn = await asyncpg.connect(DATABASE_URL, timeout=2)
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()
        return "ok"
    except Exception as e:  # noqa: BLE001 — test fixture, we want the error text
        return f"error: {type(e).__name__}"


async def _ping_redis() -> str:
    if not REDIS_URL:
        return "unconfigured"
    try:
        client = redis.from_url(REDIS_URL, socket_timeout=2)
        try:
            pong = await client.ping()
        finally:
            await client.aclose()
        return "ok" if pong else "no-pong"
    except Exception as e:  # noqa: BLE001
        return f"error: {type(e).__name__}"


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "db": await _ping_postgres(),
        "cache": await _ping_redis(),
    }
