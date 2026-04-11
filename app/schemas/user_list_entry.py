from datetime import datetime

from pydantic import BaseModel, ConfigDict

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


class UserListEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    game_id: int
    game: GameSummary
    position: int | None
    created_at: datetime
    updated_at: datetime
