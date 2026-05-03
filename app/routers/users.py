from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.validation import validate_and_normalize_username
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.game_in_collection import GameInCollection
from app.models.user import User
from app.models.user_list import UserList
from app.schemas.game_in_collection import GameInCollectionRead
from app.schemas.user import PasswordChangeRequest, UserMeUpdate, UserRead
from app.schemas.user_list import UserListRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    body: UserMeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if body.username is not None:
        normalized = validate_and_normalize_username(body.username)
        conflict = db.execute(
            select(User).where(User.username == normalized, User.id != current_user.id)
        ).scalar_one_or_none()
        if conflict:
            raise HTTPException(status_code=409, detail="Username already taken")
        current_user.username = normalized
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/password", status_code=204)
def change_password(
    body: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail="This account has no password set (OAuth-only). Use your provider to sign in.",
        )
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(body.new_password)
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
