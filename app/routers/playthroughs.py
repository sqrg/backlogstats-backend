from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.playthrough import Playthrough
from app.models.user import User
from app.schemas.playthrough import PlaythroughRead, PlaythroughUpdate

router = APIRouter(prefix="/playthroughs", tags=["playthroughs"])


@router.get("/", response_model=list[PlaythroughRead])
def list_playthroughs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Playthrough]:
    return (
        db.execute(
            select(Playthrough)
            .join(GameInCollection)
            .where(GameInCollection.user_id == current_user.id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )


@router.get("/{id}", response_model=PlaythroughRead)
def get_playthrough(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Playthrough:
    playthrough = db.get(Playthrough, id)
    if not playthrough or playthrough.game_in_collection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Playthrough not found")
    return playthrough


@router.put("/{id}", response_model=PlaythroughRead)
def update_playthrough(
    id: int,
    body: PlaythroughUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Playthrough:
    playthrough = db.get(Playthrough, id)
    if not playthrough or playthrough.game_in_collection.user_id != current_user.id:
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
    if not playthrough or playthrough.game_in_collection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Playthrough not found")
    db.delete(playthrough)
    db.commit()
