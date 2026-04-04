from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlatformBase(BaseModel):
    name: str
    company_id: int | None = None


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: str | None = None
    company_id: int | None = None


class PlatformRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company_id: int | None
    created_at: datetime
    updated_at: datetime
