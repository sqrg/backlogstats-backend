from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.user_list import UserList


class UserListEntry(Base, TimestampMixin):
    __tablename__ = "user_list_entries"
    __table_args__ = (UniqueConstraint("list_id", "game_id", name="uq_list_game"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    list_id: Mapped[int] = mapped_column(
        ForeignKey("user_lists.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int | None] = mapped_column(Integer)

    list: Mapped[UserList] = relationship(
        "UserList",
        back_populates="entries",
        lazy="selectin",
    )
    game: Mapped[Game] = relationship(
        "Game",
        back_populates="list_entries",
        lazy="selectin",
    )
