"""Shared pytest fixtures.

Every test that needs a database receives a completely isolated in-memory
SQLite instance via the ``session`` and ``client`` fixtures.  No test can
affect another test's data and no test modifies the developer database.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import create_app

# ---------------------------------------------------------------------------
# In-memory test database engine (one per test function via function scope)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture()
async def db_engine():
    """Yield a fresh async SQLite in-memory engine, then dispose it."""
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture()
async def session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session bound to the in-memory engine."""
    factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with factory() as s:
        yield s


@pytest_asyncio.fixture()
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    """Yield an HTTPX AsyncClient wired to a fresh in-memory test database.

    The FastAPI dependency ``get_session`` is overridden so every request
    within this client uses the same isolated engine.
    """
    factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as s:
            yield s

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Helper fixtures for authenticated test scenarios
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def registered_user(client: AsyncClient) -> dict:
    """Register a demo user and return the response JSON."""
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


@pytest_asyncio.fixture()
async def auth_token(client: AsyncClient, registered_user: dict) -> str:
    """Login and return a valid JWT bearer token string."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "securepassword123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest_asyncio.fixture()
async def auth_headers(auth_token: str) -> dict[str, str]:
    """Return Authorization headers for an authenticated request."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture()
async def sample_product(client: AsyncClient, auth_headers: dict[str, str]) -> dict:
    """Create a sample product and return its response JSON."""
    payload = {
        "name": "Widget Pro",
        "description": "A high-quality widget",
        "price": 29.99,
        "stock": 100,
        "category": "widgets",
    }
    response = await client.post("/api/v1/products", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()
