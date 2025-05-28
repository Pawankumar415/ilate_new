from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from db.base import Base
from sqlalchemy.orm import relationship


class DiscountQuestion(Base):
    __tablename__ = 'discount_questions2'

    question_id = Column(Integer, primary_key=True)
    standard_id=Column(Integer, ForeignKey("standards.id"))
    subject_id=Column(Integer, ForeignKey("subjects.id"))
    question_text = Column(String(255))
    option1_text = Column(String(255))
    option2_text = Column(String(255))
    option3_text = Column(String(255))
    option4_text = Column(String(255))
    correct_ans_text = Column(String(255))
    difficulty_level = Column(String(255))

    standards = relationship("Standard", back_populates="discount_Questions")
    subject = relationship("Subject", back_populates="discount_Questions")

    