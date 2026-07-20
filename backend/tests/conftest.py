"""Shared pytest fixtures: in-memory DB, async client, and DI overrides."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.dependencies import (
    get_ai_mode_repository,
    get_db_session,
    get_queue_service,
)
from app.domain.interfaces.ai_mode_repository import AIModeRepositoryPort
from app.domain.interfaces.queue_service import QueueServicePort
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import (  # noqa: F401
    assistant_log_model,
    rpa_extraction_model,
    transaction_model,
)
from app.main import app


class FakeQueueService(QueueServicePort):
    """In-memory QueueServicePort double used in integration tests."""

    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    async def enqueue(self, queue_name: str, payload: str) -> None:
        self.items.append((queue_name, payload))

    async def dequeue(self, queue_name: str) -> str | None:
        for index, (name, _payload) in enumerate(self.items):
            if name == queue_name:
                return self.items.pop(index)[1]
        return None


class FakeAIModeRepository(AIModeRepositoryPort):
    """In-memory AIModeRepositoryPort double used in integration tests."""

    def __init__(self) -> None:
        self._force_mock = False

    async def get_force_mock(self) -> bool:
        return self._force_mock

    async def set_force_mock(self, value: bool) -> None:
        self._force_mock = value


@pytest.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def fake_queue() -> FakeQueueService:
    return FakeQueueService()


@pytest.fixture
async def fake_ai_mode_repo() -> FakeAIModeRepository:
    return FakeAIModeRepository()


@pytest.fixture
async def client(
    db_session: AsyncSession,
    fake_queue: FakeQueueService,
    fake_ai_mode_repo: FakeAIModeRepository,
) -> AsyncGenerator[AsyncClient]:
    async def _override_get_db_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    def _override_get_queue_service() -> QueueServicePort:
        return fake_queue

    def _override_get_ai_mode_repository() -> AIModeRepositoryPort:
        return fake_ai_mode_repo

    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_queue_service] = _override_get_queue_service
    app.dependency_overrides[get_ai_mode_repository] = _override_get_ai_mode_repository
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
