from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


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
    genres: list[str] = []
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _extract_genres(cls, data: object) -> object:
        # Genres live in a join table; convert ORM object to dict so we can inject them.
        if hasattr(data, "game_genres"):
            genres = [
                gg.genre.name
                for gg in (data.game_genres or [])
                if hasattr(gg, "genre") and gg.genre
            ]
            return {
                "id": data.id,
                "name": data.name,
                "igdb_id": data.igdb_id,
                "summary": getattr(data, "summary", None),
                "cover_image_id": getattr(data, "cover_image_id", None),
                "first_release_date": getattr(data, "first_release_date", None),
                "rating": getattr(data, "rating", None),
                "genres": genres,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data
