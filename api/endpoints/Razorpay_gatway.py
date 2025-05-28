from datetime import datetime, timedelta, timezone
import os
from sqlalchemy import Boolean, Column, Integer, Float, String, ForeignKey, DateTime, func, TIMESTAMP, text
from sqlalchemy.orm import selectinload
import pytz
from api.models.installment import Installment
from api.models.payment import Payment
import razorpay
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import requests
import httpx
from fastapi import FastAPI, APIRouter, HTTPException, Request
import httpx
import hmac
import hashlib
from pydantic import BaseModel
import hmac
import hashlib
import json
from ..models.course_detail import CourseDetails 
from sqlalchemy.orm import Session
import razorpay
from api.models.referal_code import ReferralCode
from api.models.user import LmsUsers
from api.models.admin_installment import AdminInstallment
from auth.auth_bearer import JWTBearer, get_admin, get_admin_or_student, get_current_user
from db.session import get_db, SessionLocal
from ..schemas import CreateOrderRequest, VerifyPaymentRequest, VerifyPaymentRequest, ReferralCodeCreate
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.orm import joinedload
from pydantic import BaseModel


router = APIRouter()
logger = logging.getLogger(__name__)


RAZORPAY_KEY = os.getenv("RAZORPAY_KEYS")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRETS")
client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

if not RAZORPAY_KEY or not RAZORPAY_SECRET:
    raise ValueError("RAZORPAY_KEY or RAZORPAY_SECRET is missing in environment variables.")




####################################### updated by bhavan kumar 
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@router.post("/create_order/payment")
async def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        

        ist = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(ist)

        discount_rupees = 0
        is_referral_used = False
        original_amount = request.amount

        # Block if pending installments exist
        pending_installment = db.query(Installment).filter(
            Installment.user_id == current_user.user_id,
            Installment.status == "pending"
        ).order_by(Installment.installment_number.asc()).first()

        if pending_installment:
            raise HTTPException(
                status_code=400,
                detail=f"Please pay your previous pending installment first. Installment Number: {pending_installment.installment_number}"
            )

        # Referral code validation
        if request.referral_code:
            referral_entry = db.query(ReferralCode).filter(
                ReferralCode.code == request.referral_code,
                ReferralCode.status == "active"
            ).first()

            if not referral_entry:
                raise HTTPException(status_code=404, detail="Invalid or inactive referral code.")

            already_used = db.query(Payment).filter(
                Payment.user_id == current_user.user_id,
                Payment.referral_code == request.referral_code,
                Payment.is_referral_code_used == True
            ).first()

            if already_used:
                raise HTTPException(status_code=400, detail="Referral code already used by you.")

            if referral_entry.is_enabled:
                discount_rupees = referral_entry.discount_rupees
                is_referral_used = True

        # Get this installment's data from admin's installment_data

        current_installment_data = next(
            (item for item in request.installments_data if item.installment_number == request.installment_number),None)
        
        logger.info(f"Installment data received: {current_installment_data.dict() if current_installment_data else 'None'}")

        if not current_installment_data or current_installment_data.amount_due is None:
            logger.warning("amount_due missing in current_installment_data")
            raise HTTPException(status_code=400, detail="amount_due missing in current installment_data")



        if not current_installment_data:
            raise HTTPException(status_code=404, detail="Installment data not found.")
        
        per_installment_amount = float(current_installment_data.amount_due)

        # Sum of all installments
        total_installments_amount = sum(item.amount_due for item in request.installments_data)

        if request.installment_number == 1 and is_referral_used:
            # Apply discount only on first installment
            first_installment_amount = next(item.amount_due for item in request.installments_data if item.installment_number == 1)
            discounted_first_installment = first_installment_amount - discount_rupees
            
            # Final amount = discounted first installment + sum of other installments (except first)
            remaining_sum = total_installments_amount - first_installment_amount
            final_amount = round(discounted_first_installment + remaining_sum, 2)

            per_installment_amount = round(discounted_first_installment, 2)
        else:
            per_installment_amount = next(item.amount_due for item in request.installments_data if item.installment_number == request.installment_number)
            final_amount = round(total_installments_amount, 2)


        # Create Razorpay Order
        order_data = {
            "amount": int(per_installment_amount * 100),
            "currency": request.currency,
            "receipt": request.receipt,
        }

        # Invoice ID generation
        new_invoice_number = db.execute(
            text("SELECT MAX(CAST(SUBSTRING(invoice_id, 5) AS UNSIGNED)) FROM payments_tb")
        ).scalar()
        new_invoice_number = 1200 if new_invoice_number is None else new_invoice_number + 1
        new_invoice_id = f"AMMP{new_invoice_number}"

        order = client.order.create(data=order_data)

        # Insert into payments_tb
        payment = Payment(
            user_id=current_user.user_id,
            course_id=request.course_id,
            standard_id=request.standard_id,
            subject_id=request.subject_id,
            module_id=request.module_id,
            batch_id=request.batch_id,
            years=request.years,
            amount=original_amount,
            final_amount=final_amount,
            discount=discount_rupees if request.installment_number == 1 else 0,
            currency=request.currency,
            razorpay_order_id=order["id"],
            status="created",
            payment_mode=request.payment_mode,
            payment_info=request.payment_info,
            other_info=request.other_info,
            referral_code=request.referral_code if is_referral_used else None,
            is_referral_code_used=is_referral_used,
            receipt=request.receipt,
            invoice_id=new_invoice_id,
            gst=request.gst,
            created_on=ist_now,
            amount_paid=0.0,
            installment_count=request.installments
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # fetching admin_installment_id from db

        installment_data = db.query(AdminInstallment).filter(
            AdminInstallment.course_id == request.course_id,
            AdminInstallment.year == request.years,
            AdminInstallment.subject_id == request.subject_id,
            AdminInstallment.batch_id == request.batch_id
        ).first()

        if not installment_data:
            raise HTTPException(status_code=404, detail="Admin installment not found.")


        if request.installment_number == 1:
            amount_due = installment_data.installment_1_amount
            due_date = installment_data.installment_1_due_date
        elif request.installment_number == 2:
            amount_due = installment_data.installment_2_amount
            due_date = installment_data.installment_2_due_date
        elif request.installment_number == 3:
            amount_due = installment_data.installment_3_amount
            due_date = installment_data.installment_3_due_date
        else:
            raise HTTPException(status_code=400, detail="Invalid installment number")

   

        admin_installment_id = installment_data.id
        if not db.query(Installment).filter_by(
            user_id=current_user.user_id,
            payment_id=payment.payment_id,
            installment_number=request.installment_number
        ).first():

            logger.info(f"Saving installment with amount_due: {per_installment_amount}, discount_applied: {discount_rupees}")

        installment_plan_data = {
            "total_installments": request.installments,
            "current_installment_number": request.installment_number,
            "amount_due": per_installment_amount,
            "due_date": str(current_installment_data.due_date)
            }
             
        installment = Installment(
            user_id=current_user.user_id,
            payment_id=payment.payment_id,
            installment_number=request.installment_number,
            admin_installment_id=admin_installment_id,
            installment_plan=installment_plan_data,
            due_date=current_installment_data.due_date,
            total_amount=original_amount,
            amount_due=per_installment_amount,
            paid_amount=0.0,
            status="pending",
            referral_code_used=referral_entry.id if is_referral_used and request.installment_number == 1 else None,
            discount_rupees=discount_rupees if request.installment_number == 1 else 0.0
        )
        db.add(installment)
        db.commit()

        return {
            "status": "success",
            "order_id": order["id"],
            "final_amount": final_amount,
            "discount_applied": discount_rupees if request.installment_number == 1 else 0,
            "paid_amount": 0,
            "remaining_amount": final_amount,
            "order_details": order,
        }

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error occurred while creating the order.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
    
    

    
###############################################################################################################
    

def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    





@router.post("/verify_payment/")
async def verify_payment(
    request: VerifyPaymentRequest, 
    db: Session = Depends(get_db), 
    current_user: LmsUsers = Depends(get_current_user)
):
    
    # original_amount = request.amount
    try:
        razorpay_payment_id = request.razorpay_payment_id
        razorpay_order_id = request.razorpay_order_id
        razorpay_signature = request.razorpay_signature


        # ✅ Verify Razorpay Signature
        if not verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            raise HTTPException(status_code=400, detail="Invalid Razorpay signature")

        # ✅ Fetch payment details from Razorpay
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.razorpay.com/v1/payments/{razorpay_payment_id}",
                auth=(RAZORPAY_KEY, RAZORPAY_SECRET)
            )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch payment details from Razorpay")

        payment_data = response.json()
        print(payment_data, "<<<<<< payment_data >>>>>>")
        
        payment_status = payment_data.get("status", "failed")
        payment_amount = payment_data.get("amount", 0) / 100  # Razorpay gives in paise
        payment_currency = payment_data.get("currency", "INR")

        if not current_user.user_id:
            raise HTTPException(status_code=400, detail="User not found")

        # ✅ Fetch the existing transaction
        transaction = db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # ✅ Update transaction data
        # transaction.amount = payment_amount
        # transaction.final_amount = payment_amount
        transaction.currency = payment_currency
        transaction.razorpay_payment_id = razorpay_payment_id
        transaction.status = payment_status
        if transaction.referral_code:
            transaction.is_referral_code_used = True

        # ✅ Update updated_on timestamp
        ist_now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        transaction.updated_on = ist_now

        db.commit()
        db.refresh(transaction)  # Ensure payment_id is populated

        # ✅ Fetch admin_installment_id
        admin_installment = db.query(AdminInstallment).filter(
            AdminInstallment.course_id == transaction.course_id,
            AdminInstallment.batch_id == transaction.batch_id,
            AdminInstallment.subject_id == transaction.subject_id,
            AdminInstallment.year == transaction.years
        ).first()

        if not admin_installment:
            raise HTTPException(status_code=404, detail="Admin installment record not found")

        # ✅ Add Installments (avoid duplicates)
        installments_data = request.installments_data
        print(">>>>>> installments_data ", installments_data)

        for installment_data in installments_data:
            existing = db.query(Installment).filter_by(
                user_id=current_user.user_id,
                payment_id=transaction.payment_id,
                installment_number=installment_data["installment_number"]
            ).first()
            if existing:
                continue  # ❌ Skip duplicate

            new_installment = Installment(
                user_id=current_user.user_id,
                payment_id=transaction.payment_id,
                installment_number=installment_data["installment_number"],
                admin_installment_id=admin_installment.id,
                installment_plan={
                    "total_installments": len(installments_data),
                    "current_installment_number": installment_data["installment_number"],
                    "amount_due": installment_data["amount"],
                    "due_date": str(installment_data["due_date"])
                },
                due_date=installment_data["due_date"],
                total_amount=transaction.amount,
                amount_due=installment_data["amount"],
                paid_amount=0,
                status="pending",
            )
            db.add(new_installment)

        db.commit()

        if transaction.status == "captured":
            next_installment_paid = db.query(Installment).filter(
                Installment.payment_id == transaction.payment_id,
                Installment.user_id == current_user.user_id,
                Installment.status == "pending",  # This ensures you don’t overwrite paid ones
                Installment.amount_due == payment_amount  # Optional but adds safety
            ).order_by(Installment.installment_number.asc()).first()

            if next_installment_paid:
                next_installment_paid.paid_amount = payment_amount
                next_installment_paid.status = "paid"
                db.add(next_installment_paid)
                db.commit()

                # 🆕 ADD THIS 👇
                from sqlalchemy import func

                total_paid_amount = db.query(func.sum(Installment.paid_amount)).filter(
                    Installment.payment_id == transaction.payment_id,
                    Installment.status == "paid"
                ).scalar() or 0

                transaction.amount_paid = total_paid_amount

                total_installments = db.query(Installment).filter(
                    Installment.payment_id == transaction.payment_id
                ).count()

                paid_installments = db.query(Installment).filter(
                    Installment.payment_id == transaction.payment_id,
                    Installment.status == "paid"
                ).count()

                if total_installments == paid_installments:
                    transaction.status = "completed"
                else:
                    transaction.status = "partial"

                print(f"Paid: ₹{payment_amount}, Total Paid: ₹{total_paid_amount}, Status: {transaction.status}")


                db.add(transaction)
                db.commit()



        return {
            "status": "success",
            "message": "Payment verified and processed successfully",
            "payment_details": payment_data
        }

    except HTTPException as http_exc:
        raise http_exc
    except httpx.RequestError as e:
        db.rollback()
        logger.error(f"Razorpay API connection error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to connect to Razorpay API")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while processing payment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error while processing payment: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")




########################################### for installment ###################################################################
# API 1 - Create Razorpay Order


@router.post("/pay-next-installment", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
async def pay_next_installment(installment_number: int, db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):

    try:

        pending_installment = db.query(Installment).filter(Installment.user_id == current_user.user_id,
                            Installment.status == "pending",Installment.installment_number < installment_number).order_by(Installment.installment_number.asc()).first()
        if pending_installment:
                raise HTTPException(status_code=400,detail=f"Please pay your previous pending installment first. Installment Number: {pending_installment.installment_number}")

        installment = db.query(Installment).filter(
            Installment.installment_number == installment_number,
            Installment.user_id == current_user.user_id
        ).first()

        if not installment:
            raise HTTPException(status_code=404, detail="Installment Not Found")
        
        next_installment = db.query(Installment).filter(
            Installment.installment_number == installment_number,
            Installment.user_id == current_user.user_id,
            Installment.status == "pending"
        ).first()

        if not next_installment:
            raise HTTPException(status_code=404, detail="Installment Already Paid.")

        order_data = {
            "amount": int(next_installment.amount_due * 100),
            "currency": "INR",
            "receipt": f"receipt_inst_{next_installment.installment_id}",
        }
        order = client.order.create(data=order_data)

        return {
            "order_id": order['id'],
            "amount": next_installment.amount_due,
            "currency": "INR",
            "installment_number": next_installment.installment_number,
            "due_date": next_installment.due_date
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
    




# API 2 - Verify Payment
class RazorPayPaymentResponse(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    installment_number: int



@router.post("/verify-payment-callback", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
async def verify_payment_callback(payment_response: RazorPayPaymentResponse, db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):
    try:
        installment = db.query(Installment).filter(
            Installment.installment_number == payment_response.installment_number,
            Installment.user_id == current_user.user_id
        ).first()

        if not installment:
            raise HTTPException(status_code=404, detail="Installment Not Found")

        if installment.status == "paid":
            raise HTTPException(status_code=400, detail="Installment Already Paid")

        params_dict = {
            'razorpay_order_id': payment_response.razorpay_order_id,
            'razorpay_payment_id': payment_response.razorpay_payment_id,
            'razorpay_signature': payment_response.razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except:
            raise HTTPException(status_code=400, detail="Payment Verification Failed")

        # ✅ Mark installment as paid
        installment.status = "paid"
        installment.paid_amount = installment.amount_due
        installment.updated_on = datetime.utcnow()
        logger.info(f"[Installment Update] Installment {installment.installment_id} marked as paid.")

        db.flush()  # ⭐ VERY IMPORTANT - ensures installment is updated before aggregate queries

        # ✅ Fetch corresponding Payment
        payment = db.query(Payment).filter(Payment.payment_id == installment.payment_id).first()
        if not payment:
            logger.error(f"[Payment Missing] No payment found for installment {installment.installment_id}")
        else:
            logger.info(f"[Payment Found] Payment ID: {payment.payment_id}, Current Installment Count: {payment.installment_count}")

            total_paid = db.query(func.sum(Installment.paid_amount)).filter(
                Installment.payment_id == installment.payment_id,
                Installment.status == "paid"
            ).scalar() or 0

            paid_installments_count = db.query(func.count(Installment.installment_id)).filter(
                Installment.payment_id == installment.payment_id,
                Installment.status == "paid"
            ).scalar() or 0

            logger.info(f"[Payment Stats] Total Paid: {total_paid}, Paid Installments: {paid_installments_count}")

            # Update fields
            payment.razorpay_order_id = payment_response.razorpay_order_id
            payment.razorpay_payment_id = payment_response.razorpay_payment_id
            payment.updated_on = datetime.utcnow()
            payment.amount_paid = total_paid

            # 💥 Try direct assignment instead of +=
            logger.info(f"[Before Update] Installment Count: {payment.installment_count}")
            # payment.installment_count = paid_installments_count
            logger.info(f"[After Update] Installment Count Set To: {payment.installment_count}")

            # Update status
            if total_paid >= (payment.final_amount or 0):
                payment.status = "completed"
            else:
                payment.status = "partial"

            logger.info(f"[Payment Status] New Status: {payment.status}")

        db.commit()
        logger.info(f"[DB Commit] Changes committed to DB.")
        return {
            "message": "Payment Verified Successfully!",
            "payment_status": payment.status,
            "total_paid": total_paid,
            "final_amount": payment.final_amount
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")




    


@router.get("/all-user-installments", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
async def get_all_user_installments(
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        # Query all installments for the current user
        user_installments = db.query(Installment).options(
                joinedload(Installment.payment)
            ).filter(
                Installment.user_id == current_user.user_id
            ).order_by(Installment.installment_number.asc()).all()
        
        if not user_installments:
            return {"message": "No Installments Found", "installments": []}
        
        # Format the response
        installments_data = []
        for installment in user_installments:
            installments_data.append({
                "installment_id": installment.installment_id,
                "installment_number": installment.installment_number,
                "due_date": installment.due_date,
                "amount_due": installment.amount_due,
                "status": installment.status,
                "payment_date": installment.created_on if hasattr(installment, 'created_on') else None,
                "transaction_id": installment.payment.razorpay_payment_id if installment.payment else None
            })
        
        return {
            "message": "User Installments Retrieved Successfully",
            "installments": installments_data
        }
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")
    


    
@router.get("/all-user-payments-details", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def get_all_user_payments_details(
    db: Session = Depends(get_db),
):
    try:
        payments = db.query(Payment).options(
            joinedload(Payment.installments),
            joinedload(Payment.course),
            joinedload(Payment.standard),
            joinedload(Payment.subject),
            joinedload(Payment.module),
            joinedload(Payment.batch)
        ).all()

        if not payments:
            return {"message": "No Payment Records Found", "data": []}

        result = []
        for payment in payments:
            installment_data = []
            for installment in payment.installments:
                installment_data.append({
                    "installment_id": installment.installment_id,
                    "installment_number": installment.installment_number,
                    "due_date": installment.due_date,
                    "amount_due": installment.amount_due,
                    "status": installment.status,
                    "updated_on":installment.updated_on
                })

            result.append({
                "payment_id": payment.payment_id,
                "user_name": payment.user.user_name,
                "amount": payment.amount,
                "final_amount": payment.final_amount,
                "payment_mode": payment.payment_mode,
                "payment_info": payment.payment_info,
                "other_info": payment.other_info,
                "created_on": payment.created_on,
                "status": payment.status,
                "razorpay_payment_id": payment.razorpay_payment_id,
                "course_name": payment.course.name if payment.course else None,
                "standard_name": payment.standard.name if payment.standard else None,
                "subject_name": payment.subject.name if payment.subject else None,
                "module_name": payment.module.name if payment.module else None,
                "batch_name": payment.batch.size if payment.batch else None,
                "invoice_id":payment.invoice_id,
                "gst":payment.gst,
                "installments": installment_data
            })

        return {
            "message": "All User Payment Details Retrieved Successfully",
            "data": result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")




@router.get("/student-payment-details", dependencies=[Depends(JWTBearer())])
async def get_student_payment_details(
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        payments = db.query(Payment).options(
            joinedload(Payment.installments),
            joinedload(Payment.course),
            joinedload(Payment.standard),
            joinedload(Payment.subject),
            joinedload(Payment.module),
            joinedload(Payment.batch)
        ).filter(Payment.user_id == current_user.user_id).all() 

        if not payments:
            return {"message": "No Payment Records Found", "data": []}

        result = []
        for payment in payments:
            installment_data = []
            for installment in payment.installments:
                installment_data.append({
                    "installment_id": installment.installment_id,
                    "installment_number": installment.installment_number,
                    "due_date": installment.due_date,
                    "amount_due": installment.amount_due,
                    "status": installment.status,
                    "updated_on": installment.updated_on
                })

            result.append({
                "payment_id": payment.payment_id,
                "user_name": current_user.user_name, # Use current_user
                "amount": payment.amount,
                "final_amount": payment.final_amount,
                "payment_mode": payment.payment_mode,
                "payment_info": payment.payment_info,
                "other_info": payment.other_info,
                "created_on": payment.created_on,
                "status": payment.status,
                "razorpay_payment_id": payment.razorpay_payment_id,
                "course_name": payment.course.name if payment.course else None,
                "standard_name": payment.standard.name if payment.standard else None,
                "subject_name": payment.subject.name if payment.subject else None,
                "module_name": payment.module.name if payment.module else None,
                "batch_name": payment.batch.size if payment.batch else None,
                "invoice_id": payment.invoice_id,
                "gst": payment.gst,
                "installments": installment_data
            })

        return {
            "message": "Student Payment Details Retrieved Successfully",
            "data": result
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")



@router.delete("/delete-payment/{payment_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        # Delete all installments manually
        for installment in payment.installments:
            db.delete(installment)

        db.delete(payment)
        db.commit()

        return {
            "message": f"Payment with ID {payment_id} deleted successfully",
            "data": {}
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")

    



# @router.post("/payments/apply-referral/", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
# def apply_referral_code(
#     referral_code: str,
#     db: Session = Depends(get_db),
#     current_user: LmsUsers = Depends(get_current_user)
# ):
#     try:
#         code_entry = db.query(ReferralCode).filter(
#             ReferralCode.code == referral_code
#         ).first()

#         if not code_entry:
#             raise HTTPException(status_code=404, detail="Referral code not found")

#         # Ensure timezone-aware comparison
#         if code_entry.created_on.tzinfo is None:
#             code_entry.created_on = code_entry.created_on.replace(tzinfo=timezone.utc)  

#         utc_now = datetime.now(timezone.utc)
#         expiry_date = code_entry.created_on + timedelta(days=code_entry.expiry_days)
        
#         if code_entry.status != "active" or utc_now > expiry_date:
#             code_entry.status = "expired"  
#             db.commit()  
#             raise HTTPException(status_code=400, detail="Referral code has expired or is inactive")
        
#         discount_percentage = code_entry.discount_percentage  
#         discount_multiplier = discount_percentage / 100

#         return {
#             "message": "Referral code validated",
#             "discount_percentage": discount_percentage,
#             "discount_multiplier": discount_multiplier
#         }
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error applying referral code: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error applying referral code: {str(e)}")
    
# @router.post("/payments/validate-referral/", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
# def validate_referral_code(
#     referral_code: str,
#     db: Session = Depends(get_db),
#     current_user: LmsUsers = Depends(get_current_user)
# ):
#     try:
#         # Query the referral code from database
#         code_entry = db.query(ReferralCode).filter(
#             ReferralCode.code == referral_code
#         ).first()

#         if not code_entry:
#             raise HTTPException(status_code=404, detail="Referral code not found")

#         # Ensure timezone-aware comparison
#         if code_entry.created_on.tzinfo is None:
#             code_entry.created_on = code_entry.created_on.replace(tzinfo=timezone.utc)  

#         utc_now = datetime.now(timezone.utc)
#         expiry_date = code_entry.created_on + timedelta(days=code_entry.expiry_days)
        
#         # Check if code is expired or inactive
#         if code_entry.status != "active" or utc_now > expiry_date:
#             code_entry.status = "expired"  
#             db.commit()  
#             raise HTTPException(status_code=400, detail="Referral code has expired or is inactive")
        
#         discount_percentage = code_entry.discount_percentage  
#         discount_multiplier = discount_percentage / 100

#         return {
#             "status": "valid",
#             "message": "Referral code is valid",
#             "discount_percentage": discount_percentage,
#             "discount_multiplier": discount_multiplier,
#             "code": code_entry.code,
#             "expiry_date": expiry_date.isoformat(),
#             "created_by": code_entry.created_by
#         }
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error validating referral code: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error validating referral code: {str(e)}")
       



# @router.post("/create_order/")
# async def create_order(request: CreateOrderRequest, db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):
#     try:
#         BASE_URL = "https://api.razorpay.com/v1/orders"

#         order_data = {
#             "amount": int(request.amount * 100),  
#             "currency": request.currency,
#             "receipt": request.receipt,
#         }
        
#         order = client.order.create(data=order_data)
    
#         payment = Payment(
#             user_id=current_user.user_id,
#             course_id=request.course_id,
#             standard_id=request.standard_id,
#             subject_id=request.subject_id,
#             module_id=request.module_id,
#             batch_id=request.batch_id,
#             years=request.years,
#             amount=request.amount,
#             currency=request.currency,
#             razorpay_order_id=order["id"],
#             payment_status="created",
#             payment_mode=request.payment_mode,
#             payment_info=request.payment_info,
#             other_info=request.other_info,
#         )
#         utc_now = pytz.utc.localize(datetime.utcnow())
#         ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
#         payment.created_on = ist_now
#         db.refresh(payment)
#         db.add(payment)
#         db.commit()
#         db.refresh(payment)
        
#         return {
#             "status": "success",
#             "order_id": order["id"],
#             "order_details": order,
#         }
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail=f"A database error occurred while create order.{e}")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred  while create order.{e}")

