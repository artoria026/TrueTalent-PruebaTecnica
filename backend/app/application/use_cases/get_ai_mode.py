"""Use case: read the current global AI mode."""

from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort


class GetAiModeUseCase:
    """Reports whether AI calls are currently forced to the simulated mock."""

    def __init__(self, repo: AIModeRepositoryPort) -> None:
        self._repo = repo

    async def execute(self) -> bool:
        """Return True when AI calls are forced to the simulated mock."""
        return await self._repo.get_force_mock()
