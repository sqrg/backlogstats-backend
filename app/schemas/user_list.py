from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user_list_entry import UserListEntryRead


class UserListCreate(BaseModel):
    name: str
    is_public: bool = False


class UserListUpdate(BaseModel):
    name: str | None = None
    is_public: bool | None = None


class UserListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    is_public: bool
    entries: list[UserListEntryRead]
    created_at: datetime
    updated_at: datetime


class PublicUserListRead(BaseModel):
    id: int
    username: str
    name: str
    is_public: bool
    entries: list[UserListEntryRead]
    created_at: datetime
    updated_at: datetime
