"""TestForge Store API — main application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, orders, products
from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Application lifespan: initialise the database on startup."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Factory function that creates and configures the FastAPI application.

    Using a factory makes it straightforward to swap configuration in tests.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A fictional demonstration API built for the TestForge SDET portfolio project. "
            "Not a real commerce service. Do not use real customer data."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # permissive for local demo; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health endpoint at the root level
    @app.get("/health", tags=["health"], summary="Health check")
    async def health() -> dict[str, Any]:
        """Return the application health status."""
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    # Versioned API routers
    app.include_router(products.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(orders.router, prefix="/api/v1")

    return app


app = create_app()
