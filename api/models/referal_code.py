from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime,Boolean
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(255), unique=True, nullable=False)  
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(255), nullable=False, server_default="active")
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    discount_rupees = Column(Integer, default=0)
    
    creator = relationship("LmsUsers", back_populates="created_referral_codes")
    payments = relationship("Payment", back_populates="referral_code_info")
    installments = relationship("Installment", back_populates="referral_code_info") # Added by bhavan kumar