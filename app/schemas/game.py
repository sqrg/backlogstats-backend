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


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    igdb_id: int | None
    created_at: datetime
    updated_at: datetime
