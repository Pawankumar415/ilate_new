# from datetime import date, timedelta
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from db.session import get_db
# from ..models.installment import Installment
# from ..models import Payment
# from ..models import LmsUsers
# from ..models import ReferralCode

# from ..schemas import PaymentDetails, InstallmentResponse
# from datetime import datetime, timedelta
# from math import ceil, floor
# import json
# #from ..models.installment import InstallmentDetail

# router = APIRouter()

# # ------------------------------------------------------------------------------------------------------------------
#                         #Installment
# # ------------------------------------------------------------------------------------------------------------------

# def calculate_installments(total_amount: float, installment_number: int) -> List[float]:
#     installment_amount = total_amount / installment_number
#     installment_amount = floor(installment_amount)
#     installments = [installment_amount] * installment_number
#     return installments

# def calculate_due_dates(installment_number: int) -> List[str]:
#     current_date = datetime.now()
#     due_dates = [(current_date + timedelta(days=i*30)).strftime('%Y-%m-%d') for i in range(1, installment_number+1)]
#     return due_dates
    



# # @router.post("/installments/Insert/", response_model=None)
# # async def post_payment_details(payment_id: int, total_amount: float, installment_number: int, db: Session = Depends(get_db)):
# #     try:
   
# #         existing_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# #         if not existing_payment:
# #             raise HTTPException(status_code=404, detail="Payment not found")

# #         if total_amount <= 0 or installment_number <= 0:
# #             raise HTTPException(status_code=400, detail="Total amount and installment number must be positive")

# #         installments = calculate_installments(total_amount, installment_number)
# #         due_dates = calculate_due_dates(installment_number)
        
# #         installments_and_due_dates = [{"amount": amount, "due_date": date} for amount, date in zip(installments, due_dates)]
        
# #         installments_json = json.dumps(installments_and_due_dates)

# #         # installment = Installment(payment_id=payment_id, total_amount=total_amount, installment_number=installment_number, installments=installments_json)
# #         # changed by bhavan kumar
# #         installment = Installment(payment_id=payment_id, total_amount=total_amount, installment_number=installment_number, installment_plan=installments_json, due_date=due_dates[0] if due_dates else None, amount_due=total_amount)
# #         db.add(installment)
# #         db.commit()
# #         db.refresh(installment)
# #         db.close()
        
# #         return installment
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to insert installment: {str(e)}")



# ########################################################################################

# @router.post("/installments/Insert/", response_model=None)
# async def post_payment_details(
#     payment_id: int,
#     total_amount: float,
#     installment_number: int,
#     user_id: int,
#     referral_code: str,
#     db: Session = Depends(get_db),
    
# ):
#     try:
#         existing_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
#         if not existing_payment:
#             raise HTTPException(status_code=404, detail="Payment not found")

#         student = db.query(LmsUsers).filter(LmsUsers.user_id == user_id, LmsUsers.user_type == "student").first()
#         if not student:
#             raise HTTPException(status_code=400, detail="Invalid user ID. Must be a student user.")

#         if total_amount <= 0 or installment_number <= 0:
#             raise HTTPException(status_code=400, detail="Total amount and installment number must be positive")

#         discount_rupees = 0.0
#         referral_code_used_id = None
#         if not referral_code:
#             raise HTTPException(status_code=400, detail="Referral code is required for discount.") 

#         referral = db.query(ReferralCode).filter(ReferralCode.code == referral_code, ReferralCode.is_enabled == True, ReferralCode.status == "active").first()
#         if referral:
#             discount_rupees = referral.discount_rupees
#             referral_code_used_id = referral.id
#         else:
#             raise HTTPException(status_code=400, detail="Invalid referral code or it may be disabled") 
#         final_amount = total_amount - discount_rupees

#         installments = calculate_installments(final_amount, installment_number)
#         due_dates = calculate_due_dates(installment_number)

#         installments_and_due_dates = [{"amount": amount, "due_date": date} for amount, date in zip(installments, due_dates)]

#         installments_json = json.dumps(installments_and_due_dates)

#         installment = Installment(
#             user_id=user_id,
#             payment_id=payment_id,
#             total_amount=total_amount,
#             installment_number=installment_number,
#             installment_plan=installments_json,
#             due_date=due_dates[0] if due_dates else None,
#             amount_due=final_amount,
#             referral_code_used=referral_code_used_id,
#             discount_rupees=discount_rupees,
#         )
#         db.add(installment)
#         db.commit()
#         db.refresh(installment)
#         db.close()

#         return installment
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to insert installment: {str(e)}")








# @router.get("/installments/Fetch/{installment_id}", response_model=None)
# async def get_installment(installment_id: int, db: Session = Depends(get_db)):
#     try:
#         installment = db.query(Installment).filter(Installment. installment_id == installment_id).all()
#         if not installment:
#             raise HTTPException(status_code=404, detail="Installment not found")
#         return installment
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch installment: {str(e)}")
    


# @router.put("/installments/Update/{installment_id}", response_model=None)
# async def update_installment(installment_id: int, total_amount: float, installment_number: int, db: Session = Depends(get_db)):
   
#     installment = db.query(Installment).filter(Installment.installment_id == installment_id).first()
#     if not installment:
#         raise HTTPException(status_code=404, detail="Installment not found")

#     installments = calculate_installments(total_amount, installment_number)
#     due_dates = calculate_due_dates(installment_number)

#     installments_and_due_dates = [{"amount": amount, "due_date": date} for amount, date in zip(installments, due_dates)]

#     installments_json = json.dumps(installments_and_due_dates)
#     try:
#         installment.total_amount = total_amount
#         installment.installment_number = installment_number
#         # installment.installments = installments_json
#         installment.installment_plan = installments_json # line chanzged by bhavan kumar
#         db.commit()
#         db.refresh(installment)
#     except Exception as e:
#         db.rollback()  
#         raise HTTPException(status_code=500, detail="An error occurred while updating the installment.") from e
#     finally:
#         db.close()  

#     return installment



    
# @router.delete("/installments/delete/{installment_id}")
# async def delete_installment(installment_id: int, db: Session = Depends(get_db)):
#     try:
#         installments = db.query(Installment).filter(Installment.installment_id == installment_id).all()
#         if not installments:
#             raise HTTPException(status_code=404, detail=f"No installments found for payment_id: {installment_id}")
        
#         for installment in installments:
#             db.delete(installment)  

#         db.commit()
#         return {f"All  data  have been deleted of  payment_id {installment_id}"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete installment: {str(e)}")



####################################################################################


# updated code by bhaavan kumar


from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from db.session import get_db
from ..models.installment import Installment
from ..models import Payment
from ..models import LmsUsers
from ..models import ReferralCode
from ..models import AdminInstallment

from ..schemas import PaymentDetails, InstallmentResponse
from datetime import datetime, timedelta
from math import ceil, floor
import json


router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
#                                                Installment
# ------------------------------------------------------------------------------------------------------------------

def calculate_installments(total_amount: float, installment_number: int) -> List[float]:
    installment_amount = total_amount / installment_number
    installment_amount = floor(installment_amount)
    installments = [installment_amount] * installment_number
    return installments

def calculate_due_dates(installment_number: int) -> List[str]:
    current_date = datetime.now()
    due_dates = [(current_date + timedelta(days=i*30)).strftime('%Y-%m-%d') for i in range(1, installment_number+1)]
    return due_dates
    



# @router.post("/installments/Insert/", response_model=None)
# async def post_payment_details(payment_id: int, total_amount: float, installment_number: int, db: Session = Depends(get_db)):
#     try:
    
#         existing_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
#         if not existing_payment:
#             raise HTTPException(status_code=404, detail="Payment not found")

#         if total_amount <= 0 or installment_number <= 0:
#             raise HTTPException(status_code=400, detail="Total amount and installment number must be positive")

#         installments = calculate_installments(total_amount, installment_number)
#         due_dates = calculate_due_dates(installment_number)
        
#         installments_and_due_dates = [{"amount": amount, "due_date": date} for amount, date in zip(installments, due_dates)]
        
#         installments_json = json.dumps(installments_and_due_dates)

#         # installment = Installment(payment_id=payment_id, total_amount=total_amount, installment_number=installment_number, installments=installments_json)
#         # changed by bhavan kumar
#         installment = Installment(payment_id=payment_id, total_amount=total_amount, installment_number=installment_number, installment_plan=installments_json, due_date=due_dates[0] if due_dates else None, amount_due=total_amount)
#         db.add(installment)
#         db.commit()
#         db.refresh(installment)
#         db.close()
        
#         return installment
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to insert installment: {str(e)}")



########################################################################################

@router.post("/installments/Insert/", response_model=None)
async def post_payment_details(
    payment_id: int,
    user_id: int,
    course_id: int,
    number_of_installments: int,
    referral_code: Optional[str] = None,
    db: Session = Depends(get_db),
    
):
    try:
        existing_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not existing_payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        student = db.query(LmsUsers).filter(LmsUsers.user_id == user_id, LmsUsers.user_type == "student").first()
        if not student:
            raise HTTPException(status_code=400, detail="Invalid user ID. Must be a student user.")

        if  number_of_installments <= 0:
            raise HTTPException(status_code=400, detail="Installment number must be positive")

        admin_installment_plan = db.query(AdminInstallment).filter(AdminInstallment.course_id == course_id, AdminInstallment.number_of_installments == number_of_installments).first()
        if not admin_installment_plan:
            raise HTTPException(status_code=404, detail=f"No installment plan found for course {course_id} and {number_of_installments} installments")
        
        discount_rupees = 0.0
        referral_code_used_id = None
        if referral_code:
            referral = db.query(ReferralCode).filter(ReferralCode.code == referral_code, ReferralCode.is_enabled == True, ReferralCode.status == "active").first()
            if referral:
                discount_rupees = referral.discount_rupees
                referral_code_used_id = referral.id
            else:
                raise HTTPException(status_code=400, detail="Invalid referral code or it may be disabled") 
        final_amount = admin_installment_plan.total_amount - discount_rupees

        
        installments_data = []
        if number_of_installments == 1:
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 1,
                "due_date": admin_installment_plan.installment_1_due_date,
                "installment_amount": admin_installment_plan.installment_1_amount,
                "total_amount": final_amount,
            })
        elif number_of_installments == 2:
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 1,
                "due_date": admin_installment_plan.installment_1_due_date,
                "installment_amount": admin_installment_plan.installment_1_amount,
                "total_amount": final_amount,
            })
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 2,
                "due_date": admin_installment_plan.installment_2_due_date,
                "installment_amount": admin_installment_plan.installment_2_amount,
                "total_amount": final_amount,
            })
        elif number_of_installments == 3:
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 1,
                "due_date": admin_installment_plan.installment_1_due_date,
                "installment_amount": admin_installment_plan.installment_1_amount,
                "total_amount": final_amount,
            })
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 2,
                "due_date": admin_installment_plan.installment_2_due_date,
                "installment_amount": admin_installment_plan.installment_2_amount,
                "total_amount": final_amount,
            })
            installments_data.append({
                "user_id": user_id,
                "payment_id": payment_id,
                "admin_installment_id": admin_installment_plan.id,
                "installment_number": 3,
                "due_date": admin_installment_plan.installment_3_due_date,
                "installment_amount": admin_installment_plan.installment_3_amount,
                "total_amount": final_amount,
            })
        

        # 3. Create the installment records in the database.
        db_installments = [Installment(**data, referral_code_used=referral_code_used_id, discount_rupees=discount_rupees) for data in installments_data]
        db.add_all(db_installments)
        db.commit()
        for inst in db_installments:
            db.refresh(inst) #refresh every instance
        return db_installments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert installment: {str(e)}")








@router.get("/installments/Fetch/{installment_id}", response_model=None)
async def get_installment(installment_id: int, db: Session = Depends(get_db)):
    try:
        installment = db.query(Installment).filter(Installment. installment_id == installment_id).all()
        if not installment:
            raise HTTPException(status_code=404, detail="Installment not found")
        return installment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch installment: {str(e)}")
    


@router.put("/installments/Update/{installment_id}", response_model=None)
async def update_installment(installment_id: int, total_amount: float, installment_number: int, db: Session = Depends(get_db)):
    
    installment = db.query(Installment).filter(Installment.installment_id == installment_id).first()
    if not installment:
        raise HTTPException(status_code=404, detail="Installment not found")

    installments = calculate_installments(total_amount, installment_number)
    due_dates = calculate_due_dates(installment_number)

    installments_and_due_dates = [{"amount": amount, "due_date": date} for amount, date in zip(installments, due_dates)]

    installments_json = json.dumps(installments_and_due_dates)
    try:
        installment.total_amount = total_amount
        installment.installment_number = installment_number
        # installment.installments = installments_json
        installment.installment_plan = installments_json # line chanzged by bhavan kumar
        db.commit()
        db.refresh(installment)
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail="An error occurred while updating the installment.") from e
    finally:
        db.close() 

    return installment



    
@router.delete("/installments/delete/{installment_id}")
async def delete_installment(installment_id: int, db: Session = Depends(get_db)):
    try:
        installments = db.query(Installment).filter(Installment.installment_id == installment_id).all()
        if not installments:
            raise HTTPException(status_code=404, detail=f"No installments found for payment_id: {installment_id}")
        
        for installment in installments:
            db.delete(installment) 

        db.commit()
        return {f"All  data  have been deleted of  payment_id {installment_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete installment: {str(e)}")
