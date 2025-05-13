from fastapi import HTTPException, Depends
from db.base import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, Boolean, DateTime, TIMESTAMP, BIGINT, Enum, ForeignKey
from db.session import api_response, get_db, SessionLocal
from datetime import datetime
import re
from sqlalchemy.orm import relationship
import bcrypt
from api.schemas import ChangePassword, LoginInput, UpdateUser, UserType
from auth.auth_handler import signJWT
import pytz


class LmsUsers(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(255))
    user_email = Column(String(255), unique=True)
    user_password = Column(String(255))
    user_type = Column(String(100))
    phone_no = Column(BIGINT)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    is_deleted = Column(Boolean, server_default='0', nullable=False)
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    deleted_on = Column(DateTime)
    is_payment_done = Column(Boolean, server_default='0', nullable=False)
    is_formsubmited = Column(Boolean, server_default='0', nullable=False)
    reset_otp = Column(Integer)
    otp_generated_at = Column(DateTime, default=func.now())


    demos = relationship("DemoFormFill", back_populates="demo")
    #payments = relationship("PaymentStatus", back_populates="user")
    branch = relationship("Branch", back_populates="user")

    student = relationship("Student", back_populates="user")

    teacher = relationship("Teacher", back_populates="user")

    parent_info = relationship("Parent", back_populates="user")

    teacher_courses = relationship("TeacherCourse", back_populates="user")

    Discount_Ass_result = relationship("DiscountAssessmentResut", back_populates="users")

    answers = relationship("StudentAnswer", back_populates="users")

    installments = relationship("Installment", back_populates="user")

    created_referral_codes = relationship("ReferralCode", back_populates="creator")

    payments = relationship("Payment", back_populates="user")

    social_logins = relationship("SocialAuth", back_populates="user")


    # #######################################################################################################################
    @staticmethod
    def validate_email(email):
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email)

    @staticmethod
    def validate_password(password):
        return len(password) >= 8

    @staticmethod
    def validate_phone_number(phone_number):
        phone_pattern = r"^\d{10}$"
        return re.match(phone_pattern, phone_number)

    @staticmethod
    def lms_register(data: dict, db: SessionLocal):
        try:

            if not LmsUsers.validate_email(data.get('user_email')):
                raise HTTPException(400, detail="Invalid email format")

            if not LmsUsers.validate_password(data.get('user_password')):
                raise HTTPException(400, detail="Password must be at least 8 characters long")

            if not LmsUsers.validate_phone_number(data.get('phone_no')):
                raise HTTPException(400, detail="Invalid Phone number")

            usr = LmsUsers(**data)
            utc_now = pytz.utc.localize(datetime.utcnow())
            ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
            usr.created_on = ist_now
            hashed_password = bcrypt.hashpw(data.get('user_password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            usr.user_password = hashed_password
            db.add(usr)
            db.commit()
            response = api_response(200, message="User Created successfully")
            return response
        except HTTPException as e:
            error_message = e.detail
            return HTTPException(status_code=e.status_code, detail=error_message)
        except Exception as e:
            db.rollback()
            return HTTPException(500, detail="Failed to register, Enter valid email")

    # #######################################################################################################################

    @staticmethod
    def lms_user_update(user_data: UpdateUser, user_id: int, db: SessionLocal):
        try:
            db_user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id,
                                                LmsUsers.is_deleted == False).first()
            if db_user is None:
                return HTTPException(status_code=404, detail="Record not found")

            hero_data = user_data.dict(exclude_unset=True)
            for key, value in hero_data.items():
                setattr(db_user, key, value)

            db.commit()

            response = api_response(200, message="User Data updated successfully")
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ########################################################################################################################

    @staticmethod
    def searchall(user_id: int = None, user_type: UserType = None, page_num: int = 1, page_size: int = 20,
                  db: SessionLocal = Depends(get_db)):
        try:
            start = (page_num - 1) * page_size
            base_query = (
                db.query(LmsUsers).filter(LmsUsers.is_deleted == False))
            if user_id:
                base_query = base_query.filter(LmsUsers.user_id == user_id)
            if user_type:
                base_query = base_query.filter(LmsUsers.user_type == user_type)

            total_users = base_query.count()
            users_records = base_query.offset(start).limit(page_size).all()
            if users_records:
                user_data_dict = {}

                for record in users_records:
                    lms_user = record
                    user_id = lms_user.user_id
                    if user_id not in user_data_dict:
                        user_data_dict[user_id] = {
                            "user_details": lms_user.__dict__ if lms_user else None
                        }

                data = list(user_data_dict.values())

                response = api_response(data=data, total=total_users, status_code=200)

                return response
            return HTTPException(status_code=404, detail="No data found")
        except Exception as e:
            return HTTPException(status_code=500, detail=f"Error: {str(e)}")

    # ------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def lms_delete_user(user_id: int, db: SessionLocal):
        try:
            usr = db.query(LmsUsers).filter(LmsUsers.user_id == user_id,
                                            LmsUsers.is_deleted == False or LmsUsers.is_deleted.is_(None)).first()
            if usr is None:
                return HTTPException(status_code=404, detail=f"Record with id {user_id} not found")

            usr.is_deleted = True
            usr.deleted_on = datetime.now()

            db.commit()
            response = api_response(200, message="User Data deleted successfully")
            return response
        except Exception as e:
            db.rollback()
            return HTTPException(status_code=500, detail=str(e))

    # ###############################################################################################################

    @staticmethod
    def lms_login(credential: LoginInput):

        print(credential,"*****************")
        try:
            session = SessionLocal()
            user = session.query(LmsUsers).filter(LmsUsers.user_email == credential.email,
                                                  LmsUsers.is_deleted == False).first()

            if not user:
                return HTTPException(500, detail=f"Record with Email : {credential.email} not found")

            if bcrypt.checkpw(credential.user_password.encode('utf-8'), user.user_password.encode('utf-8')):
                token, exp = signJWT(user.user_id, user.user_type)
                if user.user_type == "user" or user.user_type == "student":
                    response = {
                        'token': token,
                        'exp' : exp,
                        'user_id': user.user_id,
                        'user_name': user.user_name,
                        'email_id': user.user_email,
                        'user_type': user.user_type,
                        'created_on': user.created_on,
                        'phone_no': user.phone_no,
                        'isFormSubmitted' : user.is_formsubmited,
                        'isPaymentDone' : user.is_payment_done
                    }
                else:
                    response = {
                        'token': token,
                        'exp' : exp,
                        'user_id': user.user_id,
                        'user_name': user.user_name,
                        'email_id': user.user_email,
                        'user_type': user.user_type,
                        'created_on': user.created_on,
                        'phone_no': user.phone_no,
                    }

                return response
            else:
                return HTTPException(500, detail='Invalid email or password')

        except Exception as e:
            return HTTPException(status_code=500, detail=f"Error: {str(e)}")

    ###################################################################################################################

    @staticmethod
    def change_password(current_password: str, new_password: str, user_id: int, is_admin: bool, db: SessionLocal):
        try:
            user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id, LmsUsers.is_deleted == False).first()
            if not user:
                return HTTPException(status_code=404, detail=f"Record with user id {user_id} not found")

            if is_admin:
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                user.user_password = hashed_new_password
            else:
                if not bcrypt.checkpw(current_password.encode('utf-8'), user.user_password.encode('utf-8')):
                    return HTTPException(status_code=400, detail="Wrong password")
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                user.user_password = hashed_new_password

            db.commit()
            response = api_response(200, message="Password changed successfully")
            return response

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    def user_reset_password(db: SessionLocal, email: str, new_password: str):
        try:
            user = db.query(LmsUsers).filter(LmsUsers.user_email == email).first()
            user.user_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            db.commit()
        except Exception:
            return False
        return True
