from sqlalchemy import Column, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete='CASCADE'))

    subject = relationship("Subject", back_populates="standards")
    videos = relationship('Video', back_populates='standard')
    course = relationship("Course", back_populates="standards")
    course_details = relationship("CourseDetails", back_populates="standard")
    payments = relationship("Payment", back_populates="standard")
    courses_content = relationship("Course_content", back_populates="standard")
    discount_Questions = relationship("DiscountQuestion", back_populates="standards")

    Fees = relationship("Fee", back_populates="standard")
    admin_installments = relationship("AdminInstallment", back_populates="standard")
   