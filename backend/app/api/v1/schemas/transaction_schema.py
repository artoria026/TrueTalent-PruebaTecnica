"""HTTP request/response Pydantic schemas for the transactions router."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.transaction import TransactionStatus, TransactionType

MIN_TRANSACTION_AMOUNT = 0.01
DEFAULT_PAGE = 1
DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


class CreateTransactionRequest(BaseModel):
    """HTTP request body to create a transaction."""

    user_id: str = Field(min_length=1, max_length=128)
    monto: float = Field(ge=MIN_TRANSACTION_AMOUNT)
    tipo: TransactionType
    idempotency_key: str = Field(min_length=1, max_length=255)


class TransactionResponse(BaseModel):
    """HTTP response body for a single transaction."""

    id: UUID
    user_id: str
    monto: float
    tipo: TransactionType
    status: TransactionStatus
    idempotency_key: str
    created_at: datetime
    processed_at: datetime | None


class TransactionListResponse(BaseModel):
    """HTTP response body for a paginated list of transactions."""

    items: list[TransactionResponse]
    total: int
    page: int
    limit: int
