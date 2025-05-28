from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship 
from db.base import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    subject_id = Column(Integer, ForeignKey('subjects.id',ondelete="CASCADE"))

    subject = relationship("Subject", back_populates='modules')
    course_details = relationship("CourseDetails", back_populates="module")
    payments = relationship("Payment", back_populates="module")
    courses_content = relationship("Course_content", back_populates="module")

    Fees = relationship("Fee", back_populates="module")
    admin_installments = relationship("AdminInstallment", back_populates="module")
    