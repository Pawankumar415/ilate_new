from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.base import Base
from .Students import Student 
from .subject import Subject
from .standard import Standard
from .module import Module
from .course import Course

class CourseDetails(Base):
    __tablename__ = "course_details"

    id = Column(Integer, primary_key=True, index=True)
    courses = Column(Integer, ForeignKey("courses.id", ondelete='CASCADE')) 
    subjects = Column(Integer, ForeignKey("subjects.id"))
    standards = Column(Integer, ForeignKey("standards.id"))
    modules = Column(Integer, ForeignKey("modules.id"))
    students = Column(Integer, ForeignKey("students.id"))
    user_id = Column(Integer)
    course_content_id = Column(Integer, ForeignKey("courses_content.id"))
    is_active_course = Column(Boolean, server_default='0', nullable=False)


    student = relationship("Student", back_populates="course_details")
    subject = relationship("Subject", back_populates="course_details")
    standard = relationship("Standard", back_populates="course_details")
    module = relationship("Module", back_populates="course_details")
    course = relationship("Course", back_populates="course_details")
    lessons = relationship("Lesson", back_populates="course_detail")
    course_contents = relationship("Course_content", back_populates="course_details")



