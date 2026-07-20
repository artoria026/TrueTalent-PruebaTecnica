"""FastAPI application entrypoint."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.middlewares.error_handler import register_exception_handlers
from app.api.middlewares.request_logger import RequestLoggerMiddleware
from app.api.v1.routers import assistant, rpa, transactions, websocket
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.security import configure_cors, configure_rate_limiting
from app.infrastructure.queue.redis_client import get_redis_client
from app.infrastructure.websocket.redis_listener import relay_transaction_updates

configure_logging()
log = structlog.get_logger(__name__)

# Only present inside Dockerfile.allinone; absent in local dev.
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application startup/shutdown hooks."""
    log.info("app.startup", env=get_settings().app_env)
    relay_task = asyncio.create_task(relay_transaction_updates(get_redis_client()))
    yield
    relay_task.cancel()
    log.info("app.shutdown")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    configure_cors(app, settings)
    configure_rate_limiting(app)
    app.add_middleware(RequestLoggerMiddleware)
    register_exception_handlers(app)

    app.include_router(transactions.router, prefix=settings.api_v1_prefix)
    app.include_router(assistant.router, prefix=settings.api_v1_prefix)
    app.include_router(rpa.router, prefix=settings.api_v1_prefix)
    app.include_router(websocket.router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Liveness probe used by Docker healthchecks."""
        return {"status": "ok"}

    if FRONTEND_DIST_DIR.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True),
            name="frontend",
        )

    return app


app = create_app()
