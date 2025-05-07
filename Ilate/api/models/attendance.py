from sqlalchemy import Column, Integer, String, JSON, DateTime, func,Date, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship


class Attendance(Base):
    __tablename__ = "attendances4"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(JSON)
    course_content_id=Column(Integer, ForeignKey("courses_content.id"))
    date = Column(DateTime, default=func.now())
    status = Column(JSON) 


    course_content = relationship("Course_content", back_populates="attendances")
    


    