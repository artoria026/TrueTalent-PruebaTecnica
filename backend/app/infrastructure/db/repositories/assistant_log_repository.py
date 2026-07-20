"""Concrete SQLAlchemy implementation of AssistantLogRepositoryPort."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.assistant_log import AssistantLog
from app.domain.interfaces.assistant_log_repository import AssistantLogRepositoryPort
from app.infrastructure.db.models.assistant_log_model import AssistantLogModel

log = structlog.get_logger(__name__)


def _to_entity(model: AssistantLogModel) -> AssistantLog:
    return AssistantLog(
        id=model.id,
        user_id=model.user_id,
        prompt=model.prompt,
        response=model.response,
        model=model.model,
        status=model.status,
        created_at=model.created_at,
    )


def _to_model(entity: AssistantLog) -> AssistantLogModel:
    return AssistantLogModel(
        id=entity.id,
        user_id=entity.user_id,
        prompt=entity.prompt,
        response=entity.response,
        model=entity.model,
        status=entity.status,
        created_at=entity.created_at,
    )


class AssistantLogRepository(AssistantLogRepositoryPort):
    """Persists AssistantLog entities using SQLAlchemy against PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, log_entry: AssistantLog) -> AssistantLog:
        model = _to_model(log_entry)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        log.info("database.assistant_log_saved", log_id=str(model.id))
        return _to_entity(model)

    async def list_paginated(
        self, page: int, limit: int
    ) -> tuple[list[AssistantLog], int]:
        total_result = await self._session.execute(
            select(func.count()).select_from(AssistantLogModel)
        )
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        paged_stmt = (
            select(AssistantLogModel)
            .order_by(AssistantLogModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(paged_stmt)
        models = result.scalars().all()

        return [_to_entity(model) for model in models], total
