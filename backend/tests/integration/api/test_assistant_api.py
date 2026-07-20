"""Integration tests for the /assistant endpoints."""

from httpx import AsyncClient

from app.core.dependencies import get_ai_service
from app.domain.exceptions import AIQuotaExceededError, AIServiceError
from app.domain.interfaces.ai_service import AIServicePort, AISummaryResult
from app.main import app

ASSISTANT_URL = "/api/v1/assistant/summarize"
ASSISTANT_LOGS_URL = "/api/v1/assistant/logs"
AI_MODE_URL = "/api/v1/assistant/ai-mode"


class _FailingAIService(AIServicePort):
    """Test double that always fails, to exercise the failed-log path."""

    async def summarize(self, text: str) -> AISummaryResult:
        raise AIServiceError("boom")


class _QuotaExceededAIService(AIServicePort):
    """Test double simulating a real provider whose daily quota ran out."""

    async def summarize(self, text: str) -> AISummaryResult:
        raise AIQuotaExceededError("cuota diaria agotada", retry_after_seconds=42.0)


async def test_summarize_text_with_valid_payload_returns_201(
    client: AsyncClient,
) -> None:
    payload = {
        "user_id": "user-1",
        "text": "Este es un texto de prueba. Con dos frases.",
    }

    response = await client.post(ASSISTANT_URL, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["summary"].startswith("[mock-summary]")
    assert body["model"] == "mock"


async def test_summarize_text_with_empty_text_returns_422(
    client: AsyncClient,
) -> None:
    payload = {"user_id": "user-1", "text": ""}

    response = await client.post(ASSISTANT_URL, json=payload)

    assert response.status_code == 422


async def test_list_assistant_logs_returns_previously_created_entry(
    client: AsyncClient,
) -> None:
    await client.post(
        ASSISTANT_URL,
        json={"user_id": "user-1", "text": "Texto para el historial de logs."},
    )

    response = await client.get(f"{ASSISTANT_LOGS_URL}?page=1&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 10
    assert body["total"] >= 1
    assert any(
        item["prompt"] == "Texto para el historial de logs." for item in body["items"]
    )


async def test_summarize_failure_still_logs_prompt(
    client: AsyncClient,
) -> None:
    app.dependency_overrides[get_ai_service] = lambda: _FailingAIService()
    try:
        response = await client.post(
            ASSISTANT_URL,
            json={
                "user_id": "user-1",
                "text": "Texto que la IA falló al resumir.",
            },
        )
    finally:
        del app.dependency_overrides[get_ai_service]

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "AI_SERVICE_ERROR"

    logs_response = await client.get(f"{ASSISTANT_LOGS_URL}?page=1&limit=10")
    items = logs_response.json()["items"]
    failed_entry = next(
        item for item in items if item["prompt"] == "Texto que la IA falló al resumir."
    )
    assert failed_entry["status"] == "failed"
    assert failed_entry["summary"] is None


async def test_summarize_quota_exceeded_falls_back_to_mock_by_default(
    client: AsyncClient,
) -> None:
    app.dependency_overrides[get_ai_service] = lambda: _QuotaExceededAIService()
    try:
        response = await client.post(
            ASSISTANT_URL,
            json={
                "user_id": "user-1",
                "text": "Texto cuando la cuota de IA ya se agotó.",
            },
        )
    finally:
        del app.dependency_overrides[get_ai_service]

    assert response.status_code == 201
    body = response.json()
    assert body["model"] == "mock"
    assert body["summary"].startswith("[mock-summary]")


async def test_summarize_quota_exceeded_without_fallback_returns_429(
    client: AsyncClient,
) -> None:
    """The RPA sends allow_fallback=false so it ends up without a summary
    instead of a simulated one — this is what its request looks like."""
    app.dependency_overrides[get_ai_service] = lambda: _QuotaExceededAIService()
    try:
        response = await client.post(
            ASSISTANT_URL,
            json={
                "user_id": "rpa-wikipedia-scraper",
                "text": "Párrafo scrapeado de Wikipedia.",
                "allow_fallback": False,
            },
        )
    finally:
        del app.dependency_overrides[get_ai_service]

    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "AI_QUOTA_EXCEEDED"


async def test_ai_mode_defaults_to_not_forced(client: AsyncClient) -> None:
    response = await client.get(AI_MODE_URL)

    assert response.status_code == 200
    assert response.json() == {"force_mock": False}


async def test_ai_mode_can_be_toggled_and_persists(client: AsyncClient) -> None:
    put_response = await client.put(AI_MODE_URL, json={"force_mock": True})
    assert put_response.status_code == 200
    assert put_response.json() == {"force_mock": True}

    get_response = await client.get(AI_MODE_URL)
    assert get_response.json() == {"force_mock": True}


async def test_toggling_ai_mode_on_makes_summarize_use_mock(
    client: AsyncClient,
) -> None:
    """End-to-end: flipping the shared toggle changes what /assistant/summarize
    does with no per-request field needed — this is what the frontend switch
    and the RPA both rely on to stay in sync without any RPA-side change."""
    await client.put(AI_MODE_URL, json={"force_mock": True})

    response = await client.post(
        ASSISTANT_URL,
        json={"user_id": "user-1", "text": "Texto con IA forzada a simulada."},
    )

    assert response.status_code == 201
    assert response.json()["model"] == "mock"
