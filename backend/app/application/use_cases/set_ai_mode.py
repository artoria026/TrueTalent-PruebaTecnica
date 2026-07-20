"""Use case: toggle the global AI mode."""

import structlog

from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort

log = structlog.get_logger(__name__)


class SetAiModeUseCase:
    """Sets the global AI mode, shared by every caller including the RPA."""

    def __init__(self, repo: AIModeRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, force_mock: bool) -> bool:
        """Persist the new mode and return it."""
        await self._repo.set_force_mock(force_mock)
        log.info("ai_mode.updated", force_mock=force_mock)
        return force_mock
