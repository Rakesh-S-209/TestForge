"""Database engine and session factory.

Uses SQLAlchemy async with SQLite (via aiosqlite).
Tests override the engine via dependency injection so they always use
an isolated in-memory database and never touch developer data.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Default (application) engine
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


async def init_db(bind_engine=None) -> None:  # type: ignore[assignment]
    """Create all tables.  Accepts an explicit engine for testing."""
    target = bind_engine or engine
    async with target.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
