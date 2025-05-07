from sqlalchemy import Column, String, Integer, ForeignKey, Date,JSON, Boolean
from sqlalchemy.orm import relationship
from db.base import Base

class TeacherCourse(Base):
    __tablename__ = "teacher_courses4"

    id = Column(Integer, primary_key=True, index=True )
    teacher_id = Column(Integer, ForeignKey("teachers.Teacher_id"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete='CASCADE'))
    course_content_id = Column(Integer, ForeignKey("courses_content.id"))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    is_assign_course = Column(Boolean, server_default='0', nullable=False)
    

    teacher_Assign = relationship("Teacher", back_populates="courses_by")
    course_Assign = relationship("Course_content", back_populates="teacher_by")
    user = relationship("LmsUsers", back_populates="teacher_courses")
    course = relationship("Course", back_populates="teacher_courses")

 

    
   
    
   