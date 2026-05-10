from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


class GameSessionCreate(BaseModel):
    completion_time: float
    started_at: date | None = None
    ended_at: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def check_dates(self) -> "GameSessionCreate":
        if self.completion_time <= 0:
            raise ValueError("completion_time must be greater than zero")
        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValueError("ended_at must be on or after started_at")
        return self


class GameSessionUpdate(BaseModel):
    completion_time: float | None = None
    started_at: date | None = None
    ended_at: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def check_dates(self) -> "GameSessionUpdate":
        if self.completion_time is not None and self.completion_time <= 0:
            raise ValueError("completion_time must be greater than zero")
        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValueError("ended_at must be on or after started_at")
        return self


class GameSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_in_collection_id: int
    started_at: date | None
    ended_at: date | None
    completion_time: float
    notes: str | None
    created_at: datetime
    updated_at: datetime
