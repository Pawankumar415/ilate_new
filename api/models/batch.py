from sqlalchemy import Column, Integer, String,ForeignKey
from db.base import Base
from sqlalchemy.orm import Session, relationship


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    size= Column(String(223), nullable=False, unique=True)

    payments = relationship("Payment", back_populates="batch")

    Fees = relationship("Fee", back_populates="batch")
    admin_installments = relationship("AdminInstallment", back_populates="batch")
