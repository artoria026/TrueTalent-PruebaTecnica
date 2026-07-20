"""Unit tests for the Transaction domain entity."""

from app.domain.entities.transaction import (
    Transaction,
    TransactionStatus,
    TransactionType,
)


def test_transaction_created_with_defaults_has_pending_status() -> None:
    transaction = Transaction(
        user_id="user-1",
        monto=10.0,
        tipo=TransactionType.DEPOSIT,
        idempotency_key="key-1",
    )

    assert transaction.status == TransactionStatus.PENDING
    assert transaction.processed_at is None
    assert transaction.id is not None


def test_transaction_created_with_same_inputs_generates_unique_ids() -> None:
    first = Transaction(
        user_id="user-1",
        monto=10.0,
        tipo=TransactionType.DEPOSIT,
        idempotency_key="k1",
    )
    second = Transaction(
        user_id="user-1",
        monto=10.0,
        tipo=TransactionType.DEPOSIT,
        idempotency_key="k2",
    )

    assert first.id != second.id
