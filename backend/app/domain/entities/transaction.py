"""Transaction domain entity — a plain dataclass."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class TransactionStatus(StrEnum):
    """Lifecycle states of a Transaction."""

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class TransactionType(StrEnum):
    """Supported transaction types."""

    DEPOSIT = "deposito"
    WITHDRAWAL = "retiro"
    TRANSFER = "transferencia"


@dataclass
class Transaction:
    """A financial transaction submitted by a user."""

    user_id: str
    monto: float
    tipo: TransactionType
    idempotency_key: str
    id: UUID = field(default_factory=uuid4)
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: datetime | None = None
