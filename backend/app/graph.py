from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import settings
_driver: AsyncDriver | None = None



async def init_driver() -> None:
    global _driver
    if _driver is None and settings.neo4j_uri:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=10,
        )




async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None





def _get() -> AsyncDriver:
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialized")
    return _driver




async def upsert_bot_node(bot_id: str, name: str, level: int) -> None:
    await _get().execute_query(
        "MERGE (b:Bot {id: $id}) SET b.name = $name, b.level = $level",
        id=bot_id, name=name, level=level,
    )




async def upsert_dependency(upstream_id: str, downstream_id: str,
                            data_field: str, criticality: str) -> None:
    await _get().execute_query(
        "MATCH (u:Bot {id: $u}), (d:Bot {id: $d}) "
        "MERGE (u)-[r:FEEDS {field: $field}]->(d) "
        "SET r.criticality = $crit",
        u=upstream_id, d=downstream_id, field=data_field, crit=criticality,
    )





async def downstream_bot_ids(bot_id: str) -> list[str]:
    records, _, _ = await _get().execute_query(
        "MATCH (start:Bot {id: $id})-[:FEEDS*1..]->(d:Bot) "
        "RETURN DISTINCT d.id AS id",
        id=bot_id,
    )
    return [r["id"] for r in records]





async def blast_radius_subgraph(bot_id: str) -> tuple[list[dict], list[dict]]:
    """Downstream cascade topology from Neo4j.
    Returns (nodes, edges):
      nodes: [{id, depth}]  — depth = shortest hop count from the origin (>=1)
      edges: [{src, dst, field, criticality}] — every FEEDS edge inside the blast
    """


    driver = _get()

    node_recs, _, _ = await driver.execute_query(
        "MATCH p = (s:Bot {id: $id})-[:FEEDS*1..]->(d:Bot) "
        "RETURN d.id AS id, min(length(p)) AS depth",
        id=bot_id,
    )
    nodes = [{"id": r["id"], "depth": r["depth"]} for r in node_recs]

    # Edges where the destination is reachable from the origin, and the source
    edge_recs, _, _ = await driver.execute_query(
        "MATCH (s:Bot {id: $id})-[:FEEDS*0..]->(a:Bot)-[r:FEEDS]->(b:Bot) "
        "WHERE EXISTS { MATCH (s)-[:FEEDS*1..]->(b) } "
        "RETURN DISTINCT a.id AS src, b.id AS dst, "
        "r.field AS field, r.criticality AS criticality",
        id=bot_id,
    )
    edges = [{"src": r["src"], "dst": r["dst"],
              "field": r["field"], "criticality": r["criticality"]}
             for r in edge_recs]
    return nodes, edges