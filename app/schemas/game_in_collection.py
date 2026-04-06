from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cover_image_id: str | None


class PlatformSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class GameInCollectionCreate(BaseModel):
    game_id: int
    platform_id: int
    # user_id is derived from the auth token — not accepted in request body


class GameInCollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game: GameSummary
    platform: PlatformSummary
    created_at: datetime
    updated_at: datetime
