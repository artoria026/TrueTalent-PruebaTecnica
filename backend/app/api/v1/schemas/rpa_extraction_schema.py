"""HTTP request/response Pydantic schemas for the RPA extractions router."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

MAX_TERM_LENGTH = 255
MAX_PARAGRAPH_LENGTH = 8000
MAX_SOURCE_URL_LENGTH = 2048
DEFAULT_PAGE = 1
DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


class CreateRpaExtractionRequest(BaseModel):
    """HTTP request body to record a paragraph the RPA scraped."""

    term: str = Field(min_length=1, max_length=MAX_TERM_LENGTH)
    paragraph: str = Field(min_length=1, max_length=MAX_PARAGRAPH_LENGTH)
    source_url: str = Field(min_length=1, max_length=MAX_SOURCE_URL_LENGTH)


class RpaExtractionResponse(BaseModel):
    """HTTP response body for a single RPA extraction."""

    id: UUID
    term: str
    paragraph: str
    source_url: str
    created_at: datetime


class RpaExtractionListResponse(BaseModel):
    """HTTP response body for a paginated list of RPA extractions."""

    items: list[RpaExtractionResponse]
    total: int
    page: int
    limit: int
