from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.playthrough import PlaythroughStatus
from app.schemas.playthrough import PlaythroughRead


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


class BaseGameSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game: GameSummary
    platform: PlatformSummary


class GameInCollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game: GameSummary
    platform: PlatformSummary
    base_game: BaseGameSummary | None
    current_status: PlaythroughStatus | None
    created_at: datetime
    updated_at: datetime


class GameInCollectionWithPlaythroughsRead(GameInCollectionRead):
    playthroughs: list[PlaythroughRead]
    children: list[BaseGameSummary]


class GameInCollectionSetBaseGame(BaseModel):
    base_game_entry_id: int | None


class GameInCollectionImportDLC(BaseModel):
    igdb_ids: list[int]
