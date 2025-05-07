from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from db.base import Base
from .Teacher import Teacher

class Dependents(Base):
    __tablename__ = "dependents"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))  
    dependent_name = Column(String(length=50))
    realtion = Column(String(length=50))
    date_of_birth = Column(Date)

    teacher = relationship("Teacher", back_populates="dependents")
