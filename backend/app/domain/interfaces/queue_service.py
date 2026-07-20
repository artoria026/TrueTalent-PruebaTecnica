"""Port for background job queueing."""

from abc import ABC, abstractmethod


class QueueServicePort(ABC):
    """Abstract contract for an async job queue."""

    @abstractmethod
    async def enqueue(self, queue_name: str, payload: str) -> None:
        """Push a payload onto the named queue."""
        ...

    @abstractmethod
    async def dequeue(self, queue_name: str) -> str | None:
        """Pop a payload from the named queue, or return None if empty."""
        ...
