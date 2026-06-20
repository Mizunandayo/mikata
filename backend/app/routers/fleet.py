from fastapi import APIRouter, HTTPException, Request
from app.schemas import BotOut, BotRegisterIn, FleetOut
from app.services import registry



router = APIRouter(prefix="/api/v1/fleet", tags=["fleet"])
HOSPITAL = "St. Raphael Medical Center"






@router.get("", response_model=FleetOut)
async def get_fleet(request: Request):
    bots = await registry.list_fleet()
    return FleetOut(hospital=HOSPITAL, bot_count=len(bots),
                    bots=[BotOut(**b) for b in bots])




@router.post("/register", response_model=BotOut, status_code=201)
async def register(request: Request, body: BotRegisterIn):
    bot = await registry.register_bot(body.name, body.description)
    return BotOut(**bot)




@router.get("/{bot_id}", response_model=BotOut)
async def bot_detail(request: Request, bot_id: str):
    bot = await registry.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return BotOut(**bot)