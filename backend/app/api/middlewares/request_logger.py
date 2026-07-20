"""Request/response logging middleware."""

import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger(__name__)

_MILLISECONDS_PER_SECOND = 1000


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Logs every incoming HTTP request and its response status/duration."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started_at = time.perf_counter()
        log.info("http.request.started", method=request.method, path=request.url.path)

        response = await call_next(request)

        duration_ms = (time.perf_counter() - started_at) * _MILLISECONDS_PER_SECOND
        log.info(
            "http.request.finished",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
