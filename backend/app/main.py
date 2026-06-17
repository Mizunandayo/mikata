from fastapi import FastAPI

from app.health import run_all_checks
from app.middleware import DemoApiKeyMiddleware

app = FastAPI(title="Mikata API")
app.add_middleware(DemoApiKeyMiddleware)


@app.get("/api/v1/healthz")
async def healthz():
    checks = await run_all_checks()
    all_ok = all(status in ("ok", "unconfigured") for status in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}
