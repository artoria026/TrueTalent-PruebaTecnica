"""SQLAlchemy ORM model for transactions, kept separate from the domain entity."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base

MAX_USER_ID_LENGTH = 128
MAX_STATUS_LENGTH = 32
MAX_TYPE_LENGTH = 32
MAX_IDEMPOTENCY_KEY_LENGTH = 255


class TransactionModel(Base):
    """ORM representation of a Transaction row."""

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(MAX_USER_ID_LENGTH), nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[str] = mapped_column(String(MAX_TYPE_LENGTH), nullable=False)
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(
        String(MAX_IDEMPOTENCY_KEY_LENGTH), nullable=False, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
