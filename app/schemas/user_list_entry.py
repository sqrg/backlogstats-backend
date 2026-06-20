from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.game_in_collection import GameSummary


class UserListEntryBase(BaseModel):
    list_id: int
    game_id: int
    position: int | None = None


class UserListEntryCreate(UserListEntryBase):
    pass


class UserListEntryUpdate(BaseModel):
    list_id: int | None = None
    game_id: int | None = None
    position: int | None = None


class UserListEntryReorder(BaseModel):
    # Full ordering of a list's entries, top to bottom.
    entry_ids: list[int] = Field(..., min_length=1)


class UserListEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    game_id: int
    game: GameSummary
    position: int | None
    created_at: datetime
    updated_at: datetime
