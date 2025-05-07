from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from db.base import Base
from sqlalchemy.orm import relationship


class DiscountAssessmentResut(Base):
    __tablename__ = "Discount_Ass_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    is_correct = Column(Boolean, default=False) 
    wrong_answer= Column(Integer, default=0)
    duration=Column(Integer, default=0)
    score = Column(Float)
    passed = Column(Boolean, default=False)
    discount_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("LmsUsers", back_populates="Discount_Ass_result")
    
