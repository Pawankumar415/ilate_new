from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from .Teacher import Teacher


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))
    education_level = Column(String(length=50))
    institution = Column(String(length=50))
    specialization = Column(String(length=50))
    field_of_study = Column(String(length=50))
    year_of_passing = Column(Integer)
    percentage = Column(Float)


    teacher = relationship("Teacher", back_populates="educations")

   

