"""Webhooks API router."""

from fastapi import APIRouter, Request, HTTPException, Query, Response, status
from typing import Optional

from backend.app.config import get_settings
from backend.app.core.platform_adapters.instagram.webhook import InstagramWebhookHandler

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
settings = get_settings()


def get_instagram_webhook_handler() -> InstagramWebhookHandler:
    return InstagramWebhookHandler(
        app_secret=settings.INSTAGRAM_CLIENT_SECRET or settings.WEBHOOK_SECRET,
        verify_token=getattr(settings, "INSTAGRAM_WEBHOOK_VERIFY_TOKEN", settings.WEBHOOK_SECRET),
        callback_url=f"{settings.FRONTEND_URL}/api/v1/webhooks/instagram",
    )


@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
):
    """Instagram webhook subscription challenge verification."""
    handler = get_instagram_webhook_handler()
    challenge = handler.verify_challenge(hub_mode or "", hub_challenge or "", hub_verify_token or "")
    if challenge:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/instagram")
async def handle_instagram_webhook(request: Request):
    """Instagram webhook event receiver with signature validation."""
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    handler = get_instagram_webhook_handler()
    if signature and not handler.verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    result = await handler.handle_webhook_request(
        method="POST",
        query_params={},
        headers=dict(request.headers),
        body=body,
    )
    return result
