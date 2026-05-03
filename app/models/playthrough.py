from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_in_collection import GameInCollection


class PlaythroughStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    PLAYING = "PLAYING"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    ON_HOLD = "ON_HOLD"


class Playthrough(Base, TimestampMixin):
    __tablename__ = "playthroughs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_in_collection_id: Mapped[int] = mapped_column(
        ForeignKey("games_in_collection.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[PlaythroughStatus] = mapped_column(
        Enum(PlaythroughStatus, name="playthroughstatus"),
        nullable=False,
    )
    started_at: Mapped[date | None] = mapped_column(Date)
    # completed_at and completion_time are only meaningful when status is COMPLETED.
    # Enforcement is at the application/schema layer, not the database layer.
    completed_at: Mapped[date | None] = mapped_column(Date)
    completion_time: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    game_in_collection: Mapped[GameInCollection] = relationship(
        "GameInCollection",
        back_populates="playthroughs",
        lazy="selectin",
    )
