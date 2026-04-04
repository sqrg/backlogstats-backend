from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.game import Game
from app.schemas.game import GameCreate, GameRead, GameUpdate

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=list[GameRead])
def list_games(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Game]:
    return db.execute(select(Game).offset(offset).limit(limit)).scalars().all()


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
