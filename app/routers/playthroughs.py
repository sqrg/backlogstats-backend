from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.playthrough import Playthrough
from app.models.user import User
from app.schemas.playthrough import (
    PlaythroughCreate,
    PlaythroughRead,
    PlaythroughUpdate,
)

router = APIRouter(prefix="/playthroughs", tags=["playthroughs"])


@router.get("/", response_model=list[PlaythroughRead])
def list_playthroughs(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Playthrough]:
    return db.execute(select(Playthrough).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=PlaythroughRead)
def get_playthrough(id: int, db: Session = Depends(get_db)) -> Playthrough:
    playthrough = db.get(Playthrough, id)
    if not playthrough:
        raise HTTPException(status_code=404, detail="Playthrough not found")
    return playthrough


@router.post("/", response_model=PlaythroughRead, status_code=201)
def create_playthrough(
    body: PlaythroughCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Playthrough:
    playthrough = Playthrough(**body.model_dump())
    db.add(playthrough)
    db.commit()
    db.refresh(playthrough)
    return playthrough


@router.put("/{id}", response_model=PlaythroughRead)
def update_playthrough(
    id: int,
    body: PlaythroughUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Playthrough:
    playthrough = db.get(Playthrough, id)
    if not playthrough:
        raise HTTPException(status_code=404, detail="Playthrough not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(playthrough, key, value)
    db.commit()
    db.refresh(playthrough)
    return playthrough


@router.delete("/{id}", status_code=204)
def delete_playthrough(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    playthrough = db.get(Playthrough, id)
    if not playthrough:
        raise HTTPException(status_code=404, detail="Playthrough not found")
    db.delete(playthrough)
    db.commit()
