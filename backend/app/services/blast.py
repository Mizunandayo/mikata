"""Cascade blast radius (feature 12)
Neo4j-first topology with a Postgres recursive-CTE fallback (Risk 3 posture)."""



from datetime import datetime, timezone
from app import graph
from app.db import get_pool
from app.events import bus



_MAX_DEPTH = 10





async def _topology(bot_id: str) -> tuple[list[dict], list[dict]]:
    try:
        nodes, edges = await graph.blast_radius_subgraph(bot_id)
        if nodes:
            return nodes, edges
    except Exception:
        pass 
    return await _topology_sql(bot_id)






async def _topology_sql(bot_id: str) -> tuple[list[dict], list[dict]]:
    pool = get_pool()
    node_rows = await pool.fetch(
        """
        WITH RECURSIVE d(id, depth) AS (
            SELECT downstream_bot_id, 1
            FROM bot_dependencies
            WHERE upstream_bot_id = $1
          UNION
            SELECT bd.downstream_bot_id, d.depth + 1
            FROM bot_dependencies bd
            JOIN d ON bd.upstream_bot_id = d.id
            WHERE d.depth < $2
        )
        SELECT id::text AS id, min(depth) AS depth
        FROM d GROUP BY id
        """,
        bot_id, _MAX_DEPTH,
    )
    nodes = [{"id": r["id"], "depth": r["depth"]} for r in node_rows]
    ids = [bot_id] + [n["id"] for n in nodes]
    edge_rows = await pool.fetch(
        "SELECT upstream_bot_id::text AS src, downstream_bot_id::text AS dst, "
        "data_field AS field, criticality FROM bot_dependencies "
        "WHERE upstream_bot_id = ANY($1::uuid[]) "
        "AND downstream_bot_id = ANY($1::uuid[])",
        ids,
    )
    edges = [dict(r) for r in edge_rows]
    return nodes, edges








async def compute(bot_id: str) -> dict | None:
    """Build the full blast-radius payload, or None if the bot does not exist."""
    pool = get_pool()
    origin = await pool.fetchrow(
        "SELECT id::text AS id, name, patient_impact_level AS level, "
        "patient_impact_score AS pis, daily_patient_volume AS volume "
        "FROM bots WHERE id = $1",
        bot_id,
    )
    if not origin:
        return None

    nodes, edges = await _topology(bot_id)
    depth_by_id = {n["id"]: n["depth"] for n in nodes}
    ids = list(depth_by_id.keys())

    enriched: list[dict] = []
    if ids:
        rows = await pool.fetch(
            "SELECT id::text AS id, name, patient_impact_level AS level, "
            "patient_impact_score AS pis, daily_patient_volume AS volume "
            "FROM bots WHERE id = ANY($1::uuid[])",
            ids,
        )
        for r in rows:
            enriched.append({
                "id": r["id"], "name": r["name"], "level": r["level"],
                "pis": float(r["pis"]), "depth": depth_by_id[r["id"]],
                "volume": r["volume"] or 0,
            })
    enriched.sort(key=lambda n: (n["depth"], n["name"]))

    summary = {
        "affected_bots": len(enriched),
        "aggregate_pis": round(sum(n["pis"] for n in enriched), 1),
        "patient_volume_24h": sum(n["volume"] for n in enriched),
        "max_depth": max((n["depth"] for n in enriched), default=0),
    }
    return {
        "origin": {
            "id": origin["id"], "name": origin["name"], "level": origin["level"],
            "pis": float(origin["pis"]), "depth": 0, "volume": origin["volume"] or 0,
        },
        "nodes": enriched,
        "edges": edges,
        "summary": summary,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }






async def compute_and_broadcast(bot_id: str) -> dict | None:
    """Compute the cascade and push it to every WS subscriber."""
    blast = await compute(bot_id)
    if blast is not None:
        await bus.publish({"type": "blast_radius", "blast": blast})
    return blast