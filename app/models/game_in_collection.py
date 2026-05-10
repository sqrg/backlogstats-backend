from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.playthrough import PlaythroughStatus

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.game_session import GameSession
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
    base_game_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("games_in_collection.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
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
    sessions: Mapped[list[GameSession]] = relationship(
        "GameSession",
        back_populates="game_in_collection",
        lazy="select",
        cascade="all, delete-orphan",
    )
    base_game: Mapped[GameInCollection | None] = relationship(
        "GameInCollection",
        foreign_keys="[GameInCollection.base_game_entry_id]",
        remote_side="[GameInCollection.id]",
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list[GameInCollection]] = relationship(
        "GameInCollection",
        foreign_keys="[GameInCollection.base_game_entry_id]",
        back_populates="base_game",
        lazy="selectin",
    )

    @property
    def current_status(self) -> PlaythroughStatus | None:
        if not self.playthroughs:
            return None
        priority = {
            PlaythroughStatus.COMPLETED: 4,
            PlaythroughStatus.PLAYING: 3,
            PlaythroughStatus.ON_HOLD: 2,
            PlaythroughStatus.NOT_STARTED: 1,
            PlaythroughStatus.ABANDONED: 0,
        }
        return max(self.playthroughs, key=lambda p: priority[p.status]).status

    @property
    def completed_years(self) -> list[int]:
        """Distinct years in which this entry has a COMPLETED playthrough.

        Returned sorted ascending so clients can render them deterministically.
        """
        years: set[int] = set()
        for p in self.playthroughs:
            if p.status == PlaythroughStatus.COMPLETED and p.completed_at:
                years.add(p.completed_at.year)
        return sorted(years)

    @property
    def last_completed_at(self) -> date | None:
        """Most recent completed_at across COMPLETED playthroughs, or None."""
        dates = [
            p.completed_at
            for p in self.playthroughs
            if p.status == PlaythroughStatus.COMPLETED and p.completed_at
        ]
        return max(dates) if dates else None
