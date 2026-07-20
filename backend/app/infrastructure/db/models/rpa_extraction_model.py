"""SQLAlchemy ORM model for RPA extractions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base

MAX_TERM_LENGTH = 255
MAX_SOURCE_URL_LENGTH = 2048


class RpaExtractionModel(Base):
    """ORM representation of an RpaExtraction row."""

    __tablename__ = "rpa_extractions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term: Mapped[str] = mapped_column(String(MAX_TERM_LENGTH), nullable=False)
    paragraph: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(
        String(MAX_SOURCE_URL_LENGTH), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
