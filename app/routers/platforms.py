from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("/", response_model=list[PlatformRead])
def list_platforms(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Platform]:
    return db.execute(select(Platform).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=PlatformRead)
def get_platform(id: int, db: Session = Depends(get_db)) -> Platform:
    platform = db.get(Platform, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.post("/", response_model=PlatformRead, status_code=201)
def create_platform(body: PlatformCreate, db: Session = Depends(get_db)) -> Platform:
    platform = Platform(**body.model_dump())
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return platform


@router.put("/{id}", response_model=PlatformRead)
def update_platform(
    id: int, body: PlatformUpdate, db: Session = Depends(get_db)
) -> Platform:
    platform = db.get(Platform, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(platform, key, value)
    db.commit()
    db.refresh(platform)
    return platform


@router.delete("/{id}", status_code=204)
def delete_platform(id: int, db: Session = Depends(get_db)) -> None:
    platform = db.get(Platform, id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    db.delete(platform)
    db.commit()
