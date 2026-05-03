"""widen completion_time to numeric(6,2)

Revision ID: c7e9a2d1f3b4
Revises: e3a1f2c4b890
Create Date: 2026-05-02 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c7e9a2d1f3b4"
down_revision: Union[str, Sequence[str], None] = "e3a1f2c4b890"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Promote playthroughs.completion_time from Integer to Numeric(6, 2)."""
    op.alter_column(
        "playthroughs",
        "completion_time",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=6, scale=2),
        existing_nullable=True,
        postgresql_using="completion_time::numeric(6,2)",
    )


def downgrade() -> None:
    """Revert playthroughs.completion_time to Integer (truncates decimals)."""
    op.alter_column(
        "playthroughs",
        "completion_time",
        existing_type=sa.Numeric(precision=6, scale=2),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="completion_time::integer",
    )
