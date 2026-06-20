from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.user_list_entry import UserListEntry


class UserList(Base, TimestampMixin):
    __tablename__ = "user_lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_public: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="lists",
        lazy="selectin",
    )
    entries: Mapped[list[UserListEntry]] = relationship(
        "UserListEntry",
        back_populates="list",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="UserListEntry.position",
    )
