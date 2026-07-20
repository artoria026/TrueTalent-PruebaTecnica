"""HTTP routes for transactions."""

from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.api.v1.schemas.transaction_schema import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_LIMIT,
    MAX_PAGE_LIMIT,
    CreateTransactionRequest,
    TransactionListResponse,
    TransactionResponse,
)
from app.application.dtos.transaction_dto import (
    CreateTransactionDTO,
    ProcessTransactionAsyncDTO,
)
from app.core.dependencies import (
    CreateTransactionUseCaseDep,
    ProcessTransactionAsyncUseCaseDep,
    TransactionRepoDep,
)
from app.core.security import limiter
from app.domain.exceptions import TransactionNotFoundError

router = APIRouter(prefix="/transactions", tags=["transactions"])

TRANSACTION_CREATE_RATE_LIMIT = "30/minute"


@router.post(
    "/create", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(TRANSACTION_CREATE_RATE_LIMIT)
async def create_transaction(
    request: Request,
    response: Response,
    payload: CreateTransactionRequest,
    use_case: CreateTransactionUseCaseDep,
) -> TransactionResponse:
    """Create a transaction idempotently (201 if new, 200 if key repeats)."""
    dto = CreateTransactionDTO(**payload.model_dump())
    result, created = await use_case.execute(dto)
    if not created:
        response.status_code = status.HTTP_200_OK
    return TransactionResponse(**result.model_dump())


@router.post(
    "/async-process",
    response_model=TransactionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def process_transaction_async(
    payload: CreateTransactionRequest,
    use_case: ProcessTransactionAsyncUseCaseDep,
) -> TransactionResponse:
    """Create a transaction and enqueue it for asynchronous processing."""
    dto = ProcessTransactionAsyncDTO(**payload.model_dump())
    result = await use_case.execute(dto)
    return TransactionResponse(**result.model_dump())


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str, repo: TransactionRepoDep
) -> TransactionResponse:
    """Fetch a single transaction by its id."""
    transaction = await repo.find_by_id(transaction_id)
    if transaction is None:
        raise TransactionNotFoundError(transaction_id)
    return TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        monto=transaction.monto,
        tipo=transaction.tipo,
        status=transaction.status,
        idempotency_key=transaction.idempotency_key,
        created_at=transaction.created_at,
        processed_at=transaction.processed_at,
    )


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    repo: TransactionRepoDep,
    page: Annotated[int, Query(ge=1)] = DEFAULT_PAGE,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> TransactionListResponse:
    """List transactions with pagination and an optional status filter."""
    transactions, total = await repo.list_paginated(page, limit, status_filter)
    return TransactionListResponse(
        items=[
            TransactionResponse(
                id=t.id,
                user_id=t.user_id,
                monto=t.monto,
                tipo=t.tipo,
                status=t.status,
                idempotency_key=t.idempotency_key,
                created_at=t.created_at,
                processed_at=t.processed_at,
            )
            for t in transactions
        ],
        total=total,
        page=page,
        limit=limit,
    )
