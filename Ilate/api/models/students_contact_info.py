from sqlalchemy import Column, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship, backref

class ContactInformation(Base):
    __tablename__ = 'students_contact_info'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    primary_no = Column(String(255))
    secondary_no = Column(String(255), nullable=True)
    primary_email = Column(String(255))
    secondary_email = Column(String(255), nullable=True)
    current_address = Column(String(255))
    permanent_address = Column(String(255))

    student = relationship("Student", back_populates="contact_info")
