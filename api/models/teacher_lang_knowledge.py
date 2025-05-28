from sqlalchemy import Column, String, Integer, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship
from .Teacher import Teacher


class LanguagesSpoken(Base):
    __tablename__ = "languages_spoken"

    id = Column(Integer, primary_key=True, index=True)
    Teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))
    languages = Column(String(length=50))

    teacher = relationship("Teacher", back_populates="languages_spoken")
    