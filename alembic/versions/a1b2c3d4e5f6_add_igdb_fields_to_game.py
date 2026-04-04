"""add_igdb_fields_to_game

Revision ID: a1b2c3d4e5f6
Revises: 23b1eaaee221
Create Date: 2026-04-04 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "23b1eaaee221"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("games", sa.Column("cover_image_id", sa.String(), nullable=True))
    op.add_column("games", sa.Column("first_release_date", sa.Integer(), nullable=True))
    op.add_column("games", sa.Column("rating", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("games", "rating")
    op.drop_column("games", "first_release_date")
    op.drop_column("games", "cover_image_id")
    op.drop_column("games", "summary")
