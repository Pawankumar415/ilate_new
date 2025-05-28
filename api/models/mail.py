from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db.base import Base

class Mail(Base):
    __tablename__ = 'mails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255))
    message = Column(String(1024))
    name = Column(String(255))
    phone = Column(String(20))
    subject = Column(String(255))
    created_on = Column(DateTime, default=func.now())

    
   