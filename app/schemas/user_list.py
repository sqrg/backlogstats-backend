from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user_list_entry import UserListEntryRead


class UserListBase(BaseModel):
    user_id: int
    name: str
    is_public: bool = False


class UserListCreate(UserListBase):
    pass


class UserListUpdate(BaseModel):
    user_id: int | None = None
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
