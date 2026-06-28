from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from app.rate_limit import limiter
from app.schemas import BlastRadiusOut
from app.services import blast





router = APIRouter(prefix="/api/v1", tags=["blast-radius"])





@router.get("/blast-radius/{bot_id}", response_model=BlastRadiusOut)
async def get_blast_radius(request: Request, bot_id: UUID):
    result = await blast.compute(str(bot_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return result






@router.post("/blast-radius/{bot_id}/simulate",
             response_model=BlastRadiusOut, status_code=202)
@limiter.limit("10/minute")
async def simulate_blast_radius(request: Request, bot_id: UUID):
    """Demo trigger: compute the cascade and broadcast it over the WS bus"""
    result = await blast.compute_and_broadcast(str(bot_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return result

