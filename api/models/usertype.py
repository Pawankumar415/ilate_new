from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class UserType(Base):
    __tablename__ = "usertypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    designation_id = Column(Integer, ForeignKey("designations.id"))
    role = relationship("Designation", back_populates="users")
