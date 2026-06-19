import httpx
from app.config import settings
from app.uipath import auth




_ORCH_BASE = (
    f"{settings.uipath_base_url}/{settings.uipath_org_name}/"
    f"{settings.uipath_tenant_name}/orchestrator_"
)



def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-UIPATH-OrganizationUnitId": settings.uipath_folder_id,   # "7949084"
    }






async def request(method: str, path: str, *, json: dict | None = None,
                  params: dict | None = None) -> httpx.Response:
    url = f"{_ORCH_BASE}{path}"
    token = await auth.get_token()
    async with httpx.AsyncClient(timeout=20, verify=True) as client:
        resp = await client.request(method, url, headers=_headers(token),
                                    json=json, params=params)
        if resp.status_code == 401:
            auth.reset_cache()
            token = await auth.get_token()
            resp = await client.request(method, url, headers=_headers(token),
                                        json=json, params=params)
    return resp