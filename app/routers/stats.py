from collections import defaultdict
from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.playthrough import Playthrough, PlaythroughStatus
from app.models.user import User
from app.schemas.stats import (
    AvgCompletionTime,
    AvgHoursPerDay,
    CompletedByPlatformEntry,
    CompletionRate,
    GenreAvg,
    GenreStat,
    HoursByMonth,
    HoursByYear,
    PlatformAvg,
    PlatformStat,
    StatsSummary,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.execute(
        select(GameInCollection).where(GameInCollection.user_id == current_user.id)
    ).scalars().all()

    counts: dict[PlaythroughStatus, int] = {s: 0 for s in PlaythroughStatus}
    no_playthroughs = 0
    for entry in entries:
        status = entry.current_status
        if status is None:
            no_playthroughs += 1
        else:
            counts[status] += 1

    return StatsSummary(
        total_games=len(entries),
        completed=counts[PlaythroughStatus.COMPLETED],
        playing=counts[PlaythroughStatus.PLAYING],
        abandoned=counts[PlaythroughStatus.ABANDONED],
        on_hold=counts[PlaythroughStatus.ON_HOLD],
        not_started=counts[PlaythroughStatus.NOT_STARTED],
        no_playthroughs=no_playthroughs,
    )


@router.get("/hours-by-year", response_model=list[HoursByYear])
def get_hours_by_year(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playthroughs = db.execute(
        select(Playthrough)
        .join(GameInCollection, Playthrough.game_in_collection_id == GameInCollection.id)
        .where(
            GameInCollection.user_id == current_user.id,
            Playthrough.status == PlaythroughStatus.COMPLETED,
            Playthrough.completed_at.is_not(None),
            Playthrough.completion_time.is_not(None),
        )
    ).scalars().all()

    totals: dict[int, float] = defaultdict(float)
    for p in playthroughs:
        totals[p.completed_at.year] += float(p.completion_time)
    return [
        HoursByYear(year=year, hours=hours)
        for year, hours in sorted(totals.items())
    ]


@router.get("/hours-by-month", response_model=list[HoursByMonth])
def get_hours_by_month(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    twelve_months_ago = today.replace(year=today.year - 1, day=1)

    playthroughs = db.execute(
        select(Playthrough)
        .join(GameInCollection, Playthrough.game_in_collection_id == GameInCollection.id)
        .where(
            GameInCollection.user_id == current_user.id,
            Playthrough.status == PlaythroughStatus.COMPLETED,
            Playthrough.completed_at.is_not(None),
            Playthrough.completion_time.is_not(None),
            Playthrough.completed_at >= twelve_months_ago,
        )
    ).scalars().all()

    totals: dict[tuple[int, int], float] = defaultdict(float)
    for p in playthroughs:
        totals[(p.completed_at.year, p.completed_at.month)] += float(p.completion_time)
    return [
        HoursByMonth(year=year, month=month, hours=hours)
        for (year, month), hours in sorted(totals.items())
    ]


@router.get("/completed-by-platform", response_model=list[CompletedByPlatformEntry])
def get_completed_by_platform(
    period: Literal["all", "last_12_months"] = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [
        GameInCollection.user_id == current_user.id,
        Playthrough.status == PlaythroughStatus.COMPLETED,
        Playthrough.completed_at.is_not(None),
    ]
    if period == "last_12_months":
        today = date.today()
        twelve_months_ago = today.replace(year=today.year - 1, day=1)
        filters.append(Playthrough.completed_at >= twelve_months_ago)

    playthroughs = db.execute(
        select(Playthrough)
        .join(GameInCollection, Playthrough.game_in_collection_id == GameInCollection.id)
        .where(*filters)
    ).scalars().all()

    counts: dict[str, int] = defaultdict(int)
    for p in playthroughs:
        counts[p.game_in_collection.platform.name] += 1

    return sorted(
        [
            CompletedByPlatformEntry(platform_name=name, completed_games=n)
            for name, n in counts.items()
        ],
        key=lambda e: -e.completed_games,
    )


@router.get("/avg-completion-time", response_model=AvgCompletionTime)
def get_avg_completion_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    playthroughs = db.execute(
        select(Playthrough)
        .join(GameInCollection, Playthrough.game_in_collection_id == GameInCollection.id)
        .where(
            GameInCollection.user_id == current_user.id,
            Playthrough.status == PlaythroughStatus.COMPLETED,
            Playthrough.completion_time.is_not(None),
        )
    ).scalars().all()

    all_times = [float(p.completion_time) for p in playthroughs]
    overall_avg = sum(all_times) / len(all_times) if all_times else None

    genre_times: dict[str, list[float]] = defaultdict(list)
    platform_times: dict[str, list[float]] = defaultdict(list)
    for p in playthroughs:
        gic = p.game_in_collection
        ct = float(p.completion_time)
        for gg in gic.game.game_genres:
            genre_times[gg.genre.name].append(ct)
        platform_times[gic.platform.name].append(ct)

    by_genre = sorted(
        [
            GenreAvg(genre_name=name, avg_hours=sum(times) / len(times), count=len(times))
            for name, times in genre_times.items()
        ],
        key=lambda x: -x.count,
    )
    by_platform = sorted(
        [
            PlatformAvg(platform_name=name, avg_hours=sum(times) / len(times), count=len(times))
            for name, times in platform_times.items()
        ],
        key=lambda x: -x.count,
    )

    return AvgCompletionTime(overall_avg=overall_avg, by_genre=by_genre, by_platform=by_platform)


@router.get("/completion-rate", response_model=CompletionRate)
def get_completion_rate(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.execute(
        select(GameInCollection).where(GameInCollection.user_id == current_user.id)
    ).scalars().all()

    total = len(entries)
    if total == 0:
        return CompletionRate(
            total_games=0,
            completed_pct=0.0,
            playing_pct=0.0,
            abandoned_pct=0.0,
            on_hold_pct=0.0,
            not_started_pct=0.0,
            no_playthrough_pct=0.0,
        )

    counts: dict[PlaythroughStatus, int] = {s: 0 for s in PlaythroughStatus}
    no_playthrough = 0
    for entry in entries:
        status = entry.current_status
        if status is None:
            no_playthrough += 1
        else:
            counts[status] += 1

    def pct(n: int) -> float:
        return round(n / total * 100, 1)

    return CompletionRate(
        total_games=total,
        completed_pct=pct(counts[PlaythroughStatus.COMPLETED]),
        playing_pct=pct(counts[PlaythroughStatus.PLAYING]),
        abandoned_pct=pct(counts[PlaythroughStatus.ABANDONED]),
        on_hold_pct=pct(counts[PlaythroughStatus.ON_HOLD]),
        not_started_pct=pct(counts[PlaythroughStatus.NOT_STARTED]),
        no_playthrough_pct=pct(no_playthrough),
    )


@router.get("/platform-breakdown", response_model=list[PlatformStat])
def get_platform_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.execute(
        select(GameInCollection).where(GameInCollection.user_id == current_user.id)
    ).scalars().all()

    data: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "completed": 0})
    for entry in entries:
        name = entry.platform.name
        data[name]["total"] += 1
        if entry.current_status == PlaythroughStatus.COMPLETED:
            data[name]["completed"] += 1

    return sorted(
        [
            PlatformStat(platform_name=name, total_games=d["total"], completed_games=d["completed"])
            for name, d in data.items()
        ],
        key=lambda x: -x.total_games,
    )


@router.get("/avg-hours-per-day", response_model=AvgHoursPerDay)
def get_avg_hours_per_day(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    windows = (7, 30, 365)
    earliest = today - timedelta(days=max(windows) - 1)

    playthroughs = db.execute(
        select(Playthrough)
        .join(GameInCollection, Playthrough.game_in_collection_id == GameInCollection.id)
        .where(
            GameInCollection.user_id == current_user.id,
            Playthrough.status == PlaythroughStatus.COMPLETED,
            Playthrough.completed_at.is_not(None),
            Playthrough.completion_time.is_not(None),
            Playthrough.completed_at >= earliest,
        )
    ).scalars().all()

    def avg_for(days: int) -> float:
        cutoff = today - timedelta(days=days - 1)
        total = sum(
            float(p.completion_time) for p in playthroughs if p.completed_at >= cutoff
        )
        return round(total / days, 2)

    return AvgHoursPerDay(
        last_7_days=avg_for(7),
        last_30_days=avg_for(30),
        last_365_days=avg_for(365),
    )


@router.get("/genre-breakdown", response_model=list[GenreStat])
def get_genre_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = db.execute(
        select(GameInCollection).where(GameInCollection.user_id == current_user.id)
    ).scalars().all()

    data: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "completed": 0})
    for entry in entries:
        is_completed = entry.current_status == PlaythroughStatus.COMPLETED
        for gg in entry.game.game_genres:
            name = gg.genre.name
            data[name]["total"] += 1
            if is_completed:
                data[name]["completed"] += 1

    return sorted(
        [
            GenreStat(genre_name=name, total_games=d["total"], completed_games=d["completed"])
            for name, d in data.items()
        ],
        key=lambda x: -x.total_games,
    )
