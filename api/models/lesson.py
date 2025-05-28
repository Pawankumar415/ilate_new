from sqlalchemy import Column, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship
from .module import Module

class Lesson(Base):
    __tablename__ = 'lessons'

    lesson_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(String(255))
    course_detail_id = Column(Integer, ForeignKey('course_details.id')) 
    course_content_id = Column(Integer, ForeignKey("courses_content.id")) 

    question_papers = relationship('QuestionPaper', back_populates='lesson')
    content = relationship('Content', back_populates='lesson')
    course_detail = relationship('CourseDetails', back_populates='lessons')
    course_contents = relationship("Course_content", back_populates="lessons")
    question_papers = relationship('QuestionPaper1', back_populates='lesson')





