from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from db.base import Base

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    announcement_text = Column(String(255), nullable=True)
    announcement_images = Column(String(255), nullable=True)
    created_on = Column(DateTime, default=func.now())
