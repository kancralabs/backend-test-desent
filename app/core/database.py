"""Async SQLAlchemy database configuration and session management"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,  # Verify connections before use (prevents stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: Prevents lazy loading after commit (N+1 queries)
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI route injection.

    Provides async database session with automatic cleanup.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
