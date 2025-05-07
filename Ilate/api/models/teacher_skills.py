from sqlalchemy import Column, String, Integer, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship
from .Teacher import Teacher

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))  
    skill = Column(String(length=50))
    certification = Column(String(length=50))
    license = Column(String(length=50))

    teacher = relationship("Teacher", back_populates="skills")
