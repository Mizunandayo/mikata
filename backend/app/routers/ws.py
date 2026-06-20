from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings
from app.events import bus
from app.security import ws_ticket




router = APIRouter()




@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    origin = websocket.headers.get("origin", "")
    ticket = websocket.query_params.get("ticket", "")
    if origin not in settings.cors_origins_list or not ws_ticket.verify(ticket):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    q = bus.subscribe()
    try:
        await websocket.send_json({"type": "connected"})
        while True:
            await websocket.send_json(await q.get())
    except WebSocketDisconnect:
        pass
    finally:
        bus.unsubscribe(q)
