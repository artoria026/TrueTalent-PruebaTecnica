"""HTTP request/response Pydantic schemas for the assistant router."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

MAX_PROMPT_LENGTH = 8000
DEFAULT_PAGE = 1
DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


class SummarizeTextRequest(BaseModel):
    """HTTP request body to summarize a piece of text."""

    user_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=MAX_PROMPT_LENGTH)
    allow_fallback: bool = Field(
        default=True,
        description="Fall back to a simulated summary if the AI quota is exhausted.",
    )


class SummarizeTextResponse(BaseModel):
    """HTTP response body with the generated summary."""

    id: UUID
    user_id: str
    summary: str
    model: str
    created_at: datetime


class AssistantLogResponse(BaseModel):
    """A past assistant interaction; summary is null when it failed."""

    id: UUID
    user_id: str
    prompt: str
    summary: str | None
    model: str
    status: str
    created_at: datetime


class AssistantLogListResponse(BaseModel):
    """HTTP response body for a paginated list of assistant interactions."""

    items: list[AssistantLogResponse]
    total: int
    page: int
    limit: int


class AiModeResponse(BaseModel):
    """HTTP response body reporting the current global AI mode."""

    force_mock: bool


class SetAiModeRequest(BaseModel):
    """HTTP request body to toggle the global AI mode."""

    force_mock: bool
