from fastapi import APIRouter, Depends, HTTPException,Query,Path
import pytz
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
from api.models.payment import Payment
from auth.auth_bearer import JWTBearer, get_admin, get_admin_or_student, get_current_user
from ..models.referal_code import ReferralCode
from ..models.user import LmsUsers
from ..schemas import ReferralCodeCreate, ReferralCodeResponse
from db.session import get_db, SessionLocal
from sqlalchemy.orm import Session, joinedload

import logging

router = APIRouter()
logger = logging.getLogger(__name__)



###########################################################################################
# updated by bhavan kumar


@router.post("/referral-codes_create/", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def create_referral_code(
    code: str = Query(..., description="Referral code to create"),
    discount_rupees: int = Query(0, description="Discount amount in rupees"),
    is_enabled: bool = Query(True, description="Is the referral code enabled?"),
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        existing_code = db.query(ReferralCode).filter(ReferralCode.code == code).first()
        if existing_code:
            raise HTTPException(status_code=400, detail="Referral code already exists")

        new_code = ReferralCode(
            code=code,
            created_by=current_user.user_id,
            discount_rupees=discount_rupees,
            created_on=ist_now,
            status="active",
            is_enabled=is_enabled
        )

        db.add(new_code)
        db.commit()
        db.refresh(new_code)

        return {
            "status": "created",
            "message": "Referral code created successfully",
            "code": new_code.code,
            "discount_rupees": discount_rupees,
            "is_enabled": is_enabled
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating referral code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating referral code: {str(e)}")





@router.get("/get_all_referral_codes/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])  
async def get_all_referral_codes(db: Session = Depends(get_db)):
    try:
        return db.query(ReferralCode).all()
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetch referral code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetch referral code: {str(e)}")
    
#######set status of referral code API implimentened by Srikanth #######
    
@router.put(
    "/referral-codes/{id}/set-status",
    dependencies=[Depends(JWTBearer()), Depends(get_admin)]
)
async def set_referral_code_status(
    id: int = Path(..., description="ID of the referral code to update"),
    is_active: bool = Query(..., description="Set to true to activate, false to deactivate"),
    db: Session = Depends(get_db)
):
    referral = db.query(ReferralCode).filter(ReferralCode.id == id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral code not found")

    referral.status = "active" if is_active else "inactive"
    db.commit()
    db.refresh(referral)

    return {
        "status": "success",
        "message": f"Referral code '{referral.code}' status set to '{referral.status}'.",
        "referral_id": referral.id,
        "new_status": referral.status
    }
    






# @router.get("/payments/validate-referral/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
# async def validate_referral_code(code: str, db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):
#     try:
#         code_entry = db.query(ReferralCode).filter(
#             ReferralCode.code == code,
#             ReferralCode.status == "active"  
#         ).first()

#         if not code_entry:
#             raise HTTPException(status_code=404, detail="Referral code not found or inactive")
        
#         already_used = db.query(Payment).filter(
#                 Payment.user_id == current_user.user_id,
#                 Payment.referral_code == code,
#                 Payment.is_referral_code_used == True
#             ).first()

#         if already_used:
#                 raise HTTPException(status_code=400, detail="Referral code already used by you.")

#         if code_entry.created_on.tzinfo is None:
#             code_entry.created_on = pytz.utc.localize(code_entry.created_on)

#         utc_now = pytz.utc.localize(datetime.utcnow())
#         ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

#         expiry_date = code_entry.created_on + timedelta(days=code_entry.expiry_days)
#         expiry_date_ist = expiry_date.astimezone(pytz.timezone('Asia/Kolkata'))

#         if ist_now > expiry_date_ist:
#             raise HTTPException(status_code=400, detail="Referral code has expired")

#         return {
#             "status": "valid",
#             "message": "Referral code is valid",
#             "discount_rupees": code_entry.discount_rupees,
#             "discount_multiplier": code_entry.discount_rupees,
#             "code": code_entry.code,
#             "expiry_date": expiry_date_ist.isoformat(),
#         }

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error validating referral code: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal server error")
    
##############################################################################################################


# updated by bhavan kumar

@router.get("/payments/validate-referral/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
async def validate_referral_code(code: str = Query(..., description="Enter the referral code to validate"), db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):
    try:
        code_entry = db.query(ReferralCode).filter(
            ReferralCode.code == code,
            ReferralCode.status == "active",
            ReferralCode.is_enabled == True # Check is_enabled
        ).first()

        if not code_entry:
            raise HTTPException(status_code=404, detail="Referral code not found or inactive")

        already_used = db.query(Payment).filter(
            Payment.user_id == current_user.user_id,
            Payment.referral_code == code,
            Payment.is_referral_code_used == True
        ).first()

        if already_used:
            raise HTTPException(status_code=400, detail="Referral code already used by you.")

        return {
            "status": "valid",
            "message": "Referral code is valid",
            "discount_rupees": code_entry.discount_rupees,
            "discount_multiplier": code_entry.discount_rupees,
            "code": code_entry.code,
            "is_enabled": code_entry.is_enabled # Added is_enabled to response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error validating referral code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    
    







# @router.post("/validateand_apply_referral/", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
# def validate_referral_code(
#     referral_code: str,
#     db: Session = Depends(get_db),
#     current_user: LmsUsers = Depends(get_current_user)
# ):
#     try:
#         code_entry = db.query(ReferralCode).options(joinedload(ReferralCode.creator)).filter(ReferralCode.code == referral_code).first()

#         if not code_entry:
#             raise HTTPException(status_code=404, detail="Referral code not found")

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
#             "status": "valid",
#             "message": "Referral code is valid",
#             "discount_percentage": discount_percentage,
#             "discount_multiplier": discount_multiplier,
#             "code": code_entry.code,
#             "expiry_date": expiry_date.isoformat(),
#             "created_by": code_entry.creator.user_name
#         }
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Error validating referral code: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Error validating referral code: {str(e)}")
