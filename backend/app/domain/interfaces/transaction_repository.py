"""Port for transaction persistence."""

from abc import ABC, abstractmethod

from app.domain.entities.transaction import Transaction, TransactionStatus


class TransactionRepositoryPort(ABC):
    """Abstract contract for transaction persistence."""

    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        """Persist a new transaction and return it."""
        ...

    @abstractmethod
    async def find_by_id(self, transaction_id: str) -> Transaction | None:
        """Find a transaction by its id, or return None."""
        ...

    @abstractmethod
    async def find_by_idempotency_key(self, key: str) -> Transaction | None:
        """Find a transaction by its idempotency key, or return None."""
        ...

    @abstractmethod
    async def update_status(
        self, transaction_id: str, status: TransactionStatus
    ) -> Transaction:
        """Update the status of a transaction and return the updated entity."""
        ...

    @abstractmethod
    async def list_paginated(
        self, page: int, limit: int, status: str | None
    ) -> tuple[list[Transaction], int]:
        """Return a page of transactions and the total count matching the filter."""
        ...
