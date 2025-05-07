from sqlalchemy import select, Column, Integer, String,ForeignKey, Float
from db.base import Base
from sqlalchemy.orm import Session, relationship

class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    course_id=Column(ForeignKey('courses.id', ondelete='CASCADE'))
    standard_id=Column(ForeignKey('standards.id'))
    year=Column(Integer) 
    subject_id=Column(ForeignKey('subjects.id'))
    module_id=Column(ForeignKey('modules.id',ondelete="CASCADE"))
    batch_id=Column(ForeignKey('batches.id'))
    amount=Column(Float) 

    # Relationships
    course = relationship("Course", back_populates="Fees")  
    subject = relationship("Subject", back_populates="Fees")
    standard = relationship("Standard", back_populates="Fees")
    module = relationship("Module", back_populates="Fees")
    batch = relationship("Batch", back_populates="Fees")


    
    
    
    
  


    
    

   