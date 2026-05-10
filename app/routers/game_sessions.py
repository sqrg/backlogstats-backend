from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.game_session import GameSession
from app.models.user import User
from app.schemas.game_session import GameSessionRead, GameSessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=list[GameSessionRead])
def list_sessions(
    game_in_collection_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GameSession]:
    stmt = (
        select(GameSession)
        .join(GameInCollection)
        .where(GameInCollection.user_id == current_user.id)
    )
    if game_in_collection_id is not None:
        stmt = stmt.where(GameSession.game_in_collection_id == game_in_collection_id)
    stmt = stmt.order_by(GameSession.created_at.desc()).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get("/{id}", response_model=GameSessionRead)
def get_session(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameSession:
    session = db.get(GameSession, id)
    if not session or session.game_in_collection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{id}", response_model=GameSessionRead)
def update_session(
    id: int,
    body: GameSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameSession:
    session = db.get(GameSession, id)
    if not session or session.game_in_collection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(session, key, value)

    if (
        session.started_at is not None
        and session.ended_at is not None
        and session.ended_at < session.started_at
    ):
        raise HTTPException(
            status_code=422, detail="ended_at must be on or after started_at"
        )

    db.commit()
    db.refresh(session)
    return session


@router.delete("/{id}", status_code=204)
def delete_session(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    session = db.get(GameSession, id)
    if not session or session.game_in_collection.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
