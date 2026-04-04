from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreRead, GenreUpdate

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=list[GenreRead])
def list_genres(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Genre]:
    return db.execute(select(Genre).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=GenreRead)
def get_genre(id: int, db: Session = Depends(get_db)) -> Genre:
    genre = db.get(Genre, id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("/", response_model=GenreRead, status_code=201)
def create_genre(body: GenreCreate, db: Session = Depends(get_db)) -> Genre:
    genre = Genre(**body.model_dump())
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@router.put("/{id}", response_model=GenreRead)
def update_genre(id: int, body: GenreUpdate, db: Session = Depends(get_db)) -> Genre:
    genre = db.get(Genre, id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(genre, key, value)
    db.commit()
    db.refresh(genre)
    return genre


@router.delete("/{id}", status_code=204)
def delete_genre(id: int, db: Session = Depends(get_db)) -> None:
    genre = db.get(Genre, id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    db.delete(genre)
    db.commit()
