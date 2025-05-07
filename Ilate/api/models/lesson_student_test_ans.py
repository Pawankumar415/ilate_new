from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float,func
from sqlalchemy.orm import relationship
from db.base import Base

class StudentAnswer(Base):
    __tablename__ = 'student_answers4'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    question_paper_id = Column(Integer, ForeignKey('question_papers2.id'))
    total_questions = Column(Integer, default=0)
    given_ans_text = Column(String(255),  nullable=True)
    given_ans_image = Column(String(255),  nullable=True)
    is_correct = Column(Boolean, default=False) 
    correct_answer= Column(Integer, default=0)
    wrong_answer= Column(Integer, default=0)
    score = Column(Float)
    is_test_completed = Column(Boolean, server_default='0', nullable=False)
    passed = Column(Boolean, default=False)
    created_on = Column(DateTime, default=func.now())
    
    
    users = relationship("LmsUsers", back_populates="answers")
    question_paper = relationship("QuestionPaper1", back_populates="student_answers")
    