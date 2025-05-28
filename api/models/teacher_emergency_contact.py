from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from .Teacher import Teacher


class EmergencyContact(Base):
    __tablename__ = "emergency_contact"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))
    emergency_contact_name = Column(String(length=50))
    relation = Column(String(length=50))
    emergency_contact_number = Column(String(length=50))

    teacher = relationship("Teacher", back_populates="emergency_contact")

    
