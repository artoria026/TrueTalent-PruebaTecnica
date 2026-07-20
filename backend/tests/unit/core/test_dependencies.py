"""Unit tests for the AI service wiring in core/dependencies.py.

Focused on the one behavior that's easy to get backwards: the global AI mode
toggle must win over AI_PROVIDER, not the other way around.
"""

from app.core.config import Settings
from app.core.dependencies import get_ai_service
from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort
from app.infrastructure.ai.mock_service import MockAIService
from app.infrastructure.ai.openai_service import OpenAIService


class _StaticAIModeRepository(AIModeRepositoryPort):
    def __init__(self, force_mock: bool) -> None:
        self._force_mock = force_mock

    async def get_force_mock(self) -> bool:
        return self._force_mock

    async def set_force_mock(self, value: bool) -> None:
        self._force_mock = value


async def test_get_ai_service_uses_configured_provider_when_not_forced() -> None:
    settings = Settings(ai_provider="openai", openai_api_key="sk-test")
    ai_mode_repo = _StaticAIModeRepository(force_mock=False)

    service = await get_ai_service(settings, ai_mode_repo)

    assert isinstance(service, OpenAIService)


async def test_get_ai_service_forces_mock_even_with_a_real_provider_configured() -> (
    None
):
    """This is the actual feature: toggling AI mode off in the frontend must
    short-circuit AI_PROVIDER entirely, so no real tokens are spent."""
    settings = Settings(ai_provider="openai", openai_api_key="sk-test")
    ai_mode_repo = _StaticAIModeRepository(force_mock=True)

    service = await get_ai_service(settings, ai_mode_repo)

    assert isinstance(service, MockAIService)


async def test_get_ai_service_defaults_to_mock_without_any_key_configured() -> None:
    settings = Settings()
    ai_mode_repo = _StaticAIModeRepository(force_mock=False)

    service = await get_ai_service(settings, ai_mode_repo)

    assert isinstance(service, MockAIService)
