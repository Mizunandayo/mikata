import asyncio
import json
from pathlib import Path
from app.config import settings
from app.db import init_pool, close_pool, get_pool
from app import graph
from app.services import pis



FIXTURE = Path(__file__).parent / "fixtures" / "st_raphael_fleet.json"
DEMO_FAIL_BOT = "Prior Authorization Bot"




async def seed() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    await init_pool()
    await graph.init_driver()
    pool = get_pool()


    # Idempotent reset of demo data.
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE bots CASCADE")
    

    name_to_id: dict[str, str] = {}
    for b in data["bots"]:
        res = await pis.classify(b["name"], b["description"])
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO bots (name, description, patient_impact_level, "
                "patient_impact_score, pis_reasoning, automation_debt_score, "
                "last_test_result, last_tested_at) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7, NOW() - INTERVAL '4 minutes') "
                "RETURNING id",
                b["name"], b["description"], res.level, res.score, res.reasoning,
                _starter_debt(res.level),
                "fail" if b["name"] == DEMO_FAIL_BOT else "pass",
            )
            bot_id = str(row["id"])
            name_to_id[b["name"]] = bot_id
            await conn.execute(
                "INSERT INTO compliance_baselines (bot_id, schema_version, "
                "required_fields, updated_by) VALUES ($1,$2,$3,'manual')",
                row["id"], "v1.0", json.dumps(["diagnosis_code", "procedure_code"]),
            )
            await conn.execute(
                "INSERT INTO debt_score_history (bot_id, score) VALUES ($1,$2)",
                row["id"], _starter_debt(res.level),
            )
        await graph.upsert_bot_node(bot_id, b["name"], res.level)
        print(f"  L{res.level} {res.score:>5.1f}  {b['name']}")
    




    for d in data["dependencies"]:
        u, dn = name_to_id[d["upstream"]], name_to_id[d["downstream"]]
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO bot_dependencies (upstream_bot_id, downstream_bot_id, "
                "data_field, criticality) VALUES ($1,$2,$3,$4) ON CONFLICT DO NOTHING",
                u, dn, d["data_field"], d["criticality"],
            )
        await graph.upsert_dependency(u, dn, d["data_field"], d["criticality"])

    await graph.close_driver()
    await close_pool()
    print(f"Seeded {len(data['bots'])} bots, {len(data['dependencies'])} edges.")







def _starter_debt(level: int) -> float:
    # Plausible initial ADS so the fleet matrix looks alive on Day 2.
    return {1: 12.0, 2: 48.0, 3: 71.0}[level]


if __name__ == "__main__":
    asyncio.run(seed())