import asyncio

import asyncpg
import httpx
from neo4j import AsyncGraphDatabase
from redis.asyncio import Redis

from app.config import settings


async def check_database() -> str:
    if not settings.database_url:
        return "unconfigured"
    try:
        conn = await asyncpg.connect(settings.database_url, timeout=3)
        await conn.execute("SELECT 1")
        await conn.close()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def check_redis() -> str:
    if not settings.redis_url:
        return "unconfigured"
    try:
        client = Redis.from_url(settings.redis_url, socket_timeout=3)
        await client.ping()
        await client.aclose()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def check_neo4j() -> str:
    if not settings.neo4j_uri:
        return "unconfigured"
    try:
        driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
        async with driver.session() as session:
            await session.run("RETURN 1")
        await driver.close()
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


async def check_uipath() -> str:
    if not settings.uipath_org_name or not settings.uipath_client_id:
        return "unconfigured"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(
                f"https://cloud.uipath.com/{settings.uipath_org_name}/{settings.uipath_tenant_name}/testmanager_/swagger/index.html"
            )
        return "ok" if resp.status_code < 500 else f"error: status {resp.status_code}"
    except Exception as exc:
        return f"error: {exc}"


async def run_all_checks() -> dict[str, str]:
    db, redis_status, neo4j_status, uipath_status = await asyncio.gather(
        check_database(), check_redis(), check_neo4j(), check_uipath()
    )
    return {
        "database": db,
        "redis": redis_status,
        "neo4j": neo4j_status,
        "uipath": uipath_status,
    }
