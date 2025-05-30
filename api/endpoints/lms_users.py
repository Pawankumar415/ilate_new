from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer, get_user_id_from_token, is_admin, get_admin, get_current_user
from db.session import get_db, api_response
from ..models.user import LmsUsers
from ..schemas import LoginInput, ChangePassword, UserCreate, UpdateUser, UserType
import bcrypt
from .Email_config import send_email
import random
import pytz

router = APIRouter()

user_ops = LmsUsers()


def generate_token(data):
    exp = datetime.utcnow() + timedelta(days=1)
    token_payload = {'user_id': data['emp_id'], 'exp': exp}
    token = jwt.encode(token_payload, 'cat_walking_on_the street', algorithm='HS256')
    return token, exp


@router.post('/lms_login')
async def lms_login(credential: LoginInput):
    try:
        response = user_ops.lms_login(credential)
        
        return response
    except HTTPException as e:
        
        raise
    except Exception as e:
       
        return HTTPException(status_code=500, detail=f"login failed: {str(e)}")



@router.post("/insert/lms_user")
async def lms_register(data: UserCreate, db: Session = Depends(get_db)):
    return user_ops.lms_register(data.model_dump(), db)


@router.get("/read/lms_user", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def searchall(user_id: int = None, user_type: UserType = None, page_num: int = 1, page_size: int = 20,
                    db: Session = Depends(get_db)):
    return user_ops.searchall(user_id, user_type, page_num, page_size, db)


@router.get("/get_my_profile")
def get_current_user_details(current_user: LmsUsers = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_details = {
            "user_id": current_user.user_id,
            "username": current_user.user_name,
            "email": current_user.user_email,
            "user_type": current_user.user_type,
            "is_formsubmited": current_user.is_formsubmited,
            "is_payment_done": current_user.is_payment_done,
            "created_on": current_user.created_on,

        }
        return api_response(data=user_details, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/update/lms_user/{user_id}", dependencies=[Depends(JWTBearer())])
async def lms_user_update(user_data: UpdateUser, user_id: int,
                          current_user: LmsUsers = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    try:
        if user_data.user_type and user_data.user_type not in {"user", "admin", "teacher", "student", "parent"}:
            raise HTTPException(status_code=403, detail="Invalid user type. Allowed values: user, admin, teacher, student, parent")

        if current_user.user_type == "admin" or current_user.user_id == user_id:
            db_user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id, LmsUsers.is_deleted == False).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail="Record not found")

            if user_data.user_email:
                existing_user = db.query(LmsUsers).filter(
                    LmsUsers.user_email == user_data.user_email,
                    LmsUsers.user_id != user_id
                ).first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="Email already exists for another user")

            hero_data = user_data.dict(exclude_unset=True)
            for key, value in hero_data.items():
                setattr(db_user, key, value)

            is_administrator: bool = current_user.user_type == "admin"

            if (is_administrator and user_data.new_password) or (
                    not is_administrator and user_data.current_password and user_data.new_password):
                if not user_ops.validate_password(user_data.new_password):
                    raise HTTPException(status_code=400, detail="Invalid new password")

                current_password = None if is_administrator else user_data.current_password
                user_ops.change_password(current_password, user_data.new_password, user_id, is_administrator, db)

            db.commit()
            response = api_response(200, message="User Data updated successfully")
            return response
        else:
            raise HTTPException(status_code=403, detail="Forbidden: You are not authorized to update this user's data.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

#######################################################################################

@staticmethod
def validate_password(password):
        return len(password) >= 8


@router.put("/change_password/{user_id}")
async def change_password(current_password: str, new_password: str, confirm_new_password: str, current_user: LmsUsers = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")

        user = db.query(LmsUsers).filter(LmsUsers.user_id == current_user.user_id, LmsUsers.is_deleted == False).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {current_user.user_id} not found")

        if not bcrypt.checkpw(current_password.encode('utf-8'), user.user_password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Wrong current password")

        if not user_ops.validate_password(new_password):
            raise HTTPException(status_code=400, detail="Invalid new password")
        
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.user_password = hashed_new_password

        db.commit()
        contact = "900-417-3181"
        email_contact = "vinay@example.com"

        reset_email_body = f"""
        <p>Dear User,</p>
        <p>Your password has been successfully changed.</p>
        <p>If you did not request this change, please contact support at {contact} or email us at {email_contact}.</p>
        <p>Thank you!</p>
        <br><br>
        <p>Best regards,</p>
        <p>Vinay Kumar</p>
        <p>MaitriAI</p>
        <p>900417181</p>
        """
        await send_email(
            subject="Password Change Confirmation",
            email_to=user.user_email,
            body=reset_email_body
        )
        return {"message": "Password changed successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



def generate_otp():
    return random.randint(100000, 999999)

async def send_otp_email(email: str, otp: int):
    otp_email_body = f"""
    <p>Dear User,</p>
    <p>Your OTP for password reset is: <strong>{otp}</strong></p>
    <p>Please use this OTP to reset your password.</p>
    <br><br>
    <p>Best regards,</p>
    <p>Vinay Kumar</p>
    <p>MaitriAI</p>
    <p>900417181</p>
    """
    await send_email(
        subject="Password Reset OTP",
        email_to=email,
        body=otp_email_body
    )

@router.post("/send_otp")
async def send_otp(email: str, db: Session = Depends(get_db)):
    user = db.query(LmsUsers).filter(LmsUsers.user_email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")

    otp = generate_otp()
    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    user.reset_otp = otp
    user.otp_generated_at = ist_now
    
    db.commit()

    await send_otp_email(email, otp)
    return {"message": "OTP sent successfully"}


@router.put("/reset_password")
async def forgot_password(otp:int, email: str, new_password: str, confirm_new_password: str, db: Session = Depends(get_db)):
    try:

        otp_created_at = db.query(LmsUsers.otp_generated_at).filter(LmsUsers.reset_otp == otp).first()

        if otp_created_at is None:
            raise HTTPException(status_code=400, detail="Invalid OTP") 

        current_time = datetime.now()
        time_difference = current_time - otp_created_at[0]
        validity_period = timedelta(minutes=2)
        if time_difference > validity_period:
            db.query(LmsUsers).filter(LmsUsers.reset_otp == otp).update({LmsUsers.reset_otp: None})
            db.commit()  
            raise HTTPException(status_code=400, detail="OTP expired, please generate a new one")
        else:
            print("OTP is still valid.")
           
        retrieved_otp = db.query(LmsUsers.reset_otp).filter(LmsUsers.user_email == email).first()
        if not retrieved_otp[0]:
            raise ValueError("OTP Expired, please generate new one!")
        
        if otp != retrieved_otp[0]:
            raise HTTPException(status_code=400, detail="OTP do not match")


        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        user = db.query(LmsUsers).filter(LmsUsers.user_email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found")
        
        if not validate_password(new_password):
            raise HTTPException(status_code=400, detail="Invalid new password")

        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.user_password = hashed_new_password

        db.commit()

        # Send email for password reset
        contact = "900-417-3181"
        email_contact = "vinay@example.com"

        reset_email_body = f"""
        <p>Dear User,</p>
        <p>Your password has been successfully changed.</p>
        <p>If you did not request this change, please contact support at {contact} or email us at {email_contact}.</p>
        <p>Thank you!</p>
        <br><br>
        <p>Best regards,</p>
        <p>Illate team</p>
        <p>Illate</p>
        <p>900417181</p>
        """
        await send_email(
            subject="Password Reset Request",
            email_to=email,
            body=reset_email_body
        )

        return {"message": "Password reset successfully"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while Reset password")