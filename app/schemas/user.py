from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    email: str | None
    google_id: str | None
    apple_id: str | None
    discord_id: str | None
    steam_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserMeUpdate(BaseModel):
    username: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
