"""OpenAI-backed implementation of AIServicePort."""

from typing import Any

import openai
import structlog
from openai import AsyncOpenAI

from app.domain.exceptions import AIQuotaExceededError, AIServiceError
from app.domain.interfaces.ai_service import AIServicePort, AISummaryResult

SUMMARIZATION_SYSTEM_PROMPT = (
    "Eres un asistente que resume textos de forma clara y concisa en español, "
    "en un maximo de 3 frases."
)
# Generous headroom: "thinking" models spend part of it on internal reasoning.
MAX_SUMMARY_TOKENS = 1024

log = structlog.get_logger(__name__)


def _error_body(exc: openai.APIStatusError) -> dict[str, Any] | None:
    """Return the provider's parsed JSON error body, if any."""
    body = exc.body
    if isinstance(body, list) and body and isinstance(body[0], dict):
        body = body[0]
    return body if isinstance(body, dict) else None


def _provider_message(exc: openai.APIStatusError) -> str | None:
    """Extract the human-readable message from a provider error body."""
    body = _error_body(exc)
    error = body.get("error") if body else None
    message = error.get("message") if isinstance(error, dict) else None
    return message if isinstance(message, str) else None


def _retry_after_seconds(exc: openai.APIStatusError) -> float | None:
    """Extract how long to wait before retrying, if the provider says so."""
    header_value = exc.response.headers.get("retry-after")
    if header_value is not None:
        try:
            return float(header_value)
        except ValueError:
            pass

    body = _error_body(exc)
    error = body.get("error") if body else None
    details = error.get("details") if isinstance(error, dict) else None
    if isinstance(details, list):
        for detail in details:
            raw_delay = detail.get("retryDelay") if isinstance(detail, dict) else None
            if isinstance(raw_delay, str) and raw_delay.endswith("s"):
                try:
                    return float(raw_delay[:-1])
                except ValueError:
                    continue
    return None


class OpenAIService(AIServicePort):
    """Implements AIServicePort using the real OpenAI Chat Completions API."""

    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    async def summarize(self, text: str) -> AISummaryResult:
        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=MAX_SUMMARY_TOKENS,
                messages=[
                    {"role": "system", "content": SUMMARIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            )
        except openai.RateLimitError as exc:
            retry_after = _retry_after_seconds(exc)
            message = _provider_message(exc) or "AI provider rate limit exceeded"
            log.error(
                "openai.rate_limited",
                model=self._model,
                error=message,
                retry_after_seconds=retry_after,
            )
            raise AIQuotaExceededError(
                message, retry_after_seconds=retry_after
            ) from exc
        except Exception as exc:
            log.error("openai.summarize_failed", error=str(exc))
            raise AIServiceError("Failed to summarize text via OpenAI") from exc

        content = completion.choices[0].message.content
        if not content:
            log.error("openai.empty_response", model=self._model)
            raise AIServiceError("OpenAI returned an empty summary")

        log.info("openai.summarized", model=self._model, output_chars=len(content))
        return AISummaryResult(text=content.strip(), model=self._model)
