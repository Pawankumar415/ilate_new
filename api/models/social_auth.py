from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base

class SocialAuth(Base):
    __tablename__ = "social_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    provider = Column(String(100), nullable=False) 
    provider_user_id = Column(String(255), nullable=False)  
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("LmsUsers", back_populates="social_logins")