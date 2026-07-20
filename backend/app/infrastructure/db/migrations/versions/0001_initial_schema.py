"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("tipo", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint(
        "uq_transactions_idempotency_key", "transactions", ["idempotency_key"]
    )
    op.create_index(
        "ix_transactions_idempotency_key", "transactions", ["idempotency_key"]
    )
    op.create_index("ix_transactions_status", "transactions", ["status"])

    op.create_table(
        "assistant_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=True),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "rpa_extractions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("term", sa.String(length=255), nullable=False),
        sa.Column("paragraph", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("rpa_extractions")
    op.drop_table("assistant_logs")
    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_idempotency_key", table_name="transactions")
    op.drop_constraint(
        "uq_transactions_idempotency_key", "transactions", type_="unique"
    )
    op.drop_table("transactions")
