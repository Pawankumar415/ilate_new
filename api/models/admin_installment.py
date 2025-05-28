from sqlalchemy import TIMESTAMP, Column, DateTime, Integer, Float, Date, ForeignKey, func, JSON, String,Numeric
from sqlalchemy.orm import relationship
from db.base import Base

class AdminInstallment(Base):
    __tablename__ = "admin_installments_tb"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete='CASCADE'), nullable=False)
    number_of_installments = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    installment_1_amount = Column(Numeric(10, 2), nullable=True)
    installment_1_due_date = Column(Date, nullable=True)
    installment_2_amount = Column(Numeric(10, 2), nullable=True)
    installment_2_due_date = Column(Date, nullable=True)
    installment_3_amount = Column(Numeric(10, 2), nullable=True)
    installment_3_due_date = Column(Date, nullable=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=True)
    year = Column(Integer, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)


    course = relationship("Course", back_populates="admin_installments")
    standard = relationship("Standard", back_populates="admin_installments")
    subject = relationship("Subject", back_populates="admin_installments")
    module = relationship("Module", back_populates="admin_installments")
    batch = relationship("Batch", back_populates="admin_installments")
    installments = relationship("Installment", back_populates="admin_installment")