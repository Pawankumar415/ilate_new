from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from db.base import Base
from sqlalchemy.orm import relationship


class DemoFormFill(Base):
    __tablename__ = "demoformfill"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    name = Column(String(255), index=True)
    email_id = Column(String(255))
    contact_no = Column(String(255))
    standard = Column(String(255))
    course = Column(String(255))
    subject = Column(String(255))
    school = Column(String(255))
    teaching_mode = Column(String(255))
    other_info = Column(String(255))
    created_on = Column(DateTime, default=func.now())

    demo = relationship("LmsUsers", back_populates="demos", uselist=False, primaryjoin="DemoFormFill.user_id==LmsUsers.user_id")


