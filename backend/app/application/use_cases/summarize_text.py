"""Use case: summarize text via the AI service and log the interaction."""

import structlog

from app.application.dtos.assistant_dto import (
    SummarizeTextDTO,
    SummarizeTextResponseDTO,
)
from app.domain.entities.assistant_log import (
    ASSISTANT_LOG_STATUS_COMPLETED,
    ASSISTANT_LOG_STATUS_FAILED,
    AssistantLog,
)
from app.domain.exceptions import (
    AIQuotaExceededError,
    AIServiceError,
    AIServiceUnavailableError,
)
from app.domain.interfaces.ai_service import AIServicePort, AISummaryResult
from app.domain.interfaces.assistant_log_repository import AssistantLogRepositoryPort

log = structlog.get_logger(__name__)


class SummarizeTextUseCase:
    """Summarizes text and logs the interaction, even when the AI call fails."""

    def __init__(
        self,
        ai_service: AIServicePort,
        fallback_ai_service: AIServicePort,
        log_repo: AssistantLogRepositoryPort,
        model_name: str,
    ) -> None:
        self._ai_service = ai_service
        self._fallback_ai_service = fallback_ai_service
        self._log_repo = log_repo
        self._model_name = model_name

    async def _resolve_summary(self, dto: SummarizeTextDTO) -> AISummaryResult:
        """Summarize via the real service, falling back to mock on quota errors."""
        try:
            return await self._ai_service.summarize(dto.text)
        except (AIQuotaExceededError, AIServiceUnavailableError) as exc:
            if not dto.allow_fallback:
                raise
            log.warning(
                "assistant.provider_failed_falling_back_to_mock",
                user_id=dto.user_id,
                reason=str(exc),
            )
            return await self._fallback_ai_service.summarize(dto.text)

    async def execute(self, dto: SummarizeTextDTO) -> SummarizeTextResponseDTO:
        """Summarize dto.text and store the resulting AssistantLog."""
        log.info("summarize_text.started", user_id=dto.user_id, chars=len(dto.text))

        try:
            result = await self._resolve_summary(dto)
        except AIServiceError as exc:
            failed_entry = AssistantLog(
                user_id=dto.user_id,
                prompt=dto.text,
                model=self._model_name,
                status=ASSISTANT_LOG_STATUS_FAILED,
            )
            saved = await self._log_repo.save(failed_entry)
            log.warning(
                "assistant.summarize_failed_but_logged",
                log_id=str(saved.id),
                user_id=dto.user_id,
            )
            # Let the router broadcast this over the WebSocket too, same as a
            # successful summary — it doesn't have the saved log otherwise.
            exc.assistant_log_id = saved.id
            exc.assistant_model = saved.model
            raise

        log_entry = AssistantLog(
            user_id=dto.user_id,
            prompt=dto.text,
            response=result.text,
            model=result.model,
            status=ASSISTANT_LOG_STATUS_COMPLETED,
        )
        saved = await self._log_repo.save(log_entry)

        log.info(
            "assistant.summarized",
            log_id=str(saved.id),
            user_id=dto.user_id,
            model=result.model,
        )
        return SummarizeTextResponseDTO.from_domain(saved)
