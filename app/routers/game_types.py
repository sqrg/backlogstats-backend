import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_type import GameType
from app.models.genre import Genre
from app.models.platform import Platform
from app.models.user import User
from app.schemas.game_type import GameTypeRead
from app.schemas.genre import GenreRead
from app.schemas.platform import PlatformRead
from app.services.igdb import igdb_service

router = APIRouter(tags=["admin"])


@router.get("/game-types", response_model=list[GameTypeRead])
def list_game_types(db: Session = Depends(get_db)) -> list[GameType]:
    return list(db.execute(select(GameType)).scalars().all())


@router.post("/admin/game-types/sync", response_model=list[GameTypeRead])
async def sync_game_types(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[GameType]:
    if not igdb_service._credentials_configured():
        raise HTTPException(
            status_code=503, detail="IGDB credentials are not configured"
        )
    try:
        return await igdb_service.sync_game_types(db)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="IGDB request failed")


@router.post("/admin/genres/sync", response_model=list[GenreRead])
async def sync_genres(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Genre]:
    if not igdb_service._credentials_configured():
        raise HTTPException(
            status_code=503, detail="IGDB credentials are not configured"
        )
    try:
        return await igdb_service.sync_genres(db)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="IGDB request failed")


@router.post("/admin/platforms/sync", response_model=list[PlatformRead])
async def sync_platforms(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Platform]:
    if not igdb_service._credentials_configured():
        raise HTTPException(
            status_code=503, detail="IGDB credentials are not configured"
        )
    try:
        return await igdb_service.sync_platforms(db)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="IGDB request failed")
