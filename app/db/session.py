# app/db/session.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from app.config import get_settings


# SQLAlchemy base class for models
Base = declarative_base()

# Global engine and session factory
_engine = None
_session_factory = None


async def init_db(database_url: str) -> None:
    """
    Initialize database engine and session factory.
    Call this during application startup.
    """

    global _engine, _session_factory

    settings = get_settings()

    # Create async engine with connection pooling
    _engine = create_async_engine(
        str(database_url),
        echo=settings.debug,    # Log SQL in debug mode
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Create session factory
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

async def close_db() -> None:
    """
    Close database connections.
    Call this during application shutdown.
    """

    global _engine

    if _engine:
        await _engine.dispose()
    
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Session is automatically closed after the request.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
        ...
    """

    if _session_factory is None:
        raise RuntimeError("Database not initialized")
        
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise