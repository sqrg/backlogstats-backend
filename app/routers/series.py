from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.series import Series
from app.schemas.series import SeriesRead, SeriesWithGamesRead

router = APIRouter(prefix="/series", tags=["series"])


@router.get("/", response_model=list[SeriesRead])
def list_series(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Series]:
    return db.execute(select(Series).offset(offset).limit(limit)).scalars().all()


# NOTE: /igdb/{igdb_id} must be registered before /{id} so FastAPI does not
# treat the literal string "igdb" as the value of the {id} path parameter.
@router.get("/igdb/{igdb_id}", response_model=SeriesWithGamesRead)
def get_series_by_igdb_id(igdb_id: int, db: Session = Depends(get_db)) -> Series:
    series = db.execute(
        select(Series).where(Series.igdb_id == igdb_id)
    ).scalar_one_or_none()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    return series


@router.get("/{id}", response_model=SeriesWithGamesRead)
def get_series(id: int, db: Session = Depends(get_db)) -> Series:
    series = db.get(Series, id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    return series
