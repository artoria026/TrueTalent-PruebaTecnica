"""Unit tests for ProcessTransactionAsyncUseCase."""

from unittest.mock import AsyncMock

import pytest

from app.application.dtos.transaction_dto import ProcessTransactionAsyncDTO
from app.application.use_cases.process_transaction_async import (
    ProcessTransactionAsyncUseCase,
)
from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.interfaces.queue_service import QueueServicePort
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort

QUEUE_NAME = "transactions"


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=TransactionRepositoryPort)


@pytest.fixture
def queue() -> AsyncMock:
    return AsyncMock(spec=QueueServicePort)


@pytest.fixture
def dto() -> ProcessTransactionAsyncDTO:
    return ProcessTransactionAsyncDTO(
        user_id="user-1",
        monto=50.0,
        tipo=TransactionType.WITHDRAWAL,
        idempotency_key="key-async-1",
    )


async def test_execute_with_new_transaction_enqueues_job(
    repo: AsyncMock, queue: AsyncMock, dto: ProcessTransactionAsyncDTO
) -> None:
    repo.find_by_idempotency_key.return_value = None
    repo.save.side_effect = lambda t: t

    use_case = ProcessTransactionAsyncUseCase(repo, queue, QUEUE_NAME)
    result = await use_case.execute(dto)

    assert result.status.value == "pending"
    queue.enqueue.assert_awaited_once()
    args, _ = queue.enqueue.call_args
    assert args[0] == QUEUE_NAME
    assert str(result.id) in args[1]


async def test_execute_with_duplicate_key_does_not_enqueue(
    repo: AsyncMock, queue: AsyncMock, dto: ProcessTransactionAsyncDTO
) -> None:
    existing = Transaction(
        user_id=dto.user_id,
        monto=dto.monto,
        tipo=dto.tipo,
        idempotency_key=dto.idempotency_key,
    )
    repo.find_by_idempotency_key.return_value = existing

    use_case = ProcessTransactionAsyncUseCase(repo, queue, QUEUE_NAME)
    result = await use_case.execute(dto)

    assert result.id == existing.id
    queue.enqueue.assert_not_awaited()
    repo.save.assert_not_awaited()
