from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.user_list import UserList
from app.models.user_list_entry import UserListEntry
from app.schemas.user_list import UserListCreate, UserListRead, UserListUpdate
from app.schemas.user_list_entry import UserListEntryRead

router = APIRouter(prefix="/lists", tags=["lists"])


def _get_owned_list(id: int, current_user: User, db: Session) -> UserList:
    user_list = db.get(UserList, id)
    if not user_list or user_list.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="List not found")
    return user_list


@router.get("/", response_model=list[UserListRead])
def list_user_lists(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserList]:
    return (
        db.execute(
            select(UserList)
            .where(UserList.user_id == current_user.id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )


@router.get("/{id}", response_model=UserListRead)
def get_user_list(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserList:
    return _get_owned_list(id, current_user, db)


@router.post("/", response_model=UserListRead, status_code=201)
def create_user_list(
    body: UserListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserList:
    user_list = UserList(user_id=current_user.id, **body.model_dump())
    db.add(user_list)
    db.commit()
    db.refresh(user_list)
    return user_list


@router.put("/{id}", response_model=UserListRead)
def update_user_list(
    id: int,
    body: UserListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserList:
    user_list = _get_owned_list(id, current_user, db)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(user_list, key, value)
    db.commit()
    db.refresh(user_list)
    return user_list


@router.delete("/{id}", status_code=204)
def delete_user_list(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    user_list = _get_owned_list(id, current_user, db)
    db.delete(user_list)
    db.commit()


@router.get("/{id}/entries", response_model=list[UserListEntryRead])
def get_list_entries(
    id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserListEntry]:
    _get_owned_list(id, current_user, db)
    return (
        db.execute(
            select(UserListEntry)
            .where(UserListEntry.list_id == id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )
