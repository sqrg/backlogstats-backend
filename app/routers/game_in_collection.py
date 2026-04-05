from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.user import User
from app.schemas.game_in_collection import (
    GameInCollectionCreate,
    GameInCollectionRead,
    GameInCollectionUpdate,
)

router = APIRouter(prefix="/collection", tags=["collection"])


@router.get("/", response_model=list[GameInCollectionRead])
def list_collection(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[GameInCollection]:
    return (
        db.execute(select(GameInCollection).offset(offset).limit(limit)).scalars().all()
    )


@router.get("/{id}", response_model=GameInCollectionRead)
def get_collection_entry(id: int, db: Session = Depends(get_db)) -> GameInCollection:
    entry = db.get(GameInCollection, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    return entry


@router.post("/", response_model=GameInCollectionRead, status_code=201)
def create_collection_entry(
    body: GameInCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameInCollection:
    entry = GameInCollection(**body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{id}", response_model=GameInCollectionRead)
def update_collection_entry(
    id: int,
    body: GameInCollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameInCollection:
    entry = db.get(GameInCollection, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{id}", status_code=204)
def delete_collection_entry(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    entry = db.get(GameInCollection, id)
    if not entry:
        raise HTTPException(status_code=404, detail="Collection entry not found")
    db.delete(entry)
    db.commit()
