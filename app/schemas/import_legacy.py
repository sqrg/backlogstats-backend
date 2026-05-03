from datetime import date

from pydantic import BaseModel


class ParsedLegacyRow(BaseModel):
    row_id: str
    title_raw: str
    platform_raw: str | None
    platform_normalized: str
    platform_note: str | None
    hours: float
    completed_at: date | None
    is_dlc: bool
    is_handheld: bool
    year_sheet: int
