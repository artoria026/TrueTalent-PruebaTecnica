"""Shared HTTP error response schema."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Body of the `error` field in every error response."""

    type: str
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Consistent error envelope returned by every failed request."""

    error: ErrorDetail
