"""
AISMM Database Session Management

Async SQLAlchemy session management with connection pooling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool

from aismm.config import settings
from aismm.db.models import Base


# Global engine and session factory
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db() -> AsyncEngine:
    """Initialize database engine and create tables."""
    global _engine, _session_factory
    
    if _engine is not None:
        return _engine
    
    # Create async engine
    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    return _engine


async def create_tables() -> None:
    """Create all database tables."""
    engine = init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables (use with caution!)."""
    engine = init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if _session_factory is None:
        init_db()
    
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """Get a raw database session (for background tasks)."""
    if _session_factory is None:
        init_db()
    return _session_factory()


async def close_db() -> None:
    """Close database connections."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
    _engine = None
    _session_factory = None
