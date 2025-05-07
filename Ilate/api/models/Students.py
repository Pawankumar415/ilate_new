from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import relationship
from db.base import Base
from .user import LmsUsers
import os
import shutil
import uuid

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    first_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(String(255))
    nationality = Column(String(255))
    referral = Column(String(255))
    id_proof = Column(String(255))
    Address_proof = Column(String(255)) 
    profile_photo=Column(String(255)) 
    date_of_joining = Column(Date)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    date_of_completion = Column(Date, nullable=True)
    

    pre_education = relationship("PreEducation", uselist=False,  back_populates="student")
    parent_info = relationship("Parent", uselist=False, back_populates="student")
    user = relationship("LmsUsers", back_populates="student")
    contact_info = relationship("ContactInformation",uselist=False, back_populates="student")
    course_details = relationship("CourseDetails",uselist=False, back_populates="student")

    branch = relationship("Branch", back_populates="student")


def save_upload(upload_file: UploadFile) -> str:
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("uploads", unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")