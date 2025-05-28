from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Company
from ..schemas import CompanyCreate, CompanyUpdate
from auth.auth_bearer import JWTBearer, get_admin

router = APIRouter()

@router.get("/companies/", response_model=None)
async def read_companies(db: Session = Depends(get_db)):
    try:
        return db.query(Company).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="company not found")

@router.get("/companies/{company_id}", response_model=None)
async def read_company(company_id: int, db: Session = Depends(get_db)):
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to fetch company")

@router.post("/companies/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def create_company(company_data: CompanyCreate, db: Session = Depends(get_db)):
    try:
        company = Company(**company_data.dict())
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to insert  company")

@router.put("/companies/{company_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_company(company_id: int, company_data: CompanyUpdate, db: Session = Depends(get_db)):
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        for key, value in company_data.dict().items():
            setattr(company, key, value)
        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to update company")

@router.delete("/companies/{company_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        db.delete(company)
        db.commit()
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to delete company")

