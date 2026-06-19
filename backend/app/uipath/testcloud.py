import asyncio
from app.config import settings
from app.uipath import client




_TERMINAL = {"Passed", "Failed", "Cancelled", "Error", "Stopped"}




async def inject_queue_item(specific_content: dict) -> None:
    resp = await client.request(
        "POST",
        "/odata/Queues/UiPathODataSvc.AddQueueItem",
        json={"itemData": {
            "Name": settings.uipath_queue_name,
            "Priority": "High",
            "SpecificContent": specific_content,
        }},
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Queue injection failed: HTTP {resp.status_code}")
    







async def start_test_set_execution(test_set_id: str) -> str:
    resp = await client.request(
        "POST",
        "/api/TestAutomation/StartTestSetExecution",
        params={"testSetId": test_set_id, "triggerType": "ExternalTool"},
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"StartTestSetExecution failed: HTTP {resp.status_code}")
    return str(resp.json())                     






async def poll_execution(execution_id: str) -> dict:
    deadline = asyncio.get_event_loop().time() + settings.uipath_poll_timeout_s
    while True:
        resp = await client.request(
            "GET",
            f"/odata/TestSetExecutions({execution_id})",
            params={"$expand": "TestCaseExecutions"},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Poll failed: HTTP {resp.status_code}")
        body = resp.json()
        status = body.get("Status", "Unknown")
        if status in _TERMINAL:
            return {"status": status, "raw": body}
        if asyncio.get_event_loop().time() > deadline:
            return {"status": "Timeout", "raw": body}
        await asyncio.sleep(settings.uipath_poll_interval_s)
    



    