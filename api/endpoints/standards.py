from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Standard, Course
from ..schemas import StandardCreate, StandardUpdate
from auth.auth_bearer import JWTBearer,get_admin, get_teacher, get_admin_or_teacher

router = APIRouter()


@router.post("/standards/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_standard(course_id:int,standard: StandardCreate, db: Session = Depends(get_db)):
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        db_standard = Standard(**standard.dict(), course_id=course_id)
        db.add(db_standard)
        db.commit()
        db.refresh(db_standard)
        return db_standard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create standard: {str(e)}")

@router.get("/standards/", response_model=None)
def read_all_standards(db: Session = Depends(get_db)):
    try:
        return db.query(Standard).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="standard not found")

@router.get("/standards/{standard_id}", response_model=None)
def read_standard(standard_id: int, db: Session = Depends(get_db)):
    try:
        db_standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if db_standard is None:
            raise HTTPException(status_code=404, detail="Standard not found")
        return db_standard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch standard: {str(e)}")

@router.put("/standards/{standard_id}", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_standard(standard_id: int, standard_update: StandardUpdate, db: Session = Depends(get_db)):
    try:
        db_standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if not db_standard:
            raise HTTPException(status_code=404, detail="Standard not found")
        if standard_update.name:
            db_standard.name = standard_update.name
        if standard_update.course_id:
            course = db.query(Course).filter(Course.id == standard_update.course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            db_standard.course_id = standard_update.course_id
        db.commit()
        db.refresh(db_standard)
        return db_standard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update standard: {str(e)}")


@router.delete("/standards/{standard_id}", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_standard(standard_id: int, db: Session = Depends(get_db)):
    try:
        db_standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if db_standard is None:
            raise HTTPException(status_code=404, detail="Standard not found")
        db.delete(db_standard)
        db.commit()
        return {"detail :" f"Data has been deleted successfuly"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete standard: {str(e)}")
