from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from datetime import date
from sqlalchemy.orm import Session, joinedload
from db.session import get_db, SessionLocal
from ..models import Student, ContactInformation, PreEducation, Parent, LmsUsers, Inquiry, DemoFormFill, CourseDetails,Course, Standard, module,Subject, Module, Payment
from ..schemas import (StudentContactCreate, PreEducationCreate, ParentCreate,
                       StudentContactUpdate, PreEducationUpdate, ParentInfoUpdate, CourseDetailsCreate, CourseDetailsUpdate,StudentUpdate_data, ContactInfoUpdate_data,
                       PreEducationUpdate_data, ParentInfoUpdate_data)
from auth.auth_bearer import JWTBearer, get_current_user, get_admin, get_admin_or_student,get_admin_student_teacher_parent
from ..schemas import StudentCreate ,StudentUpdate
from datetime import datetime
from typing import List, Union
from sqlalchemy import desc
from typing import Optional
import os
import uuid
import shutil
from datetime import date
import pytz
from .Email_config import send_email
import bcrypt
from pydantic import EmailStr, BaseModel
from ..models.courses_content import Course_content
from dotenv import load_dotenv
import re
from sqlalchemy.orm import aliased


load_dotenv()
router = APIRouter()


def get_student(db: Session, user_id: int):
    return db.query(Student) \
        .options(joinedload(Student.contact_info),
                 joinedload(Student.pre_education),
                 joinedload(Student.parent_info),
                 joinedload(Student.branch),
                 joinedload(Student.course_details)) \
        .filter(Student.user_id == user_id).first()


def get_all_students(db: Session):
    return db.query(Student) \
        .options(joinedload(Student.contact_info),
                 joinedload(Student.pre_education),
                 joinedload(Student.parent_info),
                 joinedload(Student.course_details)) \
        .all()


def get_contact_info(db: Session, student_id: int):
    return db.query(ContactInformation).filter(ContactInformation.student_id == student_id).first()


def get_pre_education(db: Session, student_id: int):
    return db.query(PreEducation).filter(PreEducation.student_id == student_id).first()


def get_parent_info(db: Session, student_id: int):
    return db.query(Parent).filter(Parent.student_id == student_id).first()

def get_course_details(db: Session, student_id: int):
    return db.query(CourseDetails).filter(CourseDetails.student_id == student_id).first()


def update_student(db: Session, student_id: int, student_data: StudentUpdate):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if db_student:
        for key, value in student_data.dict(exclude_unset=True).items():
            setattr(db_student, key, value)
        db.commit()
        db.refresh(db_student)
        return db_student
    else:
        raise HTTPException(status_code=404, detail="Student not found")


def update_contact_info(db: Session, student_id: int, contact_info: StudentContactUpdate):
    db_contact_info = db.query(ContactInformation).filter(ContactInformation.student_id == student_id).first()
    if db_contact_info:
        for key, value in contact_info.dict(exclude_unset=True).items():
            setattr(db_contact_info, key, value)
        db.commit()
        db.refresh(db_contact_info)
    else:
        raise HTTPException(status_code=404, detail="Contact information not found")


def update_pre_education(db: Session, student_id: int, pre_education: PreEducationUpdate):
    db_pre_education = db.query(PreEducation).filter(PreEducation.student_id == student_id).first()
    if db_pre_education:
        for key, value in pre_education.dict(exclude_unset=True).items():
            setattr(db_pre_education, key, value)
        db.commit()
        db.refresh(db_pre_education)
    else:
        raise HTTPException(status_code=404, detail="Pre-education information not found")


def update_parent_info(db: Session, student_id: int, parent_info: ParentInfoUpdate):
    db_parent_info = db.query(Parent).filter(Parent.student_id == student_id).first()
    if db_parent_info:
        for key, value in parent_info.dict(exclude_unset=True).items():
            setattr(db_parent_info, key, value)
        db.commit()
        db.refresh(db_parent_info)
    else:
        raise HTTPException(status_code=404, detail="Parent information not found")


def update_course_details(db: Session, student_id: int, course_details_update: CourseDetailsUpdate):
    db_course_details = get_course_details(db, student_id)
    if db_course_details:
        for key, value in course_details_update.dict().items():
            setattr(db_course_details, key, value)
        db.commit()
        db.refresh(db_course_details)
        return db_course_details
    else:
        raise HTTPException(status_code=404, detail="Course details not found")


def delete_student(db: Session, student_id: int):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
        return True
    return False

############################################################################################################################
def get_subject_by_id(db: Session, subject_id: int) -> dict:
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"id": subject.id, "name": subject.name}

def get_standard_by_id(db: Session, standard_id: int) -> dict:
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    return {"id": standard.id, "name": standard.name}

def get_module_by_id(db: Session, module_id: int) -> dict:
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"id": module.id, "name": module.name}

def get_course_by_id(db: Session, course_id: int) -> dict:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"id": course.id, "name": course.name}

def get_payment_status_by_user_id(db: Session, user_id: int) -> bool:
    user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
    if user:
        return user.is_payment_done
    return False

def check_payment_status(user_id: int, db: Session):
    payment_status = get_payment_status_by_user_id(db, user_id)
    if not payment_status:
        raise HTTPException(status_code=400, detail="Payment not made")
    
def get_payment_status_by_user_id(db_session: Session, user_id: int) -> bool:
    
    user = db_session.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
    if user:
        return user.is_payment_done
    else:
        return False 

def save_upload_file(upload_file: Optional[UploadFile]) -> Optional[str]:
    if not upload_file:
        return None
    
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "uploads", unique_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Convert backslashes to forward slashes
        file_path = file_path.replace("\\", "/")
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

def validate_phone_number(number, field_name):
    if number is None:
        raise HTTPException(status_code=400, detail=f"{field_name} is required.")
    if len(number) != 10 or not number.isdigit():
        raise HTTPException(status_code=400, detail=f"{field_name} must be 10-digit number.")
    
def validate_emails(*emails):
    for email in emails:
        if email and not LmsUsers.validate_email(email):
            raise HTTPException(status_code=400, detail=f"Invalid email format: {email}")
    
#############################################################################################################

@router.post("/admission/", response_model=None)
async def fill_admission_form(
    first_name: str = Form(...),
    middle_name: str = Form(None),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    referral: str = Form(None),
    date_of_joining: date = Form(...),
    date_of_completion: date = Form(None),
    s_primary_no: str = Form(...),
    s_secondary_no: str = Form(None),
    s_primary_email: str = Form(...),
    s_secondary_email: str = Form(None),
    current_address: str = Form(...),
    permanent_address: str = Form(...),
    student_class: str = Form(...),
    school: str = Form(...),
    year_of_passing: int = Form(...),  
    percentage: float = Form(...),
    p_first_name: str = Form(...),
    p_middle_name: str = Form(None),
    p_last_name: str = Form(...),
    p_guardian: str = Form(...),
    p_primary_no: str = Form(...),
    # p_secondary_no: str = Form(None),
    p_primary_email: str = Form(...),
    # p_secondary_email: str = Form(None),
    subject: int = Form(...),
    standard: int = Form(...),
    module: int = Form(...),
    course: int = Form(...),
    id_proof: UploadFile = File(...),
    address_proof: UploadFile = File(default=None),
    profile_photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    existing_form = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if existing_form:
        raise HTTPException(status_code=400, detail="Admission form has already been submitted")
    
    user_db=db.query(LmsUsers).filter(LmsUsers.user_id== current_user.user_id).first()
    if not user_db:
         raise HTTPException(status_code=404, detail="your are not correct user")
    
    id_proof_path = save_upload_file(id_proof)
    address_proof_path = save_upload_file(address_proof)
    profile_photo_url = save_upload_file(profile_photo)

    validate_phone_number(s_primary_no, "Student's primary contact number")
    #validate_phone_number(s_secondary_no, "Student's secondary contact number")
    validate_phone_number(p_primary_no, "Parent's primary contact number")
    validate_emails(s_primary_email, s_secondary_email, p_primary_email)

    if not id_proof:
        raise HTTPException(status_code=400, detail="ID proof is required")
    
    if not profile_photo:
        raise HTTPException(status_code=400, detail="profile photo is required")
    
    if s_primary_email == p_primary_email:
        raise HTTPException(status_code=400, detail="Student's primary Email and Parent's primary Email cannot be the same.")
    
    parent_db = db.query(LmsUsers).filter(LmsUsers.user_email == p_primary_email).first()
    if parent_db:
            raise HTTPException(status_code=400, detail="Parent email already exists and must be unique.")
    try:
        parent_user_id = p_primary_email
        parent_password = p_first_name + "@123"
        hashed_password = bcrypt.hashpw((parent_password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db_student = Student(
            user_id=current_user.user_id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            referral=referral,
            nationality=nationality,
            date_of_joining=date_of_joining,
            date_of_completion=date_of_completion,
            id_proof=id_proof_path,
            Address_proof=address_proof_path,
            profile_photo=profile_photo_url,
            branch_id=user_db.branch_id,
        )
        db.add(db_student)
        db.flush()
        db.refresh(db_student)
        
        db_contact_info = ContactInformation(
            primary_no=s_primary_no,
            secondary_no=s_secondary_no,
            primary_email=s_primary_email,
            secondary_email=s_secondary_email,
            current_address=current_address,
            permanent_address=permanent_address,
            student_id=db_student.id
        )
        db.add(db_contact_info)

        db_pre_education = PreEducation(
            student_class=student_class,
            school=school,
            year_of_passing=year_of_passing,
            percentage=percentage,
            student_id=db_student.id
        )
        db.add(db_pre_education)

        db_lmsuser = LmsUsers(
            user_name=p_first_name,
            user_email=p_primary_email,
            user_password=hashed_password,
            user_type="parent",
            phone_no=p_primary_no
        )
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_lmsuser.created_on = ist_now
        db.add(db_lmsuser)
        db.flush()
        db.refresh(db_lmsuser)

        db_parent_info = Parent(
            user_id=db_lmsuser.user_id,
            p_first_name=p_first_name,
            p_middle_name=p_middle_name,
            p_last_name=p_last_name,
            guardian=p_guardian,
            primary_no=p_primary_no,
            primary_email=p_primary_email,
            student_id=db_student.id
        )
        db.add(db_parent_info)

        CourseContentAlias = aliased(Course_content)

        query = db.query(CourseContentAlias).filter(
            CourseContentAlias.is_active == True
        )
        if course is not None:
            query = query.filter(CourseContentAlias.course_id == course)
        if standard is not None:
            query = query.filter(CourseContentAlias.standard_id == standard)
        if subject is not None:
            query = query.filter(CourseContentAlias.subject_id == subject)
        if module is not None:
            query = query.filter(CourseContentAlias.module_id == module)

        admin_course = query.first()

        if not admin_course:
            raise HTTPException(status_code=400, detail="Selected course not found or not active. Please choose a valid course.")

        db_course_details = CourseDetails(
            subjects=subject,
            standards=standard,
            modules=module,
            courses=course,
            students=db_student.id,
            user_id=current_user.user_id, 
            course_content_id=admin_course.id
        )
        db.add(db_course_details)

        current_user.user_type = 'student'
        current_user.is_formsubmited = True
        db.add(current_user)

        db.commit()

        email_body = f"""
        <p>Dear {p_first_name},</p>
        <p>Your child, student ID :{db_student.id} {first_name} {last_name}, has been successfully enrolled. Here are your login credentials:</p>
        <p>User ID: {parent_user_id}</p>
        <p>Password: {parent_password}</p>
        <p>Please use these credentials to log in for further updates.</p>
        <br>
        <p>Best regards,</p>
        <p>Vinay Kumar</p>
        <p>MaitriAI</p>
        <p>900417181</p>
        """
        await send_email(
            subject="Parent Account credentials",
            email_to=p_primary_email,
            body=email_body
        )
        return {"message": "Admission form has been submitted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=f"{e}")

base_url_path = os.getenv("BASE_URL_PATH")

@router.get("/admission/get_all", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_all_admissions(db: Session = Depends(get_db)):
    try:
        students = get_all_students(db)
        if not students:
            raise HTTPException(status_code=404, detail="No students found")
        
        all_students_data = []
        for student in students:
            id_proof_url = f"{base_url_path}/{student.id_proof}" if student.id_proof else None
            address_proof_url = f"{base_url_path}/{student.Address_proof}" if student.Address_proof else None
            profile_photot_url = f"{base_url_path}/{student.profile_photo}" if student.profile_photo else None

            def convert_to_names(ids: Union[int, List[int]], get_name_func):
                if isinstance(ids, int):
                    return get_name_func(db, ids)
                elif isinstance(ids, list):
                    return [get_name_func(db, id) for id in ids]
                return None

            student_data = {
                "user_id": student.user_id,
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "date_of_birth": student.date_of_birth,
                "gender": student.gender,
                "nationality": student.nationality,
                "referral": student.referral,
                "date_of_joining": student.date_of_joining,
                "branch_name": student.branch.name,
                "date_of_completion": student.date_of_completion,
                "id_proof_url": id_proof_url,
                "address_proof_url": address_proof_url,
                "profile_photo":profile_photot_url,
                "contact_info": {
                    "primary_no": student.contact_info.primary_no,
                    "secondary_no": student.contact_info.secondary_no,
                    "primary_email": student.contact_info.primary_email,
                    "secondary_email": student.contact_info.secondary_email,
                    "current_address": student.contact_info.current_address,
                    "permanent_address": student.contact_info.permanent_address
                },
                "pre_education": {
                    "student_class": student.pre_education.student_class,
                    "school": student.pre_education.school,
                    "year_of_passing": student.pre_education.year_of_passing,
                    "percentage": student.pre_education.percentage
                },
                "parent_info": {
                    "p_first_name": student.parent_info.p_first_name,
                    "p_middle_name": student.parent_info.p_middle_name,
                    "p_last_name": student.parent_info.p_last_name,
                    "guardian": student.parent_info.guardian,
                    "primary_no": student.parent_info.primary_no,
                    "primary_email": student.parent_info.primary_email
                },
                "course_details": {
                    "subjects": convert_to_names(student.course_details.subjects, get_subject_by_id),
                    "standards": convert_to_names(student.course_details.standards, get_standard_by_id),
                    "modules": convert_to_names(student.course_details.modules, get_module_by_id),
                    "courses": convert_to_names(student.course_details.courses, get_course_by_id)
                }
            }
            all_students_data.append(student_data)

        return all_students_data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Student not found")

@router.get("/admission/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_student_teacher_parent)])
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    try:
        student = get_student(db, user_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        is_payment_done = get_payment_status_by_user_id(db, user_id)

        id_proof_url = f"{base_url_path}/{student.id_proof}" if student.id_proof else None
        address_proof_url = f"{base_url_path}/{student.Address_proof}" if student.Address_proof else None
        profile_photot_url = f"{base_url_path}/{student.profile_photo}" if student.profile_photo else None

        def convert_to_names(ids: Union[int, List[int]], get_name_func):
            if isinstance(ids, int):
                return get_name_func(db, ids)
            elif isinstance(ids, list):
                return [get_name_func(db, id) for id in ids]
            return None

        student_data = {
            "user_id": student.user_id,
            "student_id": student.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "date_of_birth": student.date_of_birth,
            "gender": student.gender,
            "nationality": student.nationality,
            "referral": student.referral,
            "date_of_joining": student.date_of_joining,
            "branch_name": student.branch.name,
            "date_of_completion": student.date_of_completion,
            "id_proof_url": id_proof_url,
            "address_proof_url": address_proof_url,
            "profile_photo":profile_photot_url,
            "contact_info": {
                "primary_no": student.contact_info.primary_no,
                "secondary_no": student.contact_info.secondary_no,
                "primary_email": student.contact_info.primary_email,
                "secondary_email": student.contact_info.secondary_email,
                "current_address": student.contact_info.current_address,
                "permanent_address": student.contact_info.permanent_address
            },
            "pre_education": {
                "student_class": student.pre_education.student_class,
                "school": student.pre_education.school,
                "year_of_passing": student.pre_education.year_of_passing,
                "percentage": student.pre_education.percentage
            },
            "parent_info": {
                "p_first_name": student.parent_info.p_first_name,
                "p_middle_name": student.parent_info.p_middle_name,
                "p_last_name": student.parent_info.p_last_name,
                "guardian": student.parent_info.guardian,
                "primary_no": student.parent_info.primary_no,
                "primary_email": student.parent_info.primary_email
            },
            "course_details": {
                "subjects": convert_to_names(student.course_details.subjects, get_subject_by_id),
                "standards": convert_to_names(student.course_details.standards, get_standard_by_id),
                "modules": convert_to_names(student.course_details.modules, get_module_by_id),
                "courses": convert_to_names(student.course_details.courses, get_course_by_id)
            },
            "payment_details": {
                "is_payment_done": is_payment_done
            }
        }

        payment = db.query(Payment).filter(Payment.user_id == user_id).order_by(desc(Payment.created_on)).first()
        if payment:
                utc_now = pytz.utc.localize(datetime.utcnow())
                ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
                student_data["payment_details"].update({
                    "payment_id": payment.payment_id,
                    "amount": payment.amount,
                    "payment_mode": payment.payment_mode,
                    "payment_info": payment.payment_info,
                    "other_info": payment.other_info,
                    "created_on": ist_now
                })
        student_data["is_payment_done"] = is_payment_done
        return student_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch student admission form: {str(e)}")


@router.put("/admission/{student_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_current_user)])
async def update_admission_form(
    student_id: int,
    student_update: StudentUpdate_data,
    contact_info:ContactInfoUpdate_data,
    pre_education:PreEducationUpdate_data,
    parent_info:ParentInfoUpdate_data,

    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        existing_student = db.query(Student).filter(Student.id == student_id).first()
        if not existing_student:
            raise HTTPException(status_code=404, detail="Student not found")

        if student_update.first_name is not None:
            existing_student.first_name = student_update.first_name
        if student_update.middle_name is not None:
            existing_student.middle_name = student_update.middle_name
        if student_update.last_name is not None:
            existing_student.last_name = student_update.last_name
        if student_update.date_of_birth is not None:
            existing_student.date_of_birth = student_update.date_of_birth
        if student_update.gender is not None:
            existing_student.gender = student_update.gender
        if student_update.nationality is not None:
            existing_student.nationality = student_update.nationality
        if student_update.referral is not None:
            existing_student.referral = student_update.referral
        if student_update.date_of_joining is not None:
            existing_student.date_of_joining = student_update.date_of_joining
        if student_update.date_of_completion is not None:
            existing_student.date_of_completion = student_update.date_of_completion
        db.add(existing_student)
        db.commit()
       
        existing_contact_info = db.query(ContactInformation).filter(ContactInformation.student_id == student_id).first()
        if not existing_contact_info:
            raise HTTPException(status_code=404, detail="Student contact_info not found")
        
        if contact_info.primary_no is not None:
                    existing_contact_info.primary_no = contact_info.primary_no
        if contact_info.secondary_no is not None:
                    existing_contact_info.secondary_no = contact_info.secondary_no
        if contact_info.primary_email is not None:
                    existing_contact_info.primary_email = contact_info.primary_email
        if contact_info.secondary_email is not None:
                    existing_contact_info.secondary_email = contact_info.secondary_email
        if contact_info.current_address is not None:
                    existing_contact_info.current_address = contact_info.current_address
        if contact_info.permanent_address is not None:
                    existing_contact_info.permanent_address = contact_info.permanent_address
        db.add(existing_contact_info)
        db.commit()    

        existing_pre_education = db.query(PreEducation).filter(PreEducation.student_id == student_id).first()
        if not existing_pre_education:
            raise HTTPException(status_code=404, detail="Student pre_education not found")
        
        if pre_education.student_class is not None:
                    existing_pre_education.student_class = pre_education.student_class
        if pre_education.school is not None:
                    existing_pre_education.school = pre_education.school
        if pre_education.year_of_passing is not None:
                    existing_pre_education.year_of_passing = pre_education.year_of_passing
        if pre_education.percentage is not None:
                    existing_pre_education.percentage = pre_education.percentage
        db.add(existing_pre_education)
        db.commit()
        
        existing_parent_info = db.query(Parent).filter(Parent.student_id == student_id).first()
        if not existing_pre_education:
            raise HTTPException(status_code=404, detail="Student pre_education not found")
        
        if parent_info.p_first_name is not None:
                    existing_parent_info.p_first_name = parent_info.p_first_name
        if parent_info.p_middle_name is not None:
                    existing_parent_info.p_middle_name = parent_info.p_middle_name
        if parent_info.p_last_name is not None:
                    existing_parent_info.p_last_name = parent_info.p_last_name
        if parent_info.guardian is not None:
                    existing_parent_info.guardian = parent_info.guardian
        if parent_info.primary_no is not None:
                    existing_parent_info.primary_no = parent_info.primary_no
        if parent_info.primary_email is not None:
                    existing_parent_info.primary_email = parent_info.primary_email
        db.add(existing_parent_info)   
        db.commit()

        response_data = {
            "student_id": existing_student.id,
            "first_name": existing_student.first_name,
            "middle_name": existing_student.middle_name,
            "last_name": existing_student.last_name,
            "date_of_birth": existing_student.date_of_birth,
            "gender": existing_student.gender,
            "nationality": existing_student.nationality,
            "referral": existing_student.referral,
            "date_of_joining": existing_student.date_of_joining,
            "date_of_completion": existing_student.date_of_completion,
            "contact_info": {
                "primary_no": existing_contact_info.primary_no,
                "secondary_no": existing_contact_info.secondary_no,
                "primary_email": existing_contact_info.primary_email,
                "secondary_email": existing_contact_info.secondary_email,
                "current_address": existing_contact_info.current_address,
                "permanent_address": existing_contact_info.permanent_address
            },
            "pre_education": {
                "student_class": existing_student.pre_education.student_class,
                "school": existing_student.pre_education.school,
                "year_of_passing": existing_student.pre_education.year_of_passing,
                "percentage": existing_student.pre_education.percentage
            },
            "parent_info": {
                "p_first_name": existing_student.parent_info.p_first_name,
                "p_middle_name": existing_student.parent_info.p_middle_name,
                "p_last_name": existing_student.parent_info.p_last_name,
                "guardian": existing_student.parent_info.guardian,
                "primary_no": existing_student.parent_info.primary_no,
                "primary_email": existing_student.parent_info.primary_email
            }
        }

        return response_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/admission/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_admission_form(user_id: int, db: Session = Depends(get_db)):
    try:
        existing_form = db.query(Student).filter(Student.user_id == user_id).first()
        if not existing_form:
            raise HTTPException(status_code=404, detail="Student not found")

        db.query(ContactInformation).filter(ContactInformation.student_id == existing_form.id).delete()
        db.query(PreEducation).filter(PreEducation.student_id == existing_form.id).delete()
        db.query(Parent).filter(Parent.student_id == existing_form.id).delete()
        
        if existing_form.id_proof and os.path.exists(existing_form.id_proof):
            os.remove(existing_form.id_proof)
        if existing_form. Address_proof and os.path.exists(existing_form. Address_proof):
            os.remove(existing_form. Address_proof)
        
        db.delete(existing_form)
        db.commit()

        lms_user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        if not lms_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        lms_user.user_type = 'student'
        lms_user.is_formsubmited = False
        lms_user.is_payment_done = False
        db.commit()

        return {"message": "Student data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete student admission form: {str(e)}")


@router.get("/dashboard_counts", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def get_dashboard_counts(db: Session = Depends(get_db)):
    try:
        total_users = db.query(LmsUsers).count()
        total_teachers = db.query(LmsUsers).filter(LmsUsers.user_type == "teacher").count()
        total_students = db.query(LmsUsers).filter(LmsUsers.user_type == "student").count()
        total_inquiries = db.query(Inquiry).count()
        total_demo = db.query(DemoFormFill).count()

        return {
            "user_count": total_users,
            "teacher_count": total_teachers,
            "student_count": total_students,
            "inquiry_count": total_inquiries,
            "demo_count": total_demo
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delte student admission form: {str(e)}")


