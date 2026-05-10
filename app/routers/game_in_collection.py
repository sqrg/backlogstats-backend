import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game import Game
from app.models.game_in_collection import GameInCollection
from app.models.game_session import GameSession
from app.models.playthrough import Playthrough, PlaythroughStatus
from app.models.user import User
from app.schemas.game_in_collection import (
    GameInCollectionCreate,
    GameInCollectionImportDLC,
    GameInCollectionRead,
    GameInCollectionSetBaseGame,
    GameInCollectionWithPlaythroughsRead,
)
from app.schemas.game_session import GameSessionCreate, GameSessionRead
from app.schemas.playthrough import PlaythroughCreate, PlaythroughRead
from app.services.igdb import igdb_service

logger = logging.getLogger(__name__)

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
    if body.skip_default_playthrough:
        # Import path: return the existing entry instead of 409 so the caller
        # can attach a playthrough without a second round-trip.
        existing = db.execute(
            select(GameInCollection).where(
                GameInCollection.user_id == current_user.id,
                GameInCollection.game_id == body.game_id,
                GameInCollection.platform_id == body.platform_id,
            )
        ).scalar_one_or_none()
        if existing:
            return existing

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
    if not body.skip_default_playthrough:
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


@router.post("/{id}/sessions", response_model=GameSessionRead, status_code=201)
def create_session(
    id: int,
    body: GameSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameSession:
    entry = db.get(GameInCollection, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")

    session = GameSession(
        game_in_collection_id=id,
        completion_time=body.completion_time,
        started_at=body.started_at,
        ended_at=body.ended_at,
        notes=body.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


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


@router.patch("/{id}/base-game", response_model=GameInCollectionRead)
def set_base_game(
    id: int,
    body: GameInCollectionSetBaseGame,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameInCollection:
    entry = db.get(GameInCollection, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")

    if body.base_game_entry_id is not None:
        if body.base_game_entry_id == id:
            raise HTTPException(
                status_code=422,
                detail="A collection entry cannot be its own base game",
            )
        base_entry = db.get(GameInCollection, body.base_game_entry_id)
        if not base_entry or base_entry.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Base game entry not found")

    entry.base_game_entry_id = body.base_game_entry_id
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/{id}/import-dlc", response_model=list[GameInCollectionRead])
async def import_dlc(
    id: int,
    body: GameInCollectionImportDLC,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GameInCollection]:
    base_entry = db.get(GameInCollection, id)
    if not base_entry or base_entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Collection entry not found")

    results: list[GameInCollection] = []

    for igdb_id in body.igdb_ids:
        try:
            data = await igdb_service.fetch_game(igdb_id)
            if data is None:
                logger.warning("DLC igdb_id=%d not found on IGDB, skipping", igdb_id)
                continue

            game = db.execute(
                select(Game).where(Game.igdb_id == igdb_id)
            ).scalar_one_or_none()
            if game is None:
                game = Game(
                    igdb_id=igdb_id,
                    name=data["name"],
                    summary=data.get("summary"),
                    cover_image_id=data.get("cover", {}).get("image_id"),
                    first_release_date=data.get("first_release_date"),
                    rating=data.get("total_rating"),
                )
                db.add(game)
                db.flush()

            dlc_entry = db.execute(
                select(GameInCollection).where(
                    GameInCollection.user_id == current_user.id,
                    GameInCollection.game_id == game.id,
                    GameInCollection.platform_id == base_entry.platform_id,
                )
            ).scalar_one_or_none()

            if dlc_entry is None:
                dlc_entry = GameInCollection(
                    user_id=current_user.id,
                    game_id=game.id,
                    platform_id=base_entry.platform_id,
                    base_game_entry_id=base_entry.id,
                )
                db.add(dlc_entry)
            else:
                dlc_entry.base_game_entry_id = base_entry.id

            results.append(dlc_entry)

        except Exception:
            logger.warning(
                "Failed to import DLC igdb_id=%d, skipping", igdb_id, exc_info=True
            )
            continue

    db.commit()
    for entry in results:
        db.refresh(entry)

    return results
