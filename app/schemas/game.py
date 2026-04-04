from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameBase(BaseModel):
    name: str
    igdb_id: int | None = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    name: str | None = None
    igdb_id: int | None = None
    summary: str | None = None
    cover_image_id: str | None = None
    first_release_date: int | None = None
    rating: float | None = None


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    igdb_id: int | None
    summary: str | None
    cover_image_id: str | None
    first_release_date: int | None
    rating: float | None
    created_at: datetime
    updated_at: datetime
