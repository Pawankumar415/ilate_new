from sqlalchemy import Column, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    user = relationship("LmsUsers", back_populates="branch")
    student = relationship("Student", back_populates="branch")
    teacher = relationship("Teacher", back_populates="branch")
    