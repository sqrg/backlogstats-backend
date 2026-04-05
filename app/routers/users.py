from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.user import User
from app.models.user_list import UserList
from app.schemas.game_in_collection import GameInCollectionRead
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.user_list import UserListRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def list_users(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[User]:
    return db.execute(select(User).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=UserRead)
def get_user(id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{id}", response_model=UserRead)
def update_user(id: int, body: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db)) -> None:
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router.get("/{id}/collection", response_model=list[GameInCollectionRead])
def get_user_collection(
    id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GameInCollection]:
    if current_user.id != id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    if not db.get(User, id):
        raise HTTPException(status_code=404, detail="User not found")
    return (
        db.execute(
            select(GameInCollection)
            .where(GameInCollection.user_id == id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )


@router.get("/{id}/lists", response_model=list[UserListRead])
def get_user_lists(
    id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserList]:
    if current_user.id != id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    if not db.get(User, id):
        raise HTTPException(status_code=404, detail="User not found")
    return (
        db.execute(
            select(UserList).where(UserList.user_id == id).offset(offset).limit(limit)
        )
        .scalars()
        .all()
    )
