"""Mock implementation of AIServicePort, used when AI_PROVIDER=mock."""

import structlog

from app.domain.interfaces.ai_service import AIServicePort, AISummaryResult

MOCK_SUMMARY_SENTENCE_COUNT = 2
MOCK_SUMMARY_MAX_CHARS = 240
MOCK_MODEL_NAME = "mock"

log = structlog.get_logger(__name__)


class MockAIService(AIServicePort):
    """Deterministic, offline stand-in for a real AI provider."""

    async def summarize(self, text: str) -> AISummaryResult:
        flattened = text.replace("\n", " ")
        sentences = [s.strip() for s in flattened.split(".") if s.strip()]
        excerpt = ". ".join(sentences[:MOCK_SUMMARY_SENTENCE_COUNT])
        summary = excerpt[:MOCK_SUMMARY_MAX_CHARS].strip()
        if not summary:
            summary = text[:MOCK_SUMMARY_MAX_CHARS].strip()

        log.debug("mock_ai.summarize", input_chars=len(text), output_chars=len(summary))
        return AISummaryResult(text=f"[mock-summary] {summary}", model=MOCK_MODEL_NAME)
