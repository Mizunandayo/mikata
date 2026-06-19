import time
import asyncio
import httpx
from app.config import settings



_TOKEN_URL = f"{settings.uipath_base_url}/identity_/connect/token"
_REFRESH_MARGIN_S = 60
_lock = asyncio.Lock()
_cached_token: str | None = None
_expires_at: float = 0.0






async def get_token() -> str:
    global _cached_token, _expires_at
    if _cached_token and time.monotonic() < _expires_at - _REFRESH_MARGIN_S:
        return _cached_token
    async with _lock:
        if _cached_token and time.monotonic() < _expires_at - _REFRESH_MARGIN_S:
            return _cached_token
        if not (settings.uipath_client_id and settings.uipath_client_secret):
            raise RuntimeError("UiPath client credentials not configured")
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.uipath_client_id,
                    "client_secret": settings.uipath_client_secret,
                    "scope": settings.uipath_token_scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if resp.status_code != 200:
            raise RuntimeError(f"UiPath token request failed: HTTP {resp.status_code}")
        body = resp.json()
        _cached_token = body["access_token"]
        _expires_at = time.monotonic() + int(body.get("expires_in", 3600))
        return _cached_token








def reset_cache() -> None:
    global _cached_token, _expires_at
    _cached_token, _expires_at = None, 0.0