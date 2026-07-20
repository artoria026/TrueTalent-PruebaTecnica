"""Unit tests for GetAiModeUseCase and SetAiModeUseCase."""

from app.application.use_cases.get_ai_mode import GetAiModeUseCase
from app.application.use_cases.set_ai_mode import SetAiModeUseCase
from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort


class _InMemoryAIModeRepository(AIModeRepositoryPort):
    def __init__(self, initial: bool = False) -> None:
        self._force_mock = initial

    async def get_force_mock(self) -> bool:
        return self._force_mock

    async def set_force_mock(self, value: bool) -> None:
        self._force_mock = value


async def test_get_ai_mode_reports_current_value() -> None:
    repo = _InMemoryAIModeRepository(initial=True)
    use_case = GetAiModeUseCase(repo)

    assert await use_case.execute() is True


async def test_set_ai_mode_persists_and_returns_new_value() -> None:
    repo = _InMemoryAIModeRepository(initial=False)
    use_case = SetAiModeUseCase(repo)

    result = await use_case.execute(True)

    assert result is True
    assert await repo.get_force_mock() is True
