"""add_username_to_users

Revision ID: e3a1f2c4b890
Revises: db0bdae8d334
Create Date: 2026-05-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3a1f2c4b890"
down_revision: Union[str, Sequence[str], None] = "db0bdae8d334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("username", sa.String(length=30), nullable=True))
    op.create_unique_constraint("uq_users_username", "users", ["username"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_column("users", "username")
