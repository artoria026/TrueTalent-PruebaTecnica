"""RpaExtraction domain entity — a plain dataclass."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class RpaExtraction:
    """A paragraph the RPA scraped from a public site, with its source."""

    term: str
    paragraph: str
    source_url: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
