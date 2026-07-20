"""Security-related middleware: CORS, security headers, and rate limiting."""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings


def _rate_limit_key(request: Request) -> str:
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security-related HTTP response headers."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS using explicit allowed origins (never '*' in production)."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


def configure_rate_limiting(app: FastAPI) -> None:
    """Attach slowapi-based rate limiting to the application."""
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )
    app.add_middleware(SecurityHeadersMiddleware)
