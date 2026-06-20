import asyncio
from pathlib import Path
import asyncpg
from app.config import settings



MIGRATIONS_DIR = Path(__file__).parent




async def run() -> None:
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is not set")

    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT NOW())"
        )
        applied = {
            r["version"]
            for r in await conn.fetch("SELECT version FROM schema_migrations")
        }
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = path.stem
            if version in applied:
                print(f"skip   {version}")
                continue
            sql = path.read_text(encoding="utf-8")
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES ($1)", version
                )
            print(f"applied {version}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())