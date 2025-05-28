from sqlalchemy import Column, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Parent(Base):
    __tablename__ = 'parent_information'

    parent_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    p_first_name = Column(String(255))
    p_middle_name = Column(String(255))
    p_last_name = Column(String(255))
    user_type = Column(String(100))
    guardian = Column(String(255))
    primary_no = Column(String(255))
    secondary_no = Column(String(255))
    primary_email = Column(String(255))
    secondary_email = Column(String(255))

    student = relationship("Student", back_populates="parent_info")

    user = relationship("LmsUsers", back_populates="parent_info")



