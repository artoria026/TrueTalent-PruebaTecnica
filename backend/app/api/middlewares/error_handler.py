"""Global exception handling for the FastAPI application."""

from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AIQuotaExceededError,
    DomainError,
    QueuePublishError,
    RateLimitExceededError,
    TransactionConflictError,
    TransactionNotFoundError,
)

log = structlog.get_logger(__name__)

_DOMAIN_ERROR_STATUS_MAP: dict[type[DomainError], int] = {
    TransactionNotFoundError: status.HTTP_404_NOT_FOUND,
    TransactionConflictError: status.HTTP_409_CONFLICT,
    RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    AIQuotaExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
    QueuePublishError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

_DEFAULT_DOMAIN_ERROR_STATUS = status.HTTP_400_BAD_REQUEST


def _error_body(exc_type: str, message: str, code: str, **extra: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error": {"type": exc_type, "message": message, "code": code}
    }
    body["error"].update(extra)
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers that produce a consistent error shape."""

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        http_status = _DOMAIN_ERROR_STATUS_MAP.get(
            type(exc), _DEFAULT_DOMAIN_ERROR_STATUS
        )
        log.warning(
            "request.domain_error",
            path=request.url.path,
            error_type=type(exc).__name__,
            code=exc.code,
            message=exc.message,
        )
        extra: dict[str, Any] = {}
        if (
            isinstance(exc, AIQuotaExceededError)
            and exc.retry_after_seconds is not None
        ):
            extra["retry_after_seconds"] = exc.retry_after_seconds

        return JSONResponse(
            status_code=http_status,
            content=_error_body(type(exc).__name__, exc.message, exc.code, **extra),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        log.warning(
            "request.validation_error", path=request.url.path, errors=exc.errors()
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "RequestValidationError",
                "Invalid request payload",
                "VALIDATION_ERROR",
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        log.error(
            "request.unhandled_error",
            path=request.url.path,
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                "InternalServerError",
                "An unexpected error occurred",
                "INTERNAL_SERVER_ERROR",
            ),
        )
