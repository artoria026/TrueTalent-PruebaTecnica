"""Integration tests for the /rpa/extractions endpoints (no AI involved)."""

from httpx import AsyncClient

RPA_EXTRACTIONS_URL = "/api/v1/rpa/extractions"


async def test_create_extraction_with_valid_payload_returns_201(
    client: AsyncClient,
) -> None:
    payload = {
        "term": "Python (programming language)",
        "paragraph": "Python es un lenguaje de programación interpretado.",
        "source_url": "https://es.wikipedia.org/wiki/Python",
    }

    response = await client.post(RPA_EXTRACTIONS_URL, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["term"] == payload["term"]
    assert body["paragraph"] == payload["paragraph"]
    assert body["source_url"] == payload["source_url"]


async def test_create_extraction_with_empty_paragraph_returns_422(
    client: AsyncClient,
) -> None:
    payload = {
        "term": "Python",
        "paragraph": "",
        "source_url": "https://es.wikipedia.org/wiki/Python",
    }

    response = await client.post(RPA_EXTRACTIONS_URL, json=payload)

    assert response.status_code == 422


async def test_list_extractions_returns_previously_created_entry(
    client: AsyncClient,
) -> None:
    await client.post(
        RPA_EXTRACTIONS_URL,
        json={
            "term": "Alan Turing",
            "paragraph": "Alan Turing fue un matemático británico.",
            "source_url": "https://es.wikipedia.org/wiki/Alan_Turing",
        },
    )

    response = await client.get(f"{RPA_EXTRACTIONS_URL}?page=1&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["term"] == "Alan Turing" for item in body["items"])
