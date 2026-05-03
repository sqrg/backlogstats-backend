from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.user_list import UserList
from app.schemas.user_list import PublicUserListRead

router = APIRouter(prefix="/users", tags=["public-lists"])


def _resolve_active_user(username: str, db: Session) -> User:
    user = db.execute(
        select(User).where(User.username == username.lower())
    ).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Not found")
    return user


def _to_public(list_: UserList) -> PublicUserListRead:
    return PublicUserListRead(
        id=list_.id,
        username=list_.user.username or "",
        name=list_.name,
        is_public=list_.is_public,
        entries=list_.entries,
        created_at=list_.created_at,
        updated_at=list_.updated_at,
    )


@router.get("/{username}/lists", response_model=list[PublicUserListRead])
def list_public_lists(
    username: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[PublicUserListRead]:
    user = _resolve_active_user(username, db)
    rows = (
        db.execute(
            select(UserList)
            .where(UserList.user_id == user.id, UserList.is_public.is_(True))
            .order_by(UserList.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [_to_public(r) for r in rows]


@router.get("/{username}/lists/{list_id}", response_model=PublicUserListRead)
def get_public_list(
    username: str,
    list_id: int,
    db: Session = Depends(get_db),
) -> PublicUserListRead:
    user = _resolve_active_user(username, db)
    list_ = db.get(UserList, list_id)
    if not list_ or list_.user_id != user.id or not list_.is_public:
        raise HTTPException(status_code=404, detail="Not found")
    return _to_public(list_)
