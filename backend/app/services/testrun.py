import json
from app.db import get_pool
from app.config import settings
from app.events import bus
from app.services import injection
from app.uipath import testcloud
from app.services import blast







_STATUS_TO_RESULT = {"Passed": "pass", "Failed": "fail"}




async def _set_status(run_id: str, status: str, detail: str = "",
                      execution_id: str | None = None) -> None:
    pool = get_pool()
    await pool.execute(
        "UPDATE test_runs SET status=$2, detail=$3, "
        "uipath_execution_id=COALESCE($4, uipath_execution_id), "
        "finished_at=CASE WHEN $2 IN ('passed','failed','error','timeout') "
        "THEN NOW() ELSE finished_at END WHERE id=$1",
        run_id, status, detail[:500], execution_id,
    )
    await bus.publish({"type": "test_run", "run_id": run_id,
                       "status": status, "detail": detail[:500]})
    




async def run_test(bot_id: str) -> str:
    pool = get_pool()
    bot = await pool.fetchrow(
        "SELECT id, name, uipath_test_set_id FROM bots WHERE id=$1", bot_id)
    if not bot:
        raise ValueError("bot not found")
    test_set_id = bot["uipath_test_set_id"] or settings.uipath_demo_test_set_id
    if not test_set_id:
        raise RuntimeError("no test set configured for this bot")

    patient = await pool.fetchrow(
        "SELECT id, summary FROM synthetic_patients ORDER BY random() LIMIT 1")
    if not patient:
        raise RuntimeError("no synthetic patients seeded — run seed.patients first")

    run = await pool.fetchrow(
        "INSERT INTO test_runs (bot_id, synthetic_patient_id, status, uipath_test_set_id) "
        "VALUES ($1,$2,'queued',$3) RETURNING id",
        bot_id, patient["id"], test_set_id)
    run_id = str(run["id"])
    await bus.publish({"type": "test_run", "run_id": run_id, "status": "queued",
                       "bot_id": bot_id, "bot_name": bot["name"]})

    try:
        summary = patient["summary"]
        if isinstance(summary, str):
            summary = json.loads(summary)

        await _set_status(run_id, "injecting", "Injecting synthetic patient")
        await testcloud.inject_queue_item(injection.to_queue_payload(summary, run_id))

        await _set_status(run_id, "running", "Starting Test Cloud execution")
        execution_id = await testcloud.start_test_set_execution(test_set_id)
        await _set_status(run_id, "running", f"Execution {execution_id} running",
                          execution_id=execution_id)

        result = await testcloud.poll_execution(execution_id)
        uip_status = result["status"]
        final = _STATUS_TO_RESULT.get(uip_status,
                                      "timeout" if uip_status == "Timeout" else "error")
        await _set_status(run_id, final, f"Test Cloud returned {uip_status}")
        if final in ("pass", "fail"):
            await _record_result(bot_id, run_id, final, result)
        if final == "fail":
            try:
                await blast.compute_and_broadcast(bot_id)
            except Exception:
                pass  
        return run_id
    except Exception:
        await _set_status(run_id, "error", "Run failed — see server logs")
        raise







async def _record_result(bot_id: str, run_id: str, result: str, raw: dict) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE bots SET last_test_result=$2, last_tested_at=NOW() WHERE id=$1",
                bot_id, result)
            await conn.execute(
                "INSERT INTO execution_events (bot_id, event_type, payload) "
                "VALUES ($1,$2,$3)",
                bot_id, "test_pass" if result == "pass" else "test_fail",
                json.dumps({"run_id": run_id, "uipath_status": raw["status"]}))
    await bus.publish({"type": "fleet_update", "bot_id": bot_id,
                       "last_test_result": result})