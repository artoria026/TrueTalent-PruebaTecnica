"""SQLAlchemy ORM model for assistant logs."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base

MAX_USER_ID_LENGTH = 128
MAX_MODEL_NAME_LENGTH = 64
MAX_STATUS_LENGTH = 16


class AssistantLogModel(Base):
    """ORM representation of an AssistantLog row."""

    __tablename__ = "assistant_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(MAX_USER_ID_LENGTH), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(MAX_MODEL_NAME_LENGTH), nullable=False)
    status: Mapped[str] = mapped_column(
        String(MAX_STATUS_LENGTH), nullable=False, default="completed"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
