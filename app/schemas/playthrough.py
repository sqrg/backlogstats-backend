from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.playthrough import PlaythroughStatus


class PlaythroughBase(BaseModel):
    game_in_collection_id: int
    status: PlaythroughStatus
    started_at: date | None = None
    completed_at: date | None = None
    completion_time: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def check_completion_fields(self) -> "PlaythroughBase":
        if self.status != PlaythroughStatus.COMPLETED:
            if self.completed_at is not None:
                raise ValueError(
                    "completed_at can only be set when status is COMPLETED"
                )
            if self.completion_time is not None:
                raise ValueError(
                    "completion_time can only be set when status is COMPLETED"
                )
        return self


class PlaythroughCreate(PlaythroughBase):
    pass


class PlaythroughUpdate(BaseModel):
    game_in_collection_id: int | None = None
    status: PlaythroughStatus | None = None
    started_at: date | None = None
    completed_at: date | None = None
    completion_time: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def check_completion_fields(self) -> "PlaythroughUpdate":
        if self.status is not None and self.status != PlaythroughStatus.COMPLETED:
            if self.completed_at is not None:
                raise ValueError(
                    "completed_at can only be set when status is COMPLETED"
                )
            if self.completion_time is not None:
                raise ValueError(
                    "completion_time can only be set when status is COMPLETED"
                )
        return self


class PlaythroughRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_in_collection_id: int
    status: PlaythroughStatus
    started_at: date | None
    completed_at: date | None
    completion_time: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
