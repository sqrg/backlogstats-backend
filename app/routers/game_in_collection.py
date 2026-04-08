from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.playthrough import Playthrough, PlaythroughStatus
from app.models.user import User
from app.schemas.game_in_collection import (
    GameInCollectionCreate,
    GameInCollectionRead,
    GameInCollectionWithPlaythroughsRead,
)
from app.schemas.playthrough import PlaythroughCreate, PlaythroughRead

router = APIRouter(prefix="/collection", tags=["collection"])


@router.get("/", response_model=list[GameInCollectionRead])
def list_collection(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GameInCollection]:
    return (
        db.execute(
            select(GameInCollection)
            .where(GameInCollection.user_id == current_user.id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )


@router.get("/{id}", response_model=GameInCollectionWithPlaythroughsRead)
def get_collection_entry(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameInCollection:
    entry = db.get(GameInCollection, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    return entry


@router.post("/", response_model=GameInCollectionRead, status_code=201)
def create_collection_entry(
    body: GameInCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameInCollection:
    entry = GameInCollection(
        user_id=current_user.id,
        game_id=body.game_id,
        platform_id=body.platform_id,
    )
    db.add(entry)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Game already in collection on this platform",
        )
    db.add(
        Playthrough(
            game_in_collection_id=entry.id, status=PlaythroughStatus.NOT_STARTED
        )
    )
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/{id}/playthroughs", response_model=PlaythroughRead, status_code=201)
def create_playthrough(
    id: int,
    body: PlaythroughCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Playthrough:
    entry = db.get(GameInCollection, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    playthrough = Playthrough(game_in_collection_id=id, **body.model_dump())
    db.add(playthrough)
    db.commit()
    db.refresh(playthrough)
    return playthrough


@router.delete("/{id}", status_code=204)
def delete_collection_entry(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    entry = db.get(GameInCollection, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    db.delete(entry)
    db.commit()
