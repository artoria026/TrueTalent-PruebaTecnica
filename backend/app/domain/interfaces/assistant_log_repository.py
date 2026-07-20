"""Port for assistant log persistence."""

from abc import ABC, abstractmethod

from app.domain.entities.assistant_log import AssistantLog


class AssistantLogRepositoryPort(ABC):
    """Abstract contract for assistant log persistence."""

    @abstractmethod
    async def save(self, log_entry: AssistantLog) -> AssistantLog:
        """Persist a new assistant log entry and return it."""
        ...

    @abstractmethod
    async def list_paginated(
        self, page: int, limit: int
    ) -> tuple[list[AssistantLog], int]:
        """Return a page of assistant logs and the total count, newest first."""
        ...
