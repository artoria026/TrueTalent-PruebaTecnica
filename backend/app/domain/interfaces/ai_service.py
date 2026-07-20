"""Port for AI text-summarization capabilities."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AISummaryResult:
    """The summary text plus the model that actually produced it."""

    text: str
    model: str


class AIServicePort(ABC):
    """Abstract contract for an AI text service."""

    @abstractmethod
    async def summarize(self, text: str) -> AISummaryResult:
        """Return a summary of the given text and the model that produced it."""
        ...
