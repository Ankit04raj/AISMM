"""FastAPI application factory and main entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import time
import uuid
import asyncio

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.config import get_settings
from backend.app.db.session import init_db, close_db, check_db_connection
from backend.app.services.scheduling_service import run_scheduler_background_worker
from backend.app.core.errors import (
    AISMMError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    PlatformError,
    RateLimitError,
)
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.api.v1.router import api_v1_router
from backend.app.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager starting the background scheduler worker."""
    setup_logging()
    init_db()
    await check_db_connection()

    # Start automated scheduled-post background execution loop
    scheduler_task = asyncio.create_task(run_scheduler_background_worker(interval_seconds=1.0))
    try:
        yield
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        await close_db()


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

    # Observability & Correlation ID Middleware
    @app.middleware("http")
    async def add_process_time_and_correlation_header(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    # Exception handlers
    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": exc.message or "Too many requests. Please slow down.",
                "details": exc.details,
            },
            headers={"Retry-After": str(exc.details.get("retry_after", 60)) if exc.details else "60"},
        )
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
            content={"error": "NOT_FOUND", "message": str(exc), "details": exc.details},
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
            content={"error": "AUTHENTICATION_ERROR", "message": str(exc), "details": exc.details},
        )

    @app.exception_handler(PlatformError)
    async def platform_error_handler(request: Request, exc: PlatformError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "PLATFORM_ERROR", "message": str(exc), "platform": exc.platform, "details": exc.details},
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

    # Include API v1 router
    app.include_router(api_v1_router)

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
