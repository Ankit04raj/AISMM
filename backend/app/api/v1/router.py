"""API v1 Router aggregation."""

from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.accounts import router as accounts_router
from backend.app.api.v1.posts import router as posts_router
from backend.app.api.v1.metrics import router as metrics_router
from backend.app.api.v1.comments import router as comments_router
from backend.app.api.v1.webhooks import router as webhooks_router
from backend.app.api.v1.platforms import router as platforms_router
from backend.app.api.v1.content import router as content_router
from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.scheduling import router as scheduling_router
from backend.app.api.v1.intelligence import router as intelligence_router
from backend.app.api.v1.reply import router as reply_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(accounts_router)
api_v1_router.include_router(posts_router)
api_v1_router.include_router(content_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(scheduling_router)
api_v1_router.include_router(reply_router)
api_v1_router.include_router(intelligence_router)
api_v1_router.include_router(metrics_router)
api_v1_router.include_router(comments_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(platforms_router)

__all__ = ["api_v1_router"]
