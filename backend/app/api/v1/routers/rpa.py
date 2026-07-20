"""HTTP routes for RPA extractions — no AI involved here."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.rpa_extraction_schema import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_LIMIT,
    MAX_PAGE_LIMIT,
    CreateRpaExtractionRequest,
    RpaExtractionListResponse,
    RpaExtractionResponse,
)
from app.application.dtos.rpa_extraction_dto import CreateRpaExtractionDTO
from app.core.dependencies import CreateRpaExtractionUseCaseDep, RpaExtractionRepoDep
from app.infrastructure.websocket.connection_manager import manager

router = APIRouter(prefix="/rpa", tags=["rpa"])


@router.post(
    "/extractions",
    response_model=RpaExtractionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_extraction(
    payload: CreateRpaExtractionRequest,
    use_case: CreateRpaExtractionUseCaseDep,
) -> RpaExtractionResponse:
    """Record a paragraph the RPA scraped, with its source URL."""
    dto = CreateRpaExtractionDTO(**payload.model_dump())
    result = await use_case.execute(dto)

    await manager.broadcast(
        {"event": "rpa.extracted", "id": str(result.id), "term": result.term}
    )

    return RpaExtractionResponse(**result.model_dump())


@router.get("/extractions", response_model=RpaExtractionListResponse)
async def list_extractions(
    repo: RpaExtractionRepoDep,
    page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
) -> RpaExtractionListResponse:
    """List past RPA extractions with pagination, newest first."""
    extractions, total = await repo.list_paginated(page, limit)
    return RpaExtractionListResponse(
        items=[
            RpaExtractionResponse(
                id=entry.id,
                term=entry.term,
                paragraph=entry.paragraph,
                source_url=entry.source_url,
                created_at=entry.created_at,
            )
            for entry in extractions
        ],
        total=total,
        page=page,
        limit=limit,
    )
