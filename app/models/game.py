from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_genre import GameGenre
    from app.models.game_in_collection import GameInCollection
    from app.models.user_list_entry import UserListEntry


class Game(Base, TimestampMixin):
    __tablename__ = "games"
    __table_args__ = (
        # Enforces uniqueness only for manually created games (igdb_id IS NULL).
        # IGDB-sourced games share no such constraint — multiple rows may exist
        # with the same name if they originate from IGDB.
        Index(
            "ix_game_name_manual_unique",
            "name",
            unique=True,
            postgresql_where=text("igdb_id IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    igdb_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_id: Mapped[str | None] = mapped_column(String, nullable=True)
    first_release_date: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    game_genres: Mapped[list[GameGenre]] = relationship(
        "GameGenre",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    collection_entries: Mapped[list[GameInCollection]] = relationship(
        "GameInCollection",
        back_populates="game",
        lazy="selectin",
    )
    list_entries: Mapped[list[UserListEntry]] = relationship(
        "UserListEntry",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
