"""Pydantic DTOs for the transaction use cases."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.transaction import (
    Transaction,
    TransactionStatus,
    TransactionType,
)

MIN_TRANSACTION_AMOUNT = 0.01


class CreateTransactionDTO(BaseModel):
    """Input for CreateTransactionUseCase."""

    user_id: str = Field(min_length=1, max_length=128)
    monto: float = Field(ge=MIN_TRANSACTION_AMOUNT)
    tipo: TransactionType
    idempotency_key: str = Field(min_length=1, max_length=255)


class TransactionResponseDTO(BaseModel):
    """Output DTO representing a persisted transaction."""

    id: UUID
    user_id: str
    monto: float
    tipo: TransactionType
    status: TransactionStatus
    idempotency_key: str
    created_at: datetime
    processed_at: datetime | None

    @classmethod
    def from_domain(cls, transaction: Transaction) -> "TransactionResponseDTO":
        """Build a response DTO from a domain Transaction entity."""
        return cls(
            id=transaction.id,
            user_id=transaction.user_id,
            monto=transaction.monto,
            tipo=transaction.tipo,
            status=transaction.status,
            idempotency_key=transaction.idempotency_key,
            created_at=transaction.created_at,
            processed_at=transaction.processed_at,
        )


class TransactionListDTO(BaseModel):
    """Paginated list of transactions."""

    items: list[TransactionResponseDTO]
    total: int
    page: int
    limit: int


class ProcessTransactionAsyncDTO(BaseModel):
    """Input for ProcessTransactionAsyncUseCase."""

    user_id: str = Field(min_length=1, max_length=128)
    monto: float = Field(ge=MIN_TRANSACTION_AMOUNT)
    tipo: TransactionType
    idempotency_key: str = Field(min_length=1, max_length=255)
