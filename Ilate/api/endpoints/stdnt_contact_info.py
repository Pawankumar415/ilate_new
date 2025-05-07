from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import ContactInformation
from ..schemas import StudentContactCreate

router = APIRouter()


@router.post("/contact/", response_model=None)
def create_contact(contact: StudentContactCreate, db: Session = Depends(get_db)):
    try:
        db_contact = ContactInformation(**contact.dict())
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student contact: {str(e)}")


@router.get("/contact/{student_id}", response_model=None)
def read_contact(student_id: int, db: Session = Depends(get_db)):
    try:
        db_contact = (
            db.query(ContactInformation).filter(ContactInformation.StudentID == student_id).first()
        )
        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return db_contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student contact: {str(e)}")


@router.get("/contacts/", response_model=list[None])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return db.query(ContactInformation).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student contact: {str(e)}")


@router.put("/contact/{student_id}", response_model=None)
def update_contact(student_id: int, contact: StudentContactCreate, db: Session = Depends(get_db)):
    try:
        db_contact = (
            db.query(ContactInformation).filter(ContactInformation.StudentID == student_id).first()
        )
        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        update_data = contact.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update student contact: {str(e)}")


@router.delete("/contact/{student_id}", response_model=None)
def delete_contact(student_id: int, db: Session = Depends(get_db)):
    try:
        db_contact = (
            db.query(ContactInformation).filter(ContactInformation.StudentID == student_id).first()
        )
        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        db.delete(db_contact)
        db.commit()
        return db_contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete student contact: {str(e)}")
