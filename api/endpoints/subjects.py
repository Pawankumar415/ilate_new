from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Subject, Standard
from ..schemas import SubjectCreate, SubjectUpdate
from auth.auth_bearer import JWTBearer, get_user_id_from_token, get_admin

router = APIRouter()


@router.post("/subjects/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_subject(standard_id: int, subject: SubjectCreate, db: Session = Depends(get_db)):
    try:
        standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if not standard:
            raise HTTPException(status_code=404, detail="standard not found")
        
        db_subject = Subject(**subject.dict(), standard_id=standard_id)
        db.add(db_subject)
        db.commit()
        db.refresh(db_subject)
        return db_subject
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subject: {str(e)}")

@router.get("/subjects/", response_model=None)
def read_all_subjects(db: Session = Depends(get_db)):
    try:
        return db.query(Subject).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="subject not found")

@router.get("/subjects/{subject_id}", response_model=None)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    try:
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if db_subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        return db_subject
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subjcet: {str(e)}")

@router.put("/subjects/{subject_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_subject(subject_id: int, subject_update: SubjectUpdate, db: Session = Depends(get_db)):
    try:
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not db_subject:
            raise HTTPException(status_code=404, detail="Standard not found")
        if subject_update.name:
            db_subject.name = subject_update.name
        if subject_update.standard_id:
            standard = db.query(Standard).filter(Standard.id == subject_update.standard_id).first()
            if not standard:
                raise HTTPException(status_code=404, detail="Standard not found")
            db_subject.standard_id = subject_update.standard_id
        db.commit()
        db.refresh(db_subject)
        return db_subject
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update subject: {str(e)}")

@router.delete("/subjects/{subject_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)] )
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    try:
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if db_subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        db.delete(db_subject)
        db.commit()
        return {"message:" f"Data has been deleted successfuly"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete subject: {str(e)}")
