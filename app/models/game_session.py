from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_in_collection import GameInCollection


class GameSession(Base, TimestampMixin):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_in_collection_id: Mapped[int] = mapped_column(
        ForeignKey("games_in_collection.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[date | None] = mapped_column(Date)
    ended_at: Mapped[date | None] = mapped_column(Date)
    completion_time: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    game_in_collection: Mapped[GameInCollection] = relationship(
        "GameInCollection",
        back_populates="sessions",
        lazy="selectin",
    )
