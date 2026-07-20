"""Port for RPA extraction persistence."""

from abc import ABC, abstractmethod

from app.domain.entities.rpa_extraction import RpaExtraction


class RpaExtractionRepositoryPort(ABC):
    """Abstract contract for RPA extraction persistence."""

    @abstractmethod
    async def save(self, extraction: RpaExtraction) -> RpaExtraction:
        """Persist a new RPA extraction and return it."""
        ...

    @abstractmethod
    async def list_paginated(
        self, page: int, limit: int
    ) -> tuple[list[RpaExtraction], int]:
        """Return a page of RPA extractions and the total count, newest first."""
        ...
