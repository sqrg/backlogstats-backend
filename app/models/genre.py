from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_genre import GameGenre


class Genre(Base, TimestampMixin):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    game_genres: Mapped[list[GameGenre]] = relationship(
        "GameGenre",
        back_populates="genre",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
