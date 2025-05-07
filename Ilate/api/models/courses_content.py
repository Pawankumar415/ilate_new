from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class Course_content(Base):
    __tablename__ = "courses_content"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete='CASCADE'))
    subject_id = Column(Integer, ForeignKey("subjects.id",ondelete="CASCADE"))
    standard_id = Column(Integer, ForeignKey("standards.id",ondelete="CASCADE"))
    module_id = Column(Integer, ForeignKey("modules.id",ondelete="CASCADE"))
    is_active = Column(Boolean, server_default='1', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="course_contents")  
    subject = relationship("Subject", back_populates="course_contents")
    standard = relationship("Standard", back_populates="courses_content")
    module = relationship("Module", back_populates="courses_content")
    course_details = relationship("CourseDetails", back_populates="course_contents")
    lessons = relationship("Lesson", back_populates="course_contents")
    content = relationship('Content', back_populates='course_contents')
    teacher_by = relationship("TeacherCourse", back_populates="course_Assign")
    attendances = relationship("Attendance", back_populates="course_content")