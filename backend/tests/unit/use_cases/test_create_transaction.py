"""Unit tests for CreateTransactionUseCase."""

from unittest.mock import AsyncMock

import pytest

from app.application.dtos.transaction_dto import CreateTransactionDTO
from app.application.use_cases.create_transaction import CreateTransactionUseCase
from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=TransactionRepositoryPort)


@pytest.fixture
def dto() -> CreateTransactionDTO:
    return CreateTransactionDTO(
        user_id="user-1",
        monto=100.0,
        tipo=TransactionType.DEPOSIT,
        idempotency_key="key-1",
    )


async def test_execute_with_duplicate_key_returns_existing(
    repo: AsyncMock, dto: CreateTransactionDTO
) -> None:
    existing = Transaction(
        user_id=dto.user_id,
        monto=dto.monto,
        tipo=dto.tipo,
        idempotency_key=dto.idempotency_key,
    )
    repo.find_by_idempotency_key.return_value = existing

    use_case = CreateTransactionUseCase(repo)
    result, created = await use_case.execute(dto)

    assert created is False
    assert result.id == existing.id
    repo.save.assert_not_awaited()


async def test_execute_with_new_key_saves_and_returns_created(
    repo: AsyncMock, dto: CreateTransactionDTO
) -> None:
    repo.find_by_idempotency_key.return_value = None
    repo.save.side_effect = lambda t: t

    use_case = CreateTransactionUseCase(repo)
    result, created = await use_case.execute(dto)

    assert created is True
    assert result.user_id == dto.user_id
    assert result.idempotency_key == dto.idempotency_key
    repo.save.assert_awaited_once()
