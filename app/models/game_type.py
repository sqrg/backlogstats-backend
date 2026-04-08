from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class GameType(Base, TimestampMixin):
    __tablename__ = "game_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
