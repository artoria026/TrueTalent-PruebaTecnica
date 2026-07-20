"""Integration tests for the /transactions endpoints."""

from httpx import AsyncClient

TRANSACTIONS_URL = "/api/v1/transactions"
TRANSACTIONS_CREATE_URL = f"{TRANSACTIONS_URL}/create"


async def _payload(idempotency_key: str) -> dict[str, object]:
    return {
        "user_id": "user-1",
        "monto": 150.5,
        "tipo": "deposito",
        "idempotency_key": idempotency_key,
    }


async def test_create_transaction_with_valid_payload_returns_201(
    client: AsyncClient,
) -> None:
    response = await client.post(
        TRANSACTIONS_CREATE_URL, json=await _payload("it-key-1")
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["idempotency_key"] == "it-key-1"


async def test_create_transaction_with_duplicate_key_returns_200(
    client: AsyncClient,
) -> None:
    payload = await _payload("it-key-2")
    first = await client.post(TRANSACTIONS_CREATE_URL, json=payload)
    second = await client.post(TRANSACTIONS_CREATE_URL, json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


async def test_create_transaction_with_invalid_monto_returns_422(
    client: AsyncClient,
) -> None:
    payload = await _payload("it-key-3")
    payload["monto"] = -10

    response = await client.post(TRANSACTIONS_CREATE_URL, json=payload)

    assert response.status_code == 422


async def test_process_async_enqueues_job_and_returns_202(
    client: AsyncClient,
) -> None:
    payload = await _payload("it-key-async-1")

    response = await client.post(f"{TRANSACTIONS_URL}/async-process", json=payload)

    assert response.status_code == 202
    assert response.json()["status"] == "pending"


async def test_get_transaction_with_unknown_id_returns_404(
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"{TRANSACTIONS_URL}/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "TRANSACTION_NOT_FOUND"


async def test_list_transactions_returns_paginated_response(
    client: AsyncClient,
) -> None:
    await client.post(TRANSACTIONS_CREATE_URL, json=await _payload("it-key-list-1"))

    response = await client.get(f"{TRANSACTIONS_URL}?page=1&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 10
    assert isinstance(body["items"], list)
