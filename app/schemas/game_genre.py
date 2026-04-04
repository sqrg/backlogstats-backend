from pydantic import BaseModel, ConfigDict


class GameGenreBase(BaseModel):
    game_id: int
    genre_id: int


class GameGenreCreate(GameGenreBase):
    pass


class GameGenreUpdate(BaseModel):
    game_id: int | None = None
    genre_id: int | None = None


class GameGenreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: int
    genre_id: int
