import hmac
import time
import base64
import secrets
import hashlib
from app.config import settings




def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")



def _sign(payload: str) -> str:
    sig = hmac.new(settings.ws_ticket_secret.encode(), payload.encode(),
                   hashlib.sha256).digest()
    return _b64(sig)



def mint() -> str:
    if not settings.ws_ticket_secret:
        raise RuntimeError("WS_TICKET_SECRET not configured")
    exp = int(time.time()) + settings.ws_ticket_ttl_s
    nonce = secrets.token_urlsafe(8)
    payload = f"{nonce}.{exp}"
    return f"{payload}.{_sign(payload)}"



def verify(ticket: str) -> bool:
    if not settings.ws_ticket_secret or not ticket:
        return False
    try:
        nonce, exp, sig = ticket.split(".")
    except ValueError:
        return False
    if not hmac.compare_digest(sig, _sign(f"{nonce}.{exp}")):
        return False
    return int(exp) > int(time.time())
