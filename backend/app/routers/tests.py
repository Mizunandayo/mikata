from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from app.config import settings
from app.db import get_pool
from app.rate_limit import limiter
from app.schemas import TestRunOut, WsTicketOut
from app.security import ws_ticket
from app.services import testrun




router = APIRouter(prefix="/api/v1", tags=["tests"])



@router.post("/tests/run", response_model=TestRunOut, status_code=202)
@limiter.limit("10/minute")
async def trigger_run(request: Request, bot_id: UUID):
    try:
        run_id = await testrun.run_test(str(bot_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Bot not found")
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return await _get_run(run_id)



@router.get("/tests/{run_id}", response_model=TestRunOut)
async def get_run(request: Request, run_id: UUID):
    return await _get_run(str(run_id))


@router.post("/ws-ticket", response_model=WsTicketOut)
@limiter.limit("30/minute")
async def issue_ws_ticket(request: Request):
    return WsTicketOut(ticket=ws_ticket.mint(), expires_in=settings.ws_ticket_ttl_s)



async def _get_run(run_id: str) -> TestRunOut:
    row = await get_pool().fetchrow("SELECT * FROM test_runs WHERE id=$1", run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return TestRunOut(**dict(row))