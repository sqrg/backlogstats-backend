from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_series import GameSeries


class Series(Base, TimestampMixin):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    igdb_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str | None] = mapped_column(String, nullable=True)

    game_series: Mapped[list[GameSeries]] = relationship(
        "GameSeries",
        back_populates="series",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def games(self) -> list:
        return [gs.game for gs in self.game_series]
