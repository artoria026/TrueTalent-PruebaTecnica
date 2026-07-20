"""Concrete SQLAlchemy implementation of TransactionRepositoryPort."""

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import (
    Transaction,
    TransactionStatus,
    TransactionType,
)
from app.domain.exceptions import TransactionNotFoundError
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort
from app.infrastructure.db.models.transaction_model import TransactionModel

log = structlog.get_logger(__name__)


def _to_entity(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        user_id=model.user_id,
        monto=model.monto,
        tipo=TransactionType(model.tipo),
        idempotency_key=model.idempotency_key,
        status=TransactionStatus(model.status),
        created_at=model.created_at,
        processed_at=model.processed_at,
    )


def _to_model(entity: Transaction) -> TransactionModel:
    return TransactionModel(
        id=entity.id,
        user_id=entity.user_id,
        monto=entity.monto,
        tipo=entity.tipo.value,
        status=entity.status.value,
        idempotency_key=entity.idempotency_key,
        created_at=entity.created_at,
        processed_at=entity.processed_at,
    )


class TransactionRepository(TransactionRepositoryPort):
    """Persists Transaction entities using SQLAlchemy against PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, transaction: Transaction) -> Transaction:
        model = _to_model(transaction)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        log.info(
            "database.transaction_saved",
            transaction_id=str(model.id),
            user_id=model.user_id,
        )
        return _to_entity(model)

    async def find_by_id(self, transaction_id: str) -> Transaction | None:
        model = await self._session.get(TransactionModel, UUID(transaction_id))
        return _to_entity(model) if model else None

    async def find_by_idempotency_key(self, key: str) -> Transaction | None:
        stmt = select(TransactionModel).where(TransactionModel.idempotency_key == key)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def update_status(
        self, transaction_id: str, status: TransactionStatus
    ) -> Transaction:
        model = await self._session.get(TransactionModel, UUID(transaction_id))
        if model is None:
            raise TransactionNotFoundError(transaction_id)

        model.status = status.value
        if status in (TransactionStatus.PROCESSED, TransactionStatus.FAILED):
            model.processed_at = datetime.now(UTC)

        await self._session.commit()
        await self._session.refresh(model)
        log.info(
            "database.transaction_status_updated",
            transaction_id=transaction_id,
            status=status.value,
        )
        return _to_entity(model)

    async def list_paginated(
        self, page: int, limit: int, status: str | None
    ) -> tuple[list[Transaction], int]:
        base_stmt = select(TransactionModel)
        count_stmt = select(func.count()).select_from(TransactionModel)

        if status is not None:
            base_stmt = base_stmt.where(TransactionModel.status == status)
            count_stmt = count_stmt.where(TransactionModel.status == status)

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        paged_stmt = (
            base_stmt.order_by(TransactionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(paged_stmt)
        models = result.scalars().all()

        return [_to_entity(model) for model in models], total
