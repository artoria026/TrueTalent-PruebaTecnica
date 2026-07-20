"""Pydantic DTOs for the RPA extraction use case."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.rpa_extraction import RpaExtraction

MAX_TERM_LENGTH = 255
MAX_PARAGRAPH_LENGTH = 8000
MAX_SOURCE_URL_LENGTH = 2048


class CreateRpaExtractionDTO(BaseModel):
    """Input for CreateRpaExtractionUseCase."""

    term: str = Field(min_length=1, max_length=MAX_TERM_LENGTH)
    paragraph: str = Field(min_length=1, max_length=MAX_PARAGRAPH_LENGTH)
    source_url: str = Field(min_length=1, max_length=MAX_SOURCE_URL_LENGTH)


class RpaExtractionResponseDTO(BaseModel):
    """Output DTO representing a persisted RPA extraction."""

    id: UUID
    term: str
    paragraph: str
    source_url: str
    created_at: datetime

    @classmethod
    def from_domain(cls, extraction: RpaExtraction) -> "RpaExtractionResponseDTO":
        """Build a response DTO from a domain RpaExtraction entity."""
        return cls(
            id=extraction.id,
            term=extraction.term,
            paragraph=extraction.paragraph,
            source_url=extraction.source_url,
            created_at=extraction.created_at,
        )
