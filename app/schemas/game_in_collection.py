from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameInCollectionBase(BaseModel):
    user_id: int
    game_id: int
    platform_id: int


class GameInCollectionCreate(GameInCollectionBase):
    pass


class GameInCollectionUpdate(BaseModel):
    user_id: int | None = None
    game_id: int | None = None
    platform_id: int | None = None


class GameInCollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    game_id: int
    platform_id: int
    created_at: datetime
    updated_at: datetime
