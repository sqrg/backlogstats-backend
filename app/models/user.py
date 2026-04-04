from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.game_in_collection import GameInCollection
    from app.models.user_list import UserList


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String, unique=True)
    hashed_password: Mapped[str | None] = mapped_column(String)
    google_id: Mapped[str | None] = mapped_column(String, unique=True)
    apple_id: Mapped[str | None] = mapped_column(String, unique=True)
    discord_id: Mapped[str | None] = mapped_column(String, unique=True)
    # Steam uses OpenID rather than OAuth2 — treat as a separate, more complex
    # implementation task from the other three providers.
    steam_id: Mapped[str | None] = mapped_column(String, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    collection: Mapped[list[GameInCollection]] = relationship(
        "GameInCollection",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    lists: Mapped[list[UserList]] = relationship(
        "UserList",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
