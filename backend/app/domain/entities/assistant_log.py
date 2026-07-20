"""AssistantLog domain entity — a plain dataclass."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

ASSISTANT_LOG_STATUS_COMPLETED = "completed"
ASSISTANT_LOG_STATUS_FAILED = "failed"


@dataclass
class AssistantLog:
    """A record of a summarize request; response is null until it completes."""

    user_id: str
    prompt: str
    model: str
    response: str | None = None
    status: str = ASSISTANT_LOG_STATUS_COMPLETED
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
