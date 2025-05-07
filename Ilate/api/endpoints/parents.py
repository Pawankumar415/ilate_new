from fastapi import APIRouter, Depends, HTTPException
from ..models import Parent
from ..schemas import ParentCreate,ParentUpdate
from sqlalchemy.orm import Session,joinedload
from db.session import get_db, SessionLocal
from ..models import Student, ContactInformation, PreEducation, Parent, LmsUsers, Inquiry, DemoFormFill, CourseDetails,Course, Standard, module,Subject, Module, Payment
from auth.auth_bearer import JWTBearer, get_admin_or_parent,get_user_id_from_token, get_admin_student_teacher_parent, get_current_user

######
from sqlalchemy import desc
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.auth_handler import decodeJWT
from db.session import get_db
from sqlalchemy.orm import Session
from typing import Optional
from api.models.user import LmsUsers
from jwt import PyJWTError
import time
from typing import Any
import jwt
from decouple import config
from jwt import PyJWTError
from pydantic import EmailStr, BaseModel
import bcrypt
from .std_profile import send_email
####
from ..models.announcement import Announcement


router = APIRouter()


#########################################################################################################################
                    # for parent 
##########################################################################################################################

@router.post("/parent/", response_model=None)
def create_parent(parent: ParentCreate, db: Session = Depends(get_db)):
    try:
        db_parent = Parent(**parent.dict())
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
        return db_parent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert parent: {str(e)}")

@router.get("/student/{student_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_parent)])
def read_student_details(student_id: int, user_id: int = Depends(get_user_id_from_token), db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.user_type == 'parent':
            parent = db.query(Parent).filter(Parent.user_id == user_id, Parent.student_id == student_id).first()
            if not parent:
                raise HTTPException(status_code=403, detail="Access denied. This student is not associated with the parent.")
        else:
            parent = db.query(Parent).filter(Parent.student_id == student_id).first()

        # Fetch course details
        course_details = db.query(CourseDetails).filter(CourseDetails.students == student_id).first()
        if course_details:
            course = db.query(Course).filter(Course.id == course_details.courses).first()
            standard = db.query(Standard).filter(Standard.id == course_details.standards).first()
            subject = db.query(Subject).filter(Subject.id == course_details.subjects).first()
            module = db.query(Module).filter(Module.id == course_details.modules).first()
        else:
            course = None
            standard = None
            subject = None
            module = None

        payment = db.query(Payment).filter(Payment.user_id == student.user_id).order_by(desc(Payment.created_on)).first()

        return {
            "student_id": student.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "nationality": student.nationality,
            "date_of_joining": student.date_of_joining,
            "date_of_completion": student.date_of_completion,
            "parent_details": {
                "parent_id": parent.parent_id if parent else None,
                "first_name": parent.p_first_name if parent else None,
                "middle_name": parent.p_middle_name if parent else None,
                "last_name": parent.p_last_name if parent else None,
                "guardian": parent.guardian if parent else None,
                "primary_no": parent.primary_no if parent else None,
                "primary_email": parent.primary_email if parent else None,
            },
            "course_details": {
                "course_name": course.name if course else None,
                "standard_name": standard.name if standard else None,
                "subject_name": subject.name if subject else None,
                "module_name": module.name if module else None,
            },
            "payment_details": {
                "payment_id": payment.payment_id if payment else None,
                "amount": payment.amount if payment else None,
                "payment_mode": payment.payment_mode if payment else None,
                "payment_info": payment.payment_info if payment else None,
                "other_info": payment.other_info if payment else None,
                "created_on": payment.created_on if payment else None,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student data: {str(e)}")


@router.get("/parent/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_parent)])
def read_parent(user_id: int, db: Session = Depends(get_db)):
    try:
        parent = db.query(Parent).filter(Parent.user_id == user_id).options(joinedload(Parent.student)).first()
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent not found")
        return {
            "parent_id": parent.parent_id,
            "p_first_name": parent.p_first_name,
            "p_middle_name": parent.p_middle_name,
            "p_last_name": parent.p_last_name,
            "guardian": parent.guardian,
            "primary_no": parent.primary_no,
            "primary_email": parent.primary_email,
            "student_id":parent.student_id,
            "s_user_id":parent.student.user_id,
            "user_type":parent.user_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch parent: {str(e)}")

@router.get("/parent/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_parent)])
def read_all_parent(db: Session = Depends(get_db)):
    try:
        parents = db.query(Parent).all()
        if not parents:
            raise HTTPException(status_code=404, detail="Parents not found")
        
        parent_data = [
            {
                "p_first_name": parent.p_first_name,
                "p_middle_name": parent.p_middle_name,
                "p_last_name": parent.p_last_name,
                "guardian": parent.guardian,
                "primary_no": parent.primary_no,
                "primary_email": parent.primary_email,
                "student_id": parent.student_id,
                "user_type": parent.user_type,
            }
            for parent in parents
        ]
        
        return parent_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch parent data: {str(e)}")



@router.put("/parent/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_parent)])
def update_parent_form(
    user_id: int,
    parent_update: ParentUpdate,  
    db: Session = Depends(get_db)
):
    try:
        db_parent = db.query(Parent).filter(Parent.user_id == user_id).first()
        if db_parent is None:
            raise HTTPException(status_code=404, detail="Parent not found")
       
        if parent_update.p_first_name is not None:
            db_parent.p_first_name = parent_update.p_first_name
        if parent_update.p_middle_name is not None:
            db_parent.p_middle_name = parent_update.p_middle_name
        if parent_update.p_last_name is not None:
            db_parent.p_last_name = parent_update.p_last_name
        if parent_update.guardian is not None:
            db_parent.guardian = parent_update.guardian
        if parent_update.primary_no is not None:
            db_parent.primary_no = parent_update.primary_no
        if parent_update.secondary_no is not None:
            db_parent.secondary_no = parent_update.secondary_no
        if parent_update.primary_email is not None:
            db_parent.primary_email = parent_update.primary_email
        if parent_update.secondary_email is not None:
            db_parent.secondary_email = parent_update.secondary_email

        db.commit()
        db.refresh(db_parent)
        
        return db_parent  

    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail=f"Failed to update parent: {str(e)}")
    

