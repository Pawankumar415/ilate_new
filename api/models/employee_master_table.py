from sqlalchemy import Column, String, Integer, Date, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship
from .Teacher import Teacher

class Employee(Base):
    __tablename__ = "employee"
    employee_id = Column(Integer, primary_key=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))
    f_name = Column(String(length=20), index=True)
    m_name = Column(String(length=20), index=True)
    l_name = Column(String(length=20), index=True)
    dob = Column(Date)
    gender = Column(String(length=10))
    nationality = Column(String(length=20))
    marital_status = Column(String(length=20))
    citizenship_status = Column(String(length=20))
    date_of_hire = Column(Date, nullable=True)
    date_of_termination = Column(Date, nullable=True)

    teacher = relationship('Teacher', back_populates='employee')
    
   




 