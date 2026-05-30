import hmac
import hashlib
from fastapi import Request, HTTPException
from app.core.config import settings

class WebhookSecurity:
    def __init__(self):
        self.secret_key = settings.webhook_secret.encode("utf-8")

    def verify(self, payload: bytes, signature: str):
        expected = hmac.new(
            self.secret_key,
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

security = WebhookSecurity()

async def verify_webhook_signature(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Webhook-Signature")

    if not signature or not security.verify(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    return body