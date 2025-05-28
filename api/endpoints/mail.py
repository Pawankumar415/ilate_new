from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models.mail import Mail
from pydantic import BaseModel, Field
from ..schemas import  MailCreate
from datetime import datetime
import pytz
import re


router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        #mail
# ------------------------------------------------------------------------------------------------------------------

EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def is_valid_email(email: str) -> bool:
    return re.match(EMAIL_REGEX_PATTERN, email) is not None

@staticmethod
def validate_phone_number(phone):
        phone_pattern = r"^\d{10}$"
        return re.match(phone_pattern, phone)

@router.post("/mail/", response_model=None)
def create_mail(mail: MailCreate, db: Session = Depends(get_db)):
    try:
        if not is_valid_email(mail.email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid email address",
            )
        if not validate_phone_number(mail.phone):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid phone number",
            )
        db_mail = Mail(**mail.dict())
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_mail.created_on = ist_now
        db.add(db_mail)
        db.commit()
        db.refresh(db_mail)
        return db_mail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert mail: {str(e)}")

@router.get("/mail/", response_model=None)
def read_all_mails(db: Session = Depends(get_db)):
    try:
        return db.query(Mail).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="mail not found")

@router.get("/mail/{mail_id}", response_model=None)
def read_mail(mail_id: int, db: Session = Depends(get_db)):
    try:
        db_mail = db.query(Mail).filter(Mail.id == mail_id).first()
        if db_mail is None:
            raise HTTPException(status_code=404, detail="Mail not found")
        return db_mail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lesson: {str(e)}")

@router.put("/mail/{mail_id}", response_model=None)
def update_mail(mail_id: int, mail: MailCreate, db: Session = Depends(get_db)):
    try:
        db_mail = db.query(Mail).filter(Mail.id == mail_id).first()
        if db_mail is None:
            raise HTTPException(status_code=404, detail="Mail not found")
        for key, value in mail.dict().items():
            setattr(db_mail, key, value)
        db.commit()
        db.refresh(db_mail)
        return db_mail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update mail: {str(e)}")

@router.delete("/mail/{mail_id}", response_model=None)
def delete_mail(mail_id: int, db: Session = Depends(get_db)):
    try:
        db_mail = db.query(Mail).filter(Mail.id == mail_id).first()
        if db_mail is None:
            raise HTTPException(status_code=404, detail="Mail not found")
        db.delete(db_mail)
        db.commit()
        return {"message": "mail deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete mail: {str(e)}")