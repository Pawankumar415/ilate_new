# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from db.base import Base

class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(100))
    phone = Column(String(50))
    message = Column(Text)
    created_on = Column(DateTime, default=func.now())
