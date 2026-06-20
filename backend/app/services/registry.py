import orjson
from app.db import get_pool
from app import graph
from app.services import pis





async def register_bot(name: str, description: str) -> dict:
    result = await pis.classify(name, description)
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO bots (name, description, patient_impact_level, "
            "patient_impact_score, pis_reasoning) "
            "VALUES ($1, $2, $3, $4, $5) RETURNING *",
            name, description, result.level, result.score, result.reasoning,
        )
    try:
        await graph.upsert_bot_node(str(row["id"]), name, result.level)
    except Exception:
        pass 
    return dict(row)



async def list_fleet() -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch(
        "SELECT * FROM bots ORDER BY patient_impact_level DESC, name ASC"
    )
    return [dict(r) for r in rows]


async def get_bot(bot_id: str) -> dict | None:
    pool = get_pool()
    row = await pool.fetchrow("SELECT * FROM bots WHERE id = $1", bot_id)
    return dict(row) if row else None