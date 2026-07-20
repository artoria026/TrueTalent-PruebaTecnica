"""Pydantic DTOs for the AI assistant use cases."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.assistant_log import AssistantLog

MAX_PROMPT_LENGTH = 8000


class SummarizeTextDTO(BaseModel):
    """Input for SummarizeTextUseCase."""

    user_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=MAX_PROMPT_LENGTH)
    allow_fallback: bool = True


class SummarizeTextResponseDTO(BaseModel):
    """Output DTO representing the result of a summarization request."""

    id: UUID
    user_id: str
    summary: str
    model: str
    created_at: datetime

    @classmethod
    def from_domain(cls, log_entry: AssistantLog) -> "SummarizeTextResponseDTO":
        """Build a response DTO from a domain AssistantLog entity."""
        return cls(
            id=log_entry.id,
            user_id=log_entry.user_id,
            summary=log_entry.response,
            model=log_entry.model,
            created_at=log_entry.created_at,
        )
