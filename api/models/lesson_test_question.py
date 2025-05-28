from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import relationship
from db.base import Base
from typing import List, Optional
from fastapi import Form
import shutil
import uuid
import os

class LessontestQuestion(Base):
    __tablename__ = 'lesson_test_Questions2'
    
    id = Column(Integer, primary_key=True, index=True)
    question_paper_id = Column(Integer, ForeignKey('question_papers2.id'))
    question_text = Column(String(255))
    question_images = Column(String(255), nullable=True)
    option1_text = Column(String(255))
    option1_images = Column(String(255), nullable=True)
    option2_text = Column(String(255))
    option2_images = Column(String(255), nullable=True)
    option3_text = Column(String(255))
    option3_images = Column(String(255), nullable=True)
    option4_text = Column(String(255))
    option4_images = Column(String(255), nullable=True)
    correct_ans_text = Column(String(255))
    correct_ans_images = Column(String(255), nullable=True)
    difficulty_level = Column(String(255))
    per_question_marks = Column(Integer)
    
    question_paper = relationship("QuestionPaper1", back_populates="questions")
    

def save_upload(upload_file: UploadFile) -> str:
    unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
    file_path = os.path.join("uploads", unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path