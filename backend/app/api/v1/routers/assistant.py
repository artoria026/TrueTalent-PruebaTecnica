"""HTTP routes for the AI assistant."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.v1.schemas.assistant_schema import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_LIMIT,
    MAX_PAGE_LIMIT,
    AiModeResponse,
    AssistantLogListResponse,
    AssistantLogResponse,
    SetAiModeRequest,
    SummarizeTextRequest,
    SummarizeTextResponse,
)
from app.application.dtos.assistant_dto import SummarizeTextDTO
from app.core.dependencies import (
    AssistantLogRepoDep,
    GetAiModeUseCaseDep,
    SetAiModeUseCaseDep,
    SummarizeTextUseCaseDep,
)
from app.domain.exceptions import AIServiceError
from app.infrastructure.websocket.connection_manager import manager

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post(
    "/summarize",
    response_model=SummarizeTextResponse,
    status_code=status.HTTP_201_CREATED,
)
async def summarize_text(
    payload: SummarizeTextRequest,
    use_case: SummarizeTextUseCaseDep,
) -> SummarizeTextResponse:
    """Summarize the given text using the configured AI service."""
    dto = SummarizeTextDTO(**payload.model_dump())

    # Broadcast directly: this handler runs in the API process, which owns
    # the WebSocket connections (unlike the worker, see redis_listener.py).
    try:
        result = await use_case.execute(dto)
    except AIServiceError as exc:
        log_id = getattr(exc, "assistant_log_id", None)
        if log_id is not None:
            await manager.broadcast(
                {
                    "event": "assistant.created",
                    "id": str(log_id),
                    "model": getattr(exc, "assistant_model", "unknown"),
                    "status": "failed",
                }
            )
        raise

    await manager.broadcast(
        {
            "event": "assistant.created",
            "id": str(result.id),
            "model": result.model,
            "status": "completed",
        }
    )

    return SummarizeTextResponse(**result.model_dump())


@router.get("/ai-mode", response_model=AiModeResponse)
async def get_ai_mode(use_case: GetAiModeUseCaseDep) -> AiModeResponse:
    """Report whether AI calls are currently forced to the simulated mock."""
    return AiModeResponse(force_mock=await use_case.execute())


@router.put("/ai-mode", response_model=AiModeResponse)
async def set_ai_mode(
    payload: SetAiModeRequest, use_case: SetAiModeUseCaseDep
) -> AiModeResponse:
    """Toggle the global AI mode for every caller of /assistant/summarize."""
    force_mock = await use_case.execute(payload.force_mock)
    return AiModeResponse(force_mock=force_mock)


@router.get("/logs", response_model=AssistantLogListResponse)
async def list_assistant_logs(
    repo: AssistantLogRepoDep,
    page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
) -> AssistantLogListResponse:
    """List past assistant interactions with pagination, newest first."""
    logs, total = await repo.list_paginated(page, limit)
    return AssistantLogListResponse(
        items=[
            AssistantLogResponse(
                id=entry.id,
                user_id=entry.user_id,
                prompt=entry.prompt,
                summary=entry.response,
                model=entry.model,
                status=entry.status,
                created_at=entry.created_at,
            )
            for entry in logs
        ],
        total=total,
        page=page,
        limit=limit,
    )
