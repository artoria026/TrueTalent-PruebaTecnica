"""Unit tests for SummarizeTextUseCase."""

from unittest.mock import AsyncMock

import pytest

from app.application.dtos.assistant_dto import SummarizeTextDTO
from app.application.use_cases.summarize_text import SummarizeTextUseCase
from app.domain.entities.assistant_log import AssistantLog
from app.domain.exceptions import (
    AIQuotaExceededError,
    AIServiceError,
    AIServiceUnavailableError,
)
from app.domain.interfaces.ai_service import AIServicePort, AISummaryResult
from app.domain.interfaces.assistant_log_repository import AssistantLogRepositoryPort
from app.infrastructure.ai.mock_service import MockAIService

MODEL_NAME = "mock"


@pytest.fixture
def log_repo() -> AsyncMock:
    return AsyncMock(spec=AssistantLogRepositoryPort)


@pytest.fixture
def ai_service() -> AsyncMock:
    return AsyncMock(spec=AIServicePort)


@pytest.fixture
def fallback_ai_service() -> AsyncMock:
    return AsyncMock(spec=AIServicePort)


async def test_execute_with_valid_text_returns_summary_and_persists_log(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    dto = SummarizeTextDTO(user_id="user-1", text="Un texto largo para resumir.")
    ai_service.summarize.return_value = AISummaryResult(
        text="resumen corto", model=MODEL_NAME
    )
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, MODEL_NAME
    )
    result = await use_case.execute(dto)

    assert result.summary == "resumen corto"
    assert result.model == MODEL_NAME
    ai_service.summarize.assert_awaited_once_with(dto.text)
    fallback_ai_service.summarize.assert_not_awaited()
    log_repo.save.assert_awaited_once()


async def test_execute_with_mock_ai_service_returns_deterministic_summary(
    fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    dto = SummarizeTextDTO(user_id="user-1", text="Primera frase. Segunda frase.")
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        MockAIService(), fallback_ai_service, log_repo, MODEL_NAME
    )
    result = await use_case.execute(dto)

    assert result.summary.startswith("[mock-summary]")


async def test_execute_persists_assistant_log_with_prompt_and_response(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    dto = SummarizeTextDTO(user_id="user-42", text="Texto de prueba")
    ai_service.summarize.return_value = AISummaryResult(
        text="resumen", model=MODEL_NAME
    )

    captured: list[AssistantLog] = []

    async def _save(entry: AssistantLog) -> AssistantLog:
        captured.append(entry)
        return entry

    log_repo.save.side_effect = _save

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, MODEL_NAME
    )
    await use_case.execute(dto)

    assert captured[0].user_id == "user-42"
    assert captured[0].prompt == "Texto de prueba"
    assert captured[0].response == "resumen"


async def test_quota_exceeded_falls_back_to_mock_when_allowed(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    """Default behavior (allow_fallback=True): the manual/Postman path."""
    dto = SummarizeTextDTO(user_id="user-1", text="Texto", allow_fallback=True)
    ai_service.summarize.side_effect = AIQuotaExceededError("cuota agotada")
    fallback_ai_service.summarize.return_value = AISummaryResult(
        text="[mock-summary] Texto", model="mock"
    )
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, "gemini-flash-latest"
    )
    result = await use_case.execute(dto)

    assert result.model == "mock"
    assert result.summary == "[mock-summary] Texto"
    fallback_ai_service.summarize.assert_awaited_once_with(dto.text)


async def test_quota_exceeded_does_not_fall_back_when_disallowed(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    """The RPA sets allow_fallback=False: it should end up without a summary,
    not a simulated one — the extraction is already safe on its own."""
    dto = SummarizeTextDTO(
        user_id="rpa-wikipedia-scraper", text="Texto", allow_fallback=False
    )
    ai_service.summarize.side_effect = AIQuotaExceededError("cuota agotada")
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, "gemini-flash-latest"
    )

    with pytest.raises(AIQuotaExceededError):
        await use_case.execute(dto)

    fallback_ai_service.summarize.assert_not_awaited()
    saved_entry = log_repo.save.await_args.args[0]
    assert saved_entry.status == "failed"
    assert saved_entry.model == "gemini-flash-latest"


async def test_provider_unavailable_falls_back_to_mock_when_allowed(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    """A 503 (provider overloaded) should trigger the same fallback as a 429."""
    dto = SummarizeTextDTO(user_id="user-1", text="Texto", allow_fallback=True)
    ai_service.summarize.side_effect = AIServiceUnavailableError("modelo saturado")
    fallback_ai_service.summarize.return_value = AISummaryResult(
        text="[mock-summary] Texto", model="mock"
    )
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, "gemini-flash-latest"
    )
    result = await use_case.execute(dto)

    assert result.model == "mock"
    fallback_ai_service.summarize.assert_awaited_once_with(dto.text)


async def test_provider_unavailable_does_not_fall_back_when_disallowed(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    dto = SummarizeTextDTO(
        user_id="rpa-wikipedia-scraper", text="Texto", allow_fallback=False
    )
    ai_service.summarize.side_effect = AIServiceUnavailableError("modelo saturado")
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, "gemini-flash-latest"
    )

    with pytest.raises(AIServiceUnavailableError):
        await use_case.execute(dto)

    fallback_ai_service.summarize.assert_not_awaited()


async def test_non_quota_error_does_not_fall_back(
    ai_service: AsyncMock, fallback_ai_service: AsyncMock, log_repo: AsyncMock
) -> None:
    """A non-quota AIServiceError (e.g. a malformed provider response) must
    propagate as a real failure, never silently masked by the mock."""
    dto = SummarizeTextDTO(user_id="user-1", text="Texto", allow_fallback=True)
    ai_service.summarize.side_effect = AIServiceError("respuesta vacía del proveedor")
    log_repo.save.side_effect = lambda entry: entry

    use_case = SummarizeTextUseCase(
        ai_service, fallback_ai_service, log_repo, MODEL_NAME
    )

    with pytest.raises(AIServiceError):
        await use_case.execute(dto)

    fallback_ai_service.summarize.assert_not_awaited()
