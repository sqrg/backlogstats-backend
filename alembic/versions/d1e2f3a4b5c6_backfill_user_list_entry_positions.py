"""backfill_user_list_entry_positions

Revision ID: d1e2f3a4b5c6
Revises: 097c0cdf6e70
Create Date: 2026-05-31 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: str | None = "097c0cdf6e70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Give every existing entry a deterministic, gap-free position within its
    # list (0-based, ordered by id) so manual reordering has a stable baseline.
    # Correlated subquery form works on both PostgreSQL and SQLite.
    op.execute(
        """
        UPDATE user_list_entries
        SET position = (
            SELECT COUNT(*)
            FROM user_list_entries AS e2
            WHERE e2.list_id = user_list_entries.list_id
              AND e2.id < user_list_entries.id
        )
        """
    )


def downgrade() -> None:
    op.execute("UPDATE user_list_entries SET position = NULL")
