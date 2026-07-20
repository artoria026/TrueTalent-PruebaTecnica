"""Use case: create a transaction and enqueue it for async processing."""

import json

import structlog

from app.application.dtos.transaction_dto import (
    ProcessTransactionAsyncDTO,
    TransactionResponseDTO,
)
from app.domain.entities.transaction import Transaction
from app.domain.interfaces.queue_service import QueueServicePort
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort

log = structlog.get_logger(__name__)


class ProcessTransactionAsyncUseCase:
    """Creates a transaction idempotently and enqueues it for background processing."""

    def __init__(
        self,
        repo: TransactionRepositoryPort,
        queue: QueueServicePort,
        queue_name: str,
    ) -> None:
        self._repo = repo
        self._queue = queue
        self._queue_name = queue_name

    async def execute(self, dto: ProcessTransactionAsyncDTO) -> TransactionResponseDTO:
        """Persist the transaction as PENDING and push its id onto the queue."""
        log.info(
            "process_transaction_async.started",
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
            return TransactionResponseDTO.from_domain(existing)

        transaction = Transaction(
            user_id=dto.user_id,
            monto=dto.monto,
            tipo=dto.tipo,
            idempotency_key=dto.idempotency_key,
        )
        saved = await self._repo.save(transaction)

        payload = json.dumps({"transaction_id": str(saved.id)})
        await self._queue.enqueue(self._queue_name, payload)
        log.info("transaction.queued", transaction_id=str(saved.id))

        return TransactionResponseDTO.from_domain(saved)
