# # installment.py
# from sqlalchemy import TIMESTAMP, Column, DateTime, Integer, Float, Date, ForeignKey, Enum, CheckConstraint, func,JSON, String
# from sqlalchemy.orm import relationship
# from db.base import Base

# class Installment(Base):
#     __tablename__ = "installments_tb"

#     installment_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  
#     payment_id = Column(Integer, ForeignKey("payments_tb.payment_id"), nullable=False)  
#     installment_number = Column(Integer, nullable=False)
#     installment_plan = Column(JSON, nullable=False) 
#     due_date = Column(Date, nullable=False)  
#     total_amount = Column(Float, nullable=False) 
#     amount_due = Column(Float, nullable=False)  
#     paid_amount = Column(Float, default=0.0, nullable=False)  
#     status = Column(String(255)) 
#     created_on = Column(DateTime, default=func.now())
#     updated_on = Column(TIMESTAMP, server_default=None, onupdate=func.current_timestamp())


#     payment = relationship("Payment", back_populates="installments")
#     user = relationship("LmsUsers", back_populates="installments")




############################################################

# updated by bhavan kumar



from sqlalchemy import TIMESTAMP, Column, DateTime, Integer, Float, Date, ForeignKey, func, JSON, String
from sqlalchemy.orm import relationship
from db.base import Base

class Installment(Base):
    __tablename__ = "installments_tb"

    installment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments_tb.payment_id"), nullable=False)
    admin_installment_id = Column(Integer, ForeignKey("admin_installments_tb.id"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(255))
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(TIMESTAMP, server_default=None, onupdate=func.current_timestamp())

    # Fields for referral code and discount
    referral_code_used = Column(Integer, ForeignKey("referral_codes.id"), nullable=True)
    discount_rupees = Column(Float, default=0.0, nullable=False)

    payment = relationship("Payment", back_populates="installments")
    user = relationship("LmsUsers", back_populates="installments")
    referral_code_info = relationship("ReferralCode", back_populates="installments")
    admin_installment = relationship("AdminInstallment", back_populates="installments") 





    