from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.platform import Platform
    from app.models.playthrough import Playthrough
    from app.models.user import User


class GameInCollection(Base, TimestampMixin):
    __tablename__ = "games_in_collection"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "game_id", "platform_id", name="uq_user_game_platform"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="RESTRICT"),
        nullable=False,
    )
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="collection",
        lazy="selectin",
    )
    game: Mapped[Game] = relationship(
        "Game",
        back_populates="collection_entries",
        lazy="selectin",
    )
    platform: Mapped[Platform] = relationship(
        "Platform",
        back_populates="collection_entries",
        lazy="selectin",
    )
    playthroughs: Mapped[list[Playthrough]] = relationship(
        "Playthrough",
        back_populates="game_in_collection",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
