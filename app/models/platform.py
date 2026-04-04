from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.game_in_collection import GameInCollection


class Platform(Base, TimestampMixin):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"),
    )

    company: Mapped[Company | None] = relationship(
        "Company",
        back_populates="platforms",
        lazy="selectin",
    )
    collection_entries: Mapped[list[GameInCollection]] = relationship(
        "GameInCollection",
        back_populates="platform",
        lazy="selectin",
    )
