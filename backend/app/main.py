from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.config import settings
from app.db import init_pool, close_pool
from app.graph import init_driver, close_driver
from app.health import run_all_checks
from app.middleware import DemoApiKeyMiddleware
from app.rate_limit import limiter
from app.routers import fleet
from app.routers import fleet, tests, ws






@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    await init_driver()
    yield
    await close_pool()
    await close_driver()





app = FastAPI(title="Mikata API", lifespan=lifespan)


 

# Added last -> runs first (outermost). CORS wraps everything.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(DemoApiKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list, 
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["x-api-key", "content-type"],
)




app.include_router(fleet.router)
app.include_router(tests.router)
app.include_router(ws.router)






@app.get("/api/v1/healthz")
async def healthz():
    checks = await run_all_checks()
    all_ok = all(s in ("ok", "unconfigured") for s in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}