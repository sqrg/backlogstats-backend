from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_games: int
    completed: int
    playing: int
    abandoned: int
    on_hold: int
    not_started: int
    no_playthroughs: int


class HoursByYear(BaseModel):
    year: int
    hours: int


class HoursByMonth(BaseModel):
    year: int
    month: int
    hours: int


class GenreAvg(BaseModel):
    genre_name: str
    avg_hours: float
    count: int


class PlatformAvg(BaseModel):
    platform_name: str
    avg_hours: float
    count: int


class AvgCompletionTime(BaseModel):
    overall_avg: float | None
    by_genre: list[GenreAvg]
    by_platform: list[PlatformAvg]


class CompletionRate(BaseModel):
    total_games: int
    completed_pct: float
    playing_pct: float
    abandoned_pct: float
    on_hold_pct: float
    not_started_pct: float
    no_playthrough_pct: float


class PlatformStat(BaseModel):
    platform_name: str
    total_games: int
    completed_games: int


class GenreStat(BaseModel):
    genre_name: str
    total_games: int
    completed_games: int


class AvgHoursPerDay(BaseModel):
    last_7_days: float
    last_30_days: float
    last_365_days: float


class CompletedByPlatformEntry(BaseModel):
    platform_name: str
    completed_games: int
