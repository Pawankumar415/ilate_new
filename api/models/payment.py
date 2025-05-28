from sqlalchemy import Boolean, Column, Integer, Float, String, ForeignKey, DateTime, func, TIMESTAMP,Sequence
from sqlalchemy.orm import relationship
from db.base import Base

class Payment(Base):
    __tablename__ = 'payments_tb'

    payment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))
    standard_id = Column(Integer, ForeignKey('standards.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    batch_id = Column(Integer, ForeignKey('batches.id'))
    years = Column(Integer)
    amount = Column(Float)
    discount = Column(Float, nullable=True) 
    final_amount = Column(Float, nullable=True)
    amount_paid = Column(Float, default=0) # added by bhavan kumar
    payment_mode = Column(String(255))
    payment_info = Column(String(255))
    other_info = Column(String(255))
    receipt = Column(String(255), nullable=True)
    # Razorpay Integration Fields
    razorpay_order_id = Column(String(255), unique=True, nullable=True) 
    razorpay_payment_id = Column(String(255), unique=True, nullable=True)  
    currency = Column(String(255), default="INR")
    status = Column(String(50), default="pending")  
    referral_code = Column(String(255), ForeignKey('referral_codes.code'), nullable=True) 
    is_referral_code_used = Column(Boolean, default=False) 
    installment_count = Column(Integer, default=0)
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(TIMESTAMP, server_default=None, onupdate=func.current_timestamp())
    invoice_id = Column(String(255), unique=True, nullable=False) # added by bhavan kumar
    gst = Column(String(255), nullable=True) # added by bhavan kumar


    # Establishing relationships
    course = relationship("Course", back_populates="payments")
    standard = relationship("Standard", back_populates="payments")
    subject = relationship("Subject", back_populates="payments")
    module = relationship("Module", back_populates="payments")
    batch = relationship("Batch", back_populates="payments")
    installments = relationship("Installment", back_populates="payment")
    referral_code_info = relationship("ReferralCode", back_populates="payments")
    user = relationship("LmsUsers", back_populates="payments")
    