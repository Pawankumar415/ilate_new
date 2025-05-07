from sqlalchemy import Column, Integer, ForeignKey,String, Text, DateTime,func,Boolean
from sqlalchemy.orm import relationship
from db.base import Base
#from .Questions import Question1
# from .paper import Paper

class QuestionPaper1(Base):
    __tablename__ = 'question_papers2'

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.lesson_id'))
    lesson_title = Column(String(255))
    course_content_id = Column(Integer)
    is_test_completed = Column(Boolean, server_default='0', nullable=False)
    created_on = Column(DateTime, default=func.now())
    created_by = Column(Integer)

    lesson = relationship("Lesson", back_populates="question_papers")
    #teacher = relationship("Teacher", back_populates="created_question_papers")
    questions = relationship("LessontestQuestion", back_populates="question_paper")
    student_answers = relationship("StudentAnswer", back_populates="question_paper")

    