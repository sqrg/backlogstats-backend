from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.user_list_entry import UserListEntry
from app.schemas.user_list_entry import (
    UserListEntryCreate,
    UserListEntryRead,
    UserListEntryUpdate,
)

router = APIRouter(prefix="/list-entries", tags=["list-entries"])


@router.get("/", response_model=list[UserListEntryRead])
def list_entries(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[UserListEntry]:
    return db.execute(select(UserListEntry).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=UserListEntryRead)
def get_entry(id: int, db: Session = Depends(get_db)) -> UserListEntry:
    entry = db.get(UserListEntry, id)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    return entry


@router.post("/", response_model=UserListEntryRead, status_code=201)
def create_entry(
    body: UserListEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserListEntry:
    entry = UserListEntry(**body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{id}", response_model=UserListEntryRead)
def update_entry(
    id: int,
    body: UserListEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserListEntry:
    entry = db.get(UserListEntry, id)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{id}", status_code=204)
def delete_entry(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    entry = db.get(UserListEntry, id)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    db.delete(entry)
    db.commit()
