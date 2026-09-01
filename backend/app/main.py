"""FastAPI application factory and main entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.config import get_settings
from backend.app.db.session import init_db, close_db, get_db, check_db_connection
from backend.app.core.errors import (
    AISMMError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    PlatformError,
)
from backend.app.core.schemas.post import (
    CreatePostRequest,
    PostResponse,
    PostListResponse,
    PostMetrics,
)
from backend.app.core.schemas.account import (
    ConnectAccountRequest,
    SocialAccountResponse,
    SocialAccountListResponse,
    AccountInsights,
    UpdateAccountRequest,
    DisconnectAccountResponse,
    AccountProfile,
)
from backend.app.core.schemas.auth import (
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    OAuthTokenResponse,
)
from backend.app.services.post_service import PostService
from backend.app.services.account_service import AccountService
from backend.app.services.metrics_service import MetricsService
from backend.app.core.platform_adapters import PlatformRegistry


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    init_db()
    print(f"🚀 AISMM Backend started on {settings.HOST}:{settings.PORT}")
    print(f"📚 Documentation: http://{settings.HOST}:{settings.PORT}/docs")

    # Verify DB connection
    connected = await check_db_connection()
    if not connected:
        print("⚠️  Database connection failed - check configuration")

    yield

    # Shutdown
    await close_db()
    print("👋 AISMM Backend shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="AISMM - AI Social Media Manager",
        description="Backend API for multi-platform social media management with AI",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(AISMMError)
    async def aismm_error_handler(request: Request, exc: AISMMError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "NOT_FOUND", "message": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "VALIDATION_ERROR", "message": str(exc), "details": exc.details},
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "AUTHENTICATION_ERROR", "message": str(exc)},
        )

    @app.exception_handler(PlatformError)
    async def platform_error_handler(request: Request, exc: PlatformError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "PLATFORM_ERROR", "message": str(exc), "platform": exc.platform},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "VALIDATION_ERROR", "message": "Invalid request", "details": exc.errors()},
        )

    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        db_healthy = await check_db_connection()
        return {
            "status": "healthy" if db_healthy else "degraded",
            "service": "aismm-backend",
            "version": "0.1.0",
            "database": "connected" if db_healthy else "disconnected",
            "platforms": PlatformRegistry.list_platforms(),
        }

    # Root
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": "AISMM Backend",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
        }

    # ==================== POST ROUTES ====================

    @app.post(
        "/api/v1/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Posts"],
    )
    async def create_post(
        request: CreatePostRequest,
        db=Depends(get_db),
    ):
        """Create and publish a post."""
        # Get current user (placeholder - would come from auth)
        user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

        service = PostService(db)
        return await service.create_post(user_id, request)

    @app.get(
        "/api/v1/posts",
        response_model=PostListResponse,
        tags=["Posts"],
    )
    async def list_posts(
        page: int = 1,
        page_size: int = 20,
        platform: str = None,
        status: str = None,
        db=Depends(get_db),
    ):
        """List posts with pagination."""
        user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

        service = PostService(db)
        result = await service.get_posts(user_id, page, page_size, status, platform)

        return PostListResponse(
            posts=[
                PostResponse(
                    id=str(p.id),
                    platform=p.publications[0].platform if p.publications else "unknown",
                    permalink=p.publications[0].permalink if p.publications else None,
                    media_type=p.publications[0].media_type if p.publications else None,
                    published_at=p.publications[0].published_at if p.publications else None,
                    scheduled_at=p.publications[0].scheduled_at if p.publications else None,
                    status=p.status,
                )
                for p in result["posts"]
            ],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            has_next=result["has_next"],
        )

    @app.get(
        "/api/v1/posts/{post_id}",
        response_model=PostResponse,
        tags=["Posts"],
    )
    async def get_post(post_id: str, db=Depends(get_db)):
        """Get a single post by ID."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = PostService(db)
        post = await service.get_post(UUID(post_id), UUID(user_id))
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        publication = post.publications[0] if post.publications else None
        return PostResponse(
            id=str(post.id),
            platform=publication.platform if publication else "unknown",
            permalink=publication.permalink if publication else None,
            media_type=publication.media_type if publication else None,
            published_at=publication.published_at if publication else None,
            scheduled_at=publication.scheduled_at if publication else None,
            status=post.status,
        )

    @app.delete(
        "/api/v1/posts/{post_id}",
        tags=["Posts"],
    )
    async def delete_post(post_id: str, db=Depends(get_db)):
        """Delete a post."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = PostService(db)
        deleted = await service.delete_post(UUID(post_id), UUID(user_id))
        if not deleted:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"deleted": True, "id": post_id}

    @app.get(
        "/api/v1/posts/{post_id}/metrics",
        response_model=PostMetrics,
        tags=["Posts"],
    )
    async def get_post_metrics(post_id: str, db=Depends(get_db)):
        """Get metrics for a post."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = PostService(db)
        metrics = await service.get_post_metrics(UUID(post_id), UUID(user_id))
        if not metrics:
            raise HTTPException(status_code=404, detail="Metrics not found")
        return metrics

    @app.post(
        "/api/v1/posts/schedule",
        tags=["Posts"],
    )
    async def schedule_post(
        request: CreatePostRequest,
        db=Depends(get_db),
    ):
        """Schedule a post for future publishing."""
        request.publish_now = False
        return await create_post(request, db)

    @app.get(
        "/api/v1/posts/scheduled",
        tags=["Posts"],
    )
    async def get_scheduled_posts(db=Depends(get_db)):
        """Get all scheduled posts."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = PostService(db)
        posts = await service.get_scheduled_posts(UUID(user_id))
        return {"posts": [str(p.id) for p in posts]}

    @app.delete(
        "/api/v1/posts/{post_id}/schedule",
        tags=["Posts"],
    )
    async def cancel_scheduled_post(post_id: str, db=Depends(get_db)):
        """Cancel a scheduled post."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = PostService(db)
        cancelled = await service.cancel_scheduled_post(UUID(post_id), UUID(user_id))
        if not cancelled:
            raise HTTPException(status_code=404, detail="Scheduled post not found")
        return {"cancelled": True, "id": post_id}

    # ==================== ACCOUNT ROUTES ====================

    @app.post(
        "/api/v1/auth/oauth/init",
        response_model=OAuthInitResponse,
        tags=["Authentication"],
    )
    async def oauth_init(request: OAuthInitRequest):
        """Initiate OAuth flow for a platform."""
        if request.platform not in PlatformRegistry.list_platforms():
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

        adapter = PlatformRegistry.get_adapter(request.platform)
        auth_url, state = adapter.auth.get_authorization_url()

        return OAuthInitResponse(
            authorization_url=auth_url,
            state=state,
            expires_at=None,  # Would calculate from state store
        )

    @app.post(
        "/api/v1/auth/oauth/callback",
        response_model=OAuthTokenResponse,
        tags=["Authentication"],
    )
    async def oauth_callback(request: OAuthCallbackRequest):
        """Handle OAuth callback."""
        if request.platform not in PlatformRegistry.list_platforms():
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

        adapter = PlatformRegistry.get_adapter(request.platform)
        token_response = await adapter.auth.exchange_code(
            code=request.code,
            redirect_uri=request.redirect_uri,
        )

        return OAuthTokenResponse(**token_response)

    @app.post(
        "/api/v1/accounts/connect",
        response_model=SocialAccountResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["Accounts"],
    )
    async def connect_account(
        request: ConnectAccountRequest,
        db=Depends(get_db),
    ):
        """Connect a social account."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        return await service.connect_account(UUID(user_id), request)

    @app.get(
        "/api/v1/accounts",
        response_model=SocialAccountListResponse,
        tags=["Accounts"],
    )
    async def list_accounts(
        platform: str = None,
        db=Depends(get_db),
    ):
        """List connected accounts."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        accounts = await service.get_account_responses(UUID(user_id), platform)
        return SocialAccountListResponse(accounts=accounts, total=len(accounts))

    @app.get(
        "/api/v1/accounts/{account_id}",
        response_model=SocialAccountResponse,
        tags=["Accounts"],
    )
    async def get_account(account_id: str, db=Depends(get_db)):
        """Get a specific account."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        account = await service.get_account(UUID(account_id), UUID(user_id))
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return service._to_response(account)

    @app.patch(
        "/api/v1/accounts/{account_id}",
        response_model=SocialAccountResponse,
        tags=["Accounts"],
    )
    async def update_account(
        account_id: str,
        request: UpdateAccountRequest,
        db=Depends(get_db),
    ):
        """Update account settings."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        account = await service.update_account(UUID(account_id), UUID(user_id), request)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    @app.delete(
        "/api/v1/accounts/{account_id}",
        response_model=DisconnectAccountResponse,
        tags=["Accounts"],
    )
    async def disconnect_account(account_id: str, db=Depends(get_db)):
        """Disconnect a social account."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        return await service.disconnect_account(UUID(account_id), UUID(user_id))

    @app.post(
        "/api/v1/accounts/{account_id}/refresh",
        tags=["Accounts"],
    )
    async def refresh_account_token(account_id: str, db=Depends(get_db)):
        """Refresh account access token."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        success = await service.refresh_token(UUID(account_id), UUID(user_id))
        return {"success": success}

    @app.get(
        "/api/v1/accounts/{account_id}/insights",
        response_model=AccountInsights,
        tags=["Accounts"],
    )
    async def get_account_insights(account_id: str, db=Depends(get_db)):
        """Get account insights."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        insights = await service.get_account_insights(UUID(account_id), UUID(user_id))
        if not insights:
            raise HTTPException(status_code=404, detail="Insights not available")
        return insights

    @app.get(
        "/api/v1/accounts/{account_id}/profile",
        response_model=AccountProfile,
        tags=["Accounts"],
    )
    async def get_account_profile(account_id: str, db=Depends(get_db)):
        """Get account profile."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = AccountService(db)
        profile = await service.get_account_profile(UUID(account_id), UUID(user_id))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not available")
        return profile

    # ==================== METRICS ROUTES ====================

    @app.get(
        "/api/v1/metrics/overview",
        tags=["Metrics"],
    )
    async def get_overview(
        days: int = 30,
        db=Depends(get_db),
    ):
        """Get user metrics overview."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = MetricsService(db)
        return await service.get_user_overview(UUID(user_id), days)

    @app.get(
        "/api/v1/metrics/top-posts",
        tags=["Metrics"],
    )
    async def get_top_posts(
        metric: str = "impressions",
        limit: int = 10,
        days: int = 30,
        db=Depends(get_db),
    ):
        """Get top performing posts."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = MetricsService(db)
        return await service.get_top_posts(UUID(user_id), metric, limit, days)

    @app.get(
        "/api/v1/metrics/engagement-trends",
        tags=["Metrics"],
    )
    async def get_engagement_trends(
        days: int = 30,
        db=Depends(get_db),
    ):
        """Get engagement trends."""
        user_id = "00000000-0000-0000-0000-000000000001"
        from uuid import UUID

        service = MetricsService(db)
        return await service.get_engagement_trends(UUID(user_id), days)

    # ==================== PLATFORM ROUTES ====================

    @app.get(
        "/api/v1/platforms",
        tags=["Platforms"],
    )
    async def list_platforms():
        """List supported platforms."""
        return {"platforms": PlatformRegistry.list_platforms()}

    @app.get(
        "/api/v1/platforms/{platform}/capabilities",
        tags=["Platforms"],
    )
    async def get_platform_capabilities(platform: str):
        """Get platform capabilities."""
        if platform not in PlatformRegistry.list_platforms():
            raise HTTPException(status_code=404, detail=f"Platform not found: {platform}")

        adapter = PlatformRegistry.get_adapter(platform)
        caps = await adapter.get_capabilities()
        return {"platform": platform, "capabilities": list(caps)}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )