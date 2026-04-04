from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyRead])
def list_companies(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
) -> list[Company]:
    return db.execute(select(Company).offset(offset).limit(limit)).scalars().all()


@router.get("/{id}", response_model=CompanyRead)
def get_company(id: int, db: Session = Depends(get_db)) -> Company:
    company = db.get(Company, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyRead, status_code=201)
def create_company(body: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    company = Company(**body.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.put("/{id}", response_model=CompanyRead)
def update_company(
    id: int, body: CompanyUpdate, db: Session = Depends(get_db)
) -> Company:
    company = db.get(Company, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{id}", status_code=204)
def delete_company(id: int, db: Session = Depends(get_db)) -> None:
    company = db.get(Company, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
