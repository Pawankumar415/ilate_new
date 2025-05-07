from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException
from db.base import Base
from .Teacher import Teacher


class TeacherContact(Base):
    __tablename__ = "teacher_contact_info"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id")) 
    primary_number = Column(String(length=50))
    secondary_number = Column(String(length=50), nullable=True)
    primary_email_id = Column(String(length=50))
    secondary_email_id = Column(String(length=50), nullable=True)
    current_address = Column(String(length=255))
    permanent_address = Column(String(length=255))

    teacher = relationship("Teacher", back_populates="contact_information")