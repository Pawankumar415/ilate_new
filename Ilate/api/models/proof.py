from sqlalchemy import Column, Integer, String
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.base import Base
import shutil
import uuid
import os


class Image(Base):
    __tablename__ = "proof"
    
    user_id = Column(Integer, primary_key=True, index=True)
    id_prof = Column(String(255))
    Address_prof = Column(String(255))
   
def save_image_to_db(db: Session, user_id: int, id_prof: str = None, Address_prof: str = None):
    db_image = Image(user_id=user_id, id_prof=id_prof, Address_prof=Address_prof)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_image_by_user_id(user_id: int, db: Session):
    db_image = db.query(Image).filter(Image.user_id == user_id).first()
    return db_image

def update_image_in_db(db: Session, user_id: int, id_prof: UploadFile = File(None), Address_prof: UploadFile = File(None)):
    db_image = db.query(Image).filter(Image.user_id == user_id).first()
    if db_image:
        if id_prof:
            unique_id_prof_filename = str(uuid.uuid4()) + "_" + id_prof.filename
            id_prof_file_path = os.path.join("uploads", unique_id_prof_filename)
            try:
                with open(id_prof_file_path, "wb") as buffer:
                    shutil.copyfileobj(id_prof.file, buffer)
                db_image.id_prof = unique_id_prof_filename
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        if Address_prof:
            unique_address_prof_filename = str(uuid.uuid4()) + "_" + Address_prof.filename
            Address_prof_file_path = os.path.join("uploads", unique_address_prof_filename)
            try:
                with open(Address_prof_file_path, "wb") as buffer:
                    shutil.copyfileobj(Address_prof.file, buffer)
                db_image.Address_prof = unique_address_prof_filename
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        db.commit()
        db.refresh(db_image)
        return db_image
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@staticmethod
def delete_image_from_db(db: Session, user_id: int):
    db_image = db.query(Image).filter(Image.user_id == user_id).first()
    if db_image:
        db.delete(db_image)
        db.commit()
        return {"message": "Image deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Image not found")
