from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.series import Series


class GameSeries(Base):
    __tablename__ = "game_series"

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
        primary_key=True,
    )
    series_id: Mapped[int] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"),
        primary_key=True,
    )

    game: Mapped[Game] = relationship(
        "Game",
        back_populates="game_series",
        lazy="selectin",
    )
    series: Mapped[Series] = relationship(
        "Series",
        back_populates="game_series",
        lazy="selectin",
    )
