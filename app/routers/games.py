import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.game import Game
from app.models.game_series import GameSeries
from app.models.platform import Platform
from app.models.series import Series
from app.schemas.game import GameCreate, GameRead, GameUpdate
from app.schemas.igdb import GameFromIGDB, IGDBGameResult
from app.services.igdb import igdb_service

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=list[GameRead])
def list_games(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Game]:
    return db.execute(select(Game).offset(offset).limit(limit)).scalars().all()


# NOTE: /search must be registered before /{id} so FastAPI does not treat the
# literal string "search" as the value of the {id} path parameter.
@router.get("/search", response_model=list[IGDBGameResult])
async def search_games(
    q: str, limit: int = 10, db: Session = Depends(get_db)
) -> list[IGDBGameResult]:
    if not igdb_service._credentials_configured():
        raise HTTPException(
            status_code=503, detail="IGDB credentials are not configured"
        )
    limit = min(limit, 20)
    try:
        results = await igdb_service.search_games(q, limit)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=429, detail="IGDB rate limit exceeded; please retry shortly"
            )
        raise HTTPException(status_code=502, detail="IGDB request failed")

    # Collect all unique platforms across results and upsert into our DB so
    # the frontend can reference them by internal ID without a separate fetch.
    all_igdb_platforms: dict[int, str] = {}  # igdb_id -> name
    for r in results:
        for p in r.get("platforms", []):
            all_igdb_platforms[p["id"]] = p["name"]

    platform_db_ids: dict[int, int] = {}  # igdb_id -> internal db id
    for igdb_id, name in all_igdb_platforms.items():
        existing = db.execute(
            select(Platform).where(Platform.name == name)
        ).scalar_one_or_none()
        if existing:
            platform_db_ids[igdb_id] = existing.id
        else:
            platform = Platform(name=name)
            db.add(platform)
            db.flush()
            platform_db_ids[igdb_id] = platform.id
    db.commit()

    return [IGDBGameResult.from_igdb(r, platform_db_ids) for r in results]


@router.post("/from-igdb", response_model=GameRead, status_code=201)
async def import_game_from_igdb(
    body: GameFromIGDB, db: Session = Depends(get_db)
) -> Game:
    if not igdb_service._credentials_configured():
        raise HTTPException(
            status_code=503, detail="IGDB credentials are not configured"
        )

    # Idempotent: return existing game if already imported.
    existing = db.execute(
        select(Game).where(Game.igdb_id == body.igdb_id)
    ).scalar_one_or_none()
    if existing:
        return existing

    try:
        data = await igdb_service.fetch_game(body.igdb_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=429, detail="IGDB rate limit exceeded; please retry shortly"
            )
        raise HTTPException(status_code=502, detail="IGDB request failed")

    if data is None:
        raise HTTPException(status_code=404, detail="Game not found on IGDB")

    cover_data = data.get("cover")
    game = Game(
        igdb_id=data["id"],
        name=data["name"],
        summary=data.get("summary"),
        cover_image_id=cover_data["image_id"] if cover_data else None,
        first_release_date=data.get("first_release_date"),
        rating=data.get("total_rating"),
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    collections = data.get("collections", [])
    if collections:
        for c in collections:
            s = db.execute(
                select(Series).where(Series.igdb_id == c["id"])
            ).scalar_one_or_none()
            if not s:
                s = Series(igdb_id=c["id"], name=c["name"], slug=c.get("slug"))
                db.add(s)
                db.flush()
            existing_link = db.execute(
                select(GameSeries).where(
                    GameSeries.game_id == game.id,
                    GameSeries.series_id == s.id,
                )
            ).scalar_one_or_none()
            if not existing_link:
                db.add(GameSeries(game_id=game.id, series_id=s.id))
        db.commit()

    return game


@router.get("/{id}", response_model=GameRead)
def get_game(id: int, db: Session = Depends(get_db)) -> Game:
    game = db.get(Game, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/", response_model=GameRead, status_code=201)
def create_game(body: GameCreate, db: Session = Depends(get_db)) -> Game:
    game = Game(**body.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.put("/{id}", response_model=GameRead)
def update_game(id: int, body: GameUpdate, db: Session = Depends(get_db)) -> Game:
    game = db.get(Game, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(game, key, value)
    db.commit()
    db.refresh(game)
    return game


@router.delete("/{id}", status_code=204)
def delete_game(id: int, db: Session = Depends(get_db)) -> None:
    game = db.get(Game, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    db.delete(game)
    db.commit()
