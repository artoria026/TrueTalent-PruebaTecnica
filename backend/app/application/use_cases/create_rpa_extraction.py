"""Use case: persist a paragraph the RPA scraped from a public site."""

import structlog

from app.application.dtos.rpa_extraction_dto import (
    CreateRpaExtractionDTO,
    RpaExtractionResponseDTO,
)
from app.domain.entities.rpa_extraction import RpaExtraction
from app.domain.interfaces.rpa_extraction_repository import (
    RpaExtractionRepositoryPort,
)

log = structlog.get_logger(__name__)


class CreateRpaExtractionUseCase:
    """Saves an RpaExtraction. No AI involved — see PARTE 4 vs PARTE 3."""

    def __init__(self, repo: RpaExtractionRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, dto: CreateRpaExtractionDTO) -> RpaExtractionResponseDTO:
        """Persist the scraped paragraph and its source."""
        extraction = RpaExtraction(
            term=dto.term, paragraph=dto.paragraph, source_url=dto.source_url
        )
        saved = await self._repo.save(extraction)

        log.info("rpa_extraction.created", extraction_id=str(saved.id), term=dto.term)
        return RpaExtractionResponseDTO.from_domain(saved)
