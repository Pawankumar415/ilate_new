from sqlalchemy import Column, Integer, String, Float, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship


class PreEducation(Base):
    __tablename__ = 'pre_education'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    student_class = Column(String(255))
    school = Column(String(255))
    year_of_passing = Column(Integer)
    percentage = Column(Float)

    student = relationship("Student", back_populates="pre_education")
