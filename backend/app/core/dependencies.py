"""Centralized FastAPI dependency providers; wires ports to implementations."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_rpa_extraction import (
    CreateRpaExtractionUseCase,
)
from app.application.use_cases.create_transaction import CreateTransactionUseCase
from app.application.use_cases.get_ai_mode import GetAiModeUseCase
from app.application.use_cases.process_transaction_async import (
    ProcessTransactionAsyncUseCase,
)
from app.application.use_cases.set_ai_mode import SetAiModeUseCase
from app.application.use_cases.summarize_text import SummarizeTextUseCase
from app.core.config import Settings, get_settings
from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort
from app.domain.interfaces.ai_service import AIServicePort
from app.domain.interfaces.assistant_log_repository import AssistantLogRepositoryPort
from app.domain.interfaces.queue_service import QueueServicePort
from app.domain.interfaces.rpa_extraction_repository import (
    RpaExtractionRepositoryPort,
)
from app.domain.interfaces.transaction_repository import TransactionRepositoryPort
from app.infrastructure.ai.mock_service import MockAIService
from app.infrastructure.ai.openai_service import OpenAIService
from app.infrastructure.ai.redis_ai_mode_repository import RedisAIModeRepository
from app.infrastructure.db.repositories.assistant_log_repository import (
    AssistantLogRepository,
)
from app.infrastructure.db.repositories.rpa_extraction_repository import (
    RpaExtractionRepository,
)
from app.infrastructure.db.repositories.transaction_repository import (
    TransactionRepository,
)
from app.infrastructure.db.session import get_session
from app.infrastructure.queue.redis_client import get_redis_client
from app.infrastructure.queue.redis_queue import RedisQueueService

# Gemini reuses OpenAIService via its OpenAI-compatible endpoint.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a request-scoped AsyncSession."""
    async for session in get_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_transaction_repository(session: DbSession) -> TransactionRepositoryPort:
    """Provide the concrete TransactionRepository behind its port."""
    return TransactionRepository(session)


def get_assistant_log_repository(session: DbSession) -> AssistantLogRepositoryPort:
    """Provide the concrete AssistantLogRepository behind its port."""
    return AssistantLogRepository(session)


def get_rpa_extraction_repository(session: DbSession) -> RpaExtractionRepositoryPort:
    """Provide the concrete RpaExtractionRepository behind its port."""
    return RpaExtractionRepository(session)


def get_queue_service() -> QueueServicePort:
    """Provide the concrete RedisQueueService behind its port."""
    return RedisQueueService(get_redis_client())


def get_ai_mode_repository() -> AIModeRepositoryPort:
    """Provide the concrete RedisAIModeRepository behind its port."""
    return RedisAIModeRepository(get_redis_client())


AIModeRepoDep = Annotated[AIModeRepositoryPort, Depends(get_ai_mode_repository)]


def _resolve_ai_provider(settings: Settings) -> tuple[str, str]:
    """Return the (provider, model) in effect, falling back to mock without a key."""
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return "openai", settings.openai_model
    if settings.ai_provider == "gemini" and settings.gemini_api_key:
        return "gemini", settings.gemini_model
    return "mock", "mock"


async def get_ai_service(
    settings: SettingsDep, ai_mode_repo: AIModeRepoDep
) -> AIServicePort:
    """Provide the AI service, respecting the global mock toggle over AI_PROVIDER."""
    if await ai_mode_repo.get_force_mock():
        return MockAIService()
    provider, model = _resolve_ai_provider(settings)
    if provider == "openai":
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        return OpenAIService(client=client, model=model)
    if provider == "gemini":
        client = AsyncOpenAI(api_key=settings.gemini_api_key, base_url=GEMINI_BASE_URL)
        return OpenAIService(client=client, model=model)
    return MockAIService()


def get_fallback_ai_service() -> AIServicePort:
    """Provide the fallback used when the primary provider's quota runs out."""
    return MockAIService()


TransactionRepoDep = Annotated[
    TransactionRepositoryPort, Depends(get_transaction_repository)
]
AssistantLogRepoDep = Annotated[
    AssistantLogRepositoryPort, Depends(get_assistant_log_repository)
]
RpaExtractionRepoDep = Annotated[
    RpaExtractionRepositoryPort, Depends(get_rpa_extraction_repository)
]
QueueServiceDep = Annotated[QueueServicePort, Depends(get_queue_service)]
AIServiceDep = Annotated[AIServicePort, Depends(get_ai_service)]
FallbackAIServiceDep = Annotated[AIServicePort, Depends(get_fallback_ai_service)]


def get_create_transaction_use_case(
    repo: TransactionRepoDep,
) -> CreateTransactionUseCase:
    """Provide CreateTransactionUseCase wired with its repository dependency."""
    return CreateTransactionUseCase(repo)


def get_process_transaction_async_use_case(
    repo: TransactionRepoDep,
    queue: QueueServiceDep,
    settings: SettingsDep,
) -> ProcessTransactionAsyncUseCase:
    """Provide ProcessTransactionAsyncUseCase wired with its dependencies."""
    return ProcessTransactionAsyncUseCase(
        repo=repo, queue=queue, queue_name=settings.transactions_queue_name
    )


def get_summarize_text_use_case(
    ai_service: AIServiceDep,
    fallback_ai_service: FallbackAIServiceDep,
    log_repo: AssistantLogRepoDep,
    settings: SettingsDep,
) -> SummarizeTextUseCase:
    """Provide SummarizeTextUseCase wired with its dependencies."""
    _, model_name = _resolve_ai_provider(settings)
    return SummarizeTextUseCase(
        ai_service=ai_service,
        fallback_ai_service=fallback_ai_service,
        log_repo=log_repo,
        model_name=model_name,
    )


def get_create_rpa_extraction_use_case(
    repo: RpaExtractionRepoDep,
) -> CreateRpaExtractionUseCase:
    """Provide CreateRpaExtractionUseCase wired with its repository dependency."""
    return CreateRpaExtractionUseCase(repo)


def get_get_ai_mode_use_case(repo: AIModeRepoDep) -> GetAiModeUseCase:
    """Provide GetAiModeUseCase wired with its repository dependency."""
    return GetAiModeUseCase(repo)


def get_set_ai_mode_use_case(repo: AIModeRepoDep) -> SetAiModeUseCase:
    """Provide SetAiModeUseCase wired with its repository dependency."""
    return SetAiModeUseCase(repo)


CreateTransactionUseCaseDep = Annotated[
    CreateTransactionUseCase, Depends(get_create_transaction_use_case)
]
ProcessTransactionAsyncUseCaseDep = Annotated[
    ProcessTransactionAsyncUseCase, Depends(get_process_transaction_async_use_case)
]
SummarizeTextUseCaseDep = Annotated[
    SummarizeTextUseCase, Depends(get_summarize_text_use_case)
]
CreateRpaExtractionUseCaseDep = Annotated[
    CreateRpaExtractionUseCase, Depends(get_create_rpa_extraction_use_case)
]
GetAiModeUseCaseDep = Annotated[GetAiModeUseCase, Depends(get_get_ai_mode_use_case)]
SetAiModeUseCaseDep = Annotated[SetAiModeUseCase, Depends(get_set_ai_mode_use_case)]
