"""Concrete SQLAlchemy implementation of RpaExtractionRepositoryPort."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.rpa_extraction import RpaExtraction
from app.domain.interfaces.rpa_extraction_repository import (
    RpaExtractionRepositoryPort,
)
from app.infrastructure.db.models.rpa_extraction_model import RpaExtractionModel

log = structlog.get_logger(__name__)


def _to_entity(model: RpaExtractionModel) -> RpaExtraction:
    return RpaExtraction(
        id=model.id,
        term=model.term,
        paragraph=model.paragraph,
        source_url=model.source_url,
        created_at=model.created_at,
    )


def _to_model(entity: RpaExtraction) -> RpaExtractionModel:
    return RpaExtractionModel(
        id=entity.id,
        term=entity.term,
        paragraph=entity.paragraph,
        source_url=entity.source_url,
        created_at=entity.created_at,
    )


class RpaExtractionRepository(RpaExtractionRepositoryPort):
    """Persists RpaExtraction entities using SQLAlchemy against PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, extraction: RpaExtraction) -> RpaExtraction:
        model = _to_model(extraction)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        log.info("database.rpa_extraction_saved", extraction_id=str(model.id))
        return _to_entity(model)

    async def list_paginated(
        self, page: int, limit: int
    ) -> tuple[list[RpaExtraction], int]:
        total_result = await self._session.execute(
            select(func.count()).select_from(RpaExtractionModel)
        )
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        paged_stmt = (
            select(RpaExtractionModel)
            .order_by(RpaExtractionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(paged_stmt)
        models = result.scalars().all()

        return [_to_entity(model) for model in models], total
