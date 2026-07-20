"""Use case: create a transaction idempotently."""

import structlog

from app.application.dtos.transaction_dto import (
    CreateTransactionDTO,
    TransactionResponseDTO,
)
from app.domain.entities.transaction import Transaction
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort

log = structlog.get_logger(__name__)


class CreateTransactionUseCase:
    """Creates a transaction idempotently, based on an idempotency key."""

    def __init__(self, repo: TransactionRepositoryPort) -> None:
        self._repo = repo

    async def execute(
        self, dto: CreateTransactionDTO
    ) -> tuple[TransactionResponseDTO, bool]:
        """Create a transaction, or return the existing one for the same key."""
        log.info(
            "create_transaction.started",
            user_id=dto.user_id,
            idempotency_key=dto.idempotency_key,
        )

        existing = await self._repo.find_by_idempotency_key(dto.idempotency_key)
        if existing:
            log.info(
                "transaction.idempotent_hit",
                transaction_id=str(existing.id),
                idempotency_key=dto.idempotency_key,
            )
            return TransactionResponseDTO.from_domain(existing), False

        transaction = Transaction(
            user_id=dto.user_id,
            monto=dto.monto,
            tipo=dto.tipo,
            idempotency_key=dto.idempotency_key,
        )
        saved = await self._repo.save(transaction)
        log.info(
            "transaction.created", transaction_id=str(saved.id), user_id=dto.user_id
        )
        return TransactionResponseDTO.from_domain(saved), True
