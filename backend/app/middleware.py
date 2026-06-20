import hmac

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

EXEMPT_PATHS = {"/api/v1/healthz", "/docs", "/openapi.json", "/redoc", "/ws/events"}


class DemoApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        provided_key = request.headers.get("x-api-key", "")
        if not hmac.compare_digest(provided_key, settings.demo_api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})

        return await call_next(request)
