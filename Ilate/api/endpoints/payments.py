from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models.payment import Payment
from ..models import Student, Course, LmsUsers, Batch,Module,Standard,Subject
from pydantic import BaseModel
from ..schemas import PaymentCreate,PaymentResponse
from auth.auth_bearer import JWTBearer, get_current_user,get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student
from typing import List
from sqlalchemy import desc
from datetime import datetime
from typing import Optional
import pytz
from sqlalchemy import desc, func
from ..models.course_detail import CourseDetails 

router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        #Payments
# ------------------------------------------------------------------------------------------------------------------

@router.post("/payments/insert/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
def create_payment(
    payment: PaymentCreate, 
    db: Session = Depends(get_db), 
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        if not current_user.is_formsubmited:
            raise HTTPException(status_code=400, detail="Admission form not submitted")

        existing_payment = db.query(Payment).filter(Payment.user_id == current_user.user_id).first()
        
        existing_course = db.query(Course).filter(Course.id == payment.course_id).first()
        existing_standard = db.query(Standard).filter(Standard.id == payment.standard_id).first()
        existing_subject = db.query(Subject).filter(Subject.id == payment.subject_id).first()
        existing_module = db.query(Module).filter(Module.id == payment.module_id).first()
        existing_batch = db.query(Batch).filter(Batch.id == payment.batch_id).first()  

        if not all([existing_course, existing_standard, existing_subject, existing_module, existing_batch]):
                raise HTTPException(status_code=404, detail="One or more of course, standard, subject, module, or batch not found")
        
        db_payment = Payment(
                user_id=current_user.user_id,
                course_id=payment.course_id,
                standard_id=payment.standard_id,
                subject_id=payment.subject_id,
                module_id=payment.module_id,
                batch_id=payment.batch_id,
                years=payment.years,
                amount=payment.amount,
                payment_mode=payment.payment_mode,
                payment_info=payment.payment_info,
                other_info=payment.other_info
            )
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_payment.created_on = ist_now
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
            
        return db_payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert payment: {str(e)}")

@router.get("/payments/history/{user_id}", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_payment_history(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payment_history = db.query(Payment).filter(Payment.user_id == user_id).all()

        payment_history_details = []

        total_amount = 0

        for payment in payment_history:
            course = db.query(Course).filter(Course.id == payment.course_id).first()
            if course:
                payment_history_details.append({
                    "payment_id": payment.payment_id,
                    "course_name": course.name,
                    "amount": payment.amount,
                    "created_on": payment.created_on
                })
                total_amount += payment.amount

        num_payments = len(payment_history_details)

        response = {
            "user_id": user.user_id,
            "total_payments": num_payments,
            "total_amount": total_amount,
            "payment_history": payment_history_details,
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment history: {str(e)}")


@router.get("/payments/FetchAll", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def read_all_payments(db: Session = Depends(get_db)):
    try:
    
        subquery = (
            db.query(
                Payment.user_id,
                func.max(Payment.created_on).label("latest_payment_date")
            )
            .group_by(Payment.user_id)
            .subquery()
        )

        payments = (
            db.query(Payment)
            .join(subquery, (Payment.user_id == subquery.c.user_id) & (Payment.created_on == subquery.c.latest_payment_date))
            .order_by(desc(Payment.created_on))
            .all()
        )
        
        if not payments:
            return {"message": "No payments found"}

        payment_history_details = []
        for payment in payments:
            course = db.query(Course).filter(Course.id == payment.course_id).first()
            standard = db.query(Standard).filter(Standard.id == payment.standard_id).first()
            subject = db.query(Subject).filter(Subject.id == payment.subject_id).first()
            module = db.query(Module).filter(Module.id == payment.module_id).first()
            batch = db.query(Batch).filter(Batch.id == payment.batch_id).first()

            course_name = course.name if course else None
            standard_name = standard.name if standard else None
            subject_name = subject.name if subject else None
            module_name = module.name if module else None
            batch_name = batch.size if batch else None

            user = db.query(LmsUsers).filter(LmsUsers.user_id == payment.user_id).first()

            payment_data = {
                "payment_id": payment.payment_id,
                "user_id": payment.user_id,
                "user_name": user.user_name if user else None,
                "course_name": course_name,
                "standard_name": standard_name,
                "subject_name": subject_name,
                "module_name": module_name,
                "batch_name": batch_name,
                "years": payment.years,
                "amount": payment.amount,
                "payment_mode": payment.payment_mode,
                "payment_info": payment.payment_info,
                "other_info": payment.other_info,
                "created_on": payment.created_on,
                "updated_on": payment.updated_on,
            }
            payment_history_details.append(payment_data)
        
        return payment_history_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment all details: {str(e)}")


@router.get("/payments/Fetch/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def read_payment(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        latest_payment = db.query(Payment).filter(Payment.user_id == user_id).order_by(desc(Payment.created_on)).first()

        if not latest_payment:
            raise HTTPException(status_code=404, detail="No payments found for this user")

        course = db.query(Course).filter(Course.id == latest_payment.course_id).first()
        standard = db.query(Standard).filter(Standard.id == latest_payment.standard_id).first()
        subject = db.query(Subject).filter(Subject.id == latest_payment.subject_id).first()
        module = db.query(Module).filter(Module.id == latest_payment.module_id).first()
        batch = db.query(Batch).filter(Batch.id == latest_payment.batch_id).first()

        course_name = course.name if course else None
        standard_name = standard.name if standard else None
        subject_name = subject.name if subject else None
        module_name = module.name if module else None
        batch_name = batch.size if batch else None

        response_data = {
            "payment_id": latest_payment.payment_id,
            "user_id": latest_payment.user_id,
            "course_name": course_name,
            "standard_name": standard_name,
            "subject_name": subject_name,
            "module_name": module_name,
            "batch_name": batch_name,
            "years": latest_payment.years,
            "amount": latest_payment.amount,
            "payment_mode": latest_payment.payment_mode,
            "payment_info": latest_payment.payment_info,
            "other_info": latest_payment.other_info,
            "created_on": latest_payment.created_on,
            "updated_on": latest_payment.updated_on,
        }

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment details: {str(e)}")

@router.put("/payments/verify/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def verify_payments_and_update_details(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payment_info = db.query(Payment).filter(Payment.user_id == user_id).all()

        response = {
            "user_id": user.user_id,
            "is_payment_done": user.is_payment_done,
            "payments": None  
        }

        if payment_info:
            response["payments"] = []
            for payment in  payment_info:
                response["payments"].append({
                    "payment_id": payment.payment_id,
                    "years": payment.years,
                    "amount": payment.amount,
                    "created_on": payment.created_on
                })

        if  payment_info:
            user.is_payment_done = True
            db.add(user)
            course_details = db.query(CourseDetails).filter(CourseDetails.user_id == user_id).first()
       
            course_details.is_active_course = True
       
            db.add(course_details)
            db.commit()
            response["is_payment_done"] = True
            response["message"] = "Payments verified. Students can access courses."
        else:
            response["message"] = "No payments found. Students cannot access courses."

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify payment details: {str(e)}")

@router.put("/payments/{payment_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_payment(
    payment_id: int, 
    payment: PaymentCreate, 
    db: Session = Depends(get_db), 
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not db_payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        existing_course = db.query(Course).filter(Course.id == payment.course_id).first()
        existing_standard = db.query(Standard).filter(Standard.id == payment.standard_id).first()
        existing_subject = db.query(Subject).filter(Subject.id == payment.subject_id).first()
        existing_module = db.query(Module).filter(Module.id == payment.module_id).first()
        existing_batch = db.query(Batch).filter(Batch.id == payment.batch_id).first()

        if not all([existing_course, existing_standard, existing_subject, existing_module, existing_batch]):
            raise HTTPException(status_code=404, detail="One or more of course, standard, subject, module, or batch not found")

        db_payment.course_id = payment.course_id
        db_payment.standard_id = payment.standard_id
        db_payment.subject_id = payment.subject_id
        db_payment.module_id = payment.module_id
        db_payment.batch_id = payment.batch_id
        db_payment.years = payment.years
        db_payment.amount = payment.amount
        db_payment.payment_mode = payment.payment_mode
        db_payment.payment_info = payment.payment_info
        db_payment.other_info = payment.other_info

        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_payment.updated_on =  ist_now  
        db.commit()
        db.refresh(db_payment)

        return db_payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payment details: {str(e)}")


@router.delete("/payments/delete/{payment_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        db.delete(payment)
        db.commit()
        return {"message": "Payment deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment details: {str(e)}")
