from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SeriesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int
    name: str
    slug: str | None
    created_at: datetime
    updated_at: datetime


class GameInSeriesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int | None
    name: str
    cover_image_id: str | None


class SeriesWithGamesRead(SeriesRead):
    games: list[GameInSeriesRead]
