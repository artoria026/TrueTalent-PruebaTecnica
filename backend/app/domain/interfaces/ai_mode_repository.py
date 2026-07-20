"""Port for the shared global AI mode toggle (real provider vs. forced mock)."""

from abc import ABC, abstractmethod


class AIModeRepositoryPort(ABC):
    """Abstract contract for persisting the global AI mode toggle."""

    @abstractmethod
    async def get_force_mock(self) -> bool:
        """Return whether AI calls are currently forced to the mock."""
        ...

    @abstractmethod
    async def set_force_mock(self, value: bool) -> None:
        """Persist whether AI calls should be forced to the mock."""
        ...
