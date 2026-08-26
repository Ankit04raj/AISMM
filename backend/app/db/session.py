"""Database session management and initialization."""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text

from backend.app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# Global engine and session factory
engine = None
async_session_factory = None


def init_db() -> None:
    """Initialize database engine and session factory."""
    global engine, async_session_factory

    settings = get_settings()
    database_url = settings.DATABASE_URL

    # Convert postgresql:// to postgresql+asyncpg:// for async
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(
        database_url,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )

    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    if async_session_factory is None:
        init_db()

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session outside of FastAPI."""
    if async_session_factory is None:
        init_db()

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def check_db_connection() -> bool:
    """Check if database is accessible."""
    try:
        async with get_db_context() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# Event listeners for connection pool monitoring
@event.listens_for(engine, "checkout") if engine else lambda *args, **kwargs: None
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout."""
    pass


@event.listens_for(engine, "checkin") if engine else lambda *args, **kwargs: None
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin."""
    pass


async def create_tables() -> None:
    """Create all tables (for development/testing)."""
    if engine is None:
        init_db()

    # Import all models to register them
    from backend.app.db import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all tables (for testing)."""
    if engine is None:
        init_db()

    from backend.app.db import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)