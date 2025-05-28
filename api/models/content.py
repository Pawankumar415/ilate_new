from sqlalchemy import Column, Integer, String,ForeignKey, JSON, Boolean,DateTime,func
from sqlalchemy.orm import relationship
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from db.base import Base
import shutil
import os
from pathlib import Path
import uuid

class Content(Base):
    __tablename__ = "contents1"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id')) 
    course_content_id = Column(Integer, ForeignKey("courses_content.id")) 
    content_description = Column(String(255)) 
    content_path = Column(JSON) 
    created_on = Column(DateTime, default=func.now())

    lesson = relationship('Lesson', back_populates='content')

    course_contents = relationship("Course_content", back_populates="content")
    
def save_upload(upload_file: UploadFile) -> str:
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("uploads", unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")