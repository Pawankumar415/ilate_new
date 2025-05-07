from datetime import datetime
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException
import pytz
from sqlalchemy import desc
from sqlalchemy.orm import Session
from api.endpoints.std_profile import get_course_by_id, get_module_by_id, get_payment_status_by_user_id, get_standard_by_id, get_student, get_subject_by_id
from api.models import Teacher
from api.models.payment import Payment
from api.models.user import LmsUsers
from auth.auth_bearer import JWTBearer, get_admin_or_teacher, get_admin_student_teacher_parent
from db.session import get_db
from ..models import Branch
from ..schemas import BranchCreate, BranchUpdate
from dotenv import load_dotenv
from sqlalchemy.orm import Session, joinedload
import os
from ..models.Students import Student



load_dotenv()
router = APIRouter()

base_url_path = os.getenv("BASE_URL_PATH")

@router.post("/branches/", response_model=None)
async def create_branch(branch_data: BranchCreate, db: Session = Depends(get_db)):
    try:
        branch = Branch(**branch_data.dict())
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to insert branch")

@router.get("/branches/get_all/", response_model=None)
async def read_all_branches(db: Session = Depends(get_db)):
    try:
        all_data=[]
        get_data=db.query(Branch).all()
        for branch in get_data:
            data={
                "id":branch.id,
                "name":branch.name,
            }
            all_data.append(data)
        return {"all_branches":all_data}
    except:
        raise HTTPException(status_code=404, detail="branch not found")
        
    
@router.get("/branches/{branch_id}", response_model=None)
async def read_branch(branch_id: int, db: Session = Depends(get_db)):
    try:
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")
        return branch
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to fetch branch")

@router.put("/branches/{branch_id}", response_model=None)
async def update_branch(branch_id: int, branch_data: BranchUpdate, db: Session = Depends(get_db)):
    try:
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")
        for key, value in branch_data.dict().items():
            setattr(branch, key, value)
        db.commit()
        db.refresh(branch)
        return branch
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to update branch")

@router.delete("/branches/{branch_id}", response_model=None)
async def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    try:
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if branch is None:
            raise HTTPException(status_code=404, detail="Branch not found")
        db.delete(branch)
        db.commit()
        return branch
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to delete batch")

#############################################################################################################################

@router.get("/admission/forSearch/{branch_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_student_teacher_parent)])
def get_user_profile(branch_id: int, db: Session = Depends(get_db)):
    try:
        # Query the Student table with joined load to load related data in a single query
        students = db.query(Student)\
                  .filter(Student.branch_id == branch_id)\
                  .options(
                      joinedload(Student.pre_education),  # Load pre-education details
                      joinedload(Student.parent_info),  # Load parent information
                      joinedload(Student.contact_info),  # Load contact information
                      joinedload(Student.course_details),  # Load course details
                      joinedload(Student.branch),  # Load branch information
                      joinedload(Student.user)  # Load related user data (LmsUsers)
                  )\
                  .all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found for this branch")

        result = []

        for student in students:
            user = student.user
            if not user:
                raise HTTPException(status_code=404, detail=f"User profile not found for student {student.id}")

            is_payment_done = user.is_payment_done

            # Construct URLs for the documents (id_proof, address_proof, profile_photo)
            id_proof_url = f"{base_url_path}/{student.id_proof}" if student.id_proof else None
            address_proof_url = f"{base_url_path}/{student.Address_proof}" if student.Address_proof else None
            profile_photo_url = f"{base_url_path}/{student.profile_photo}" if student.profile_photo else None

            # Helper function to convert IDs to names
            def convert_to_names(ids: Union[int, List[int]], get_name_func):
                if isinstance(ids, int):
                    return get_name_func(db, ids)
                elif isinstance(ids, list):
                    return [get_name_func(db, id) for id in ids]
                return None

            # Student profile data
            student_data = {
                "user_id": user.user_id,
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
                "profile_photo_url": profile_photo_url,
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

            # Fetch the latest payment details
            payment = db.query(Payment).filter(Payment.user_id == user.user_id).order_by(desc(Payment.created_on)).first()
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

            result.append(student_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch data for branch {branch_id}: {str(e)}")
    
##############################################################################################################################
def get_teachers_by_branch_id(db: Session, branch_id: int):
    query = db.query(Teacher).options(
        joinedload(Teacher.employee),
        joinedload(Teacher.contact_information),
        joinedload(Teacher.educations),
        joinedload(Teacher.dependents),
        joinedload(Teacher.emergency_contact),
        joinedload(Teacher.skills),
        joinedload(Teacher.branch),
        joinedload(Teacher.languages_spoken)
    )
    
    return query.filter(Teacher.branch_id == branch_id).all()

@router.get("/teachers/for_search/{branch_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_teachers_by_branch(branch_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch the teachers based on branch_id
        teachers = get_teachers_by_branch_id(db, branch_id)

        if not teachers:
            raise HTTPException(status_code=404, detail="No teachers found for this branch")

        result = []

        for teacher in teachers:
            # Extract related information
            employee_info = teacher.employee[0] if teacher.employee else None
            contact_info = teacher.contact_information[0] if teacher.contact_information else None
            dependent = teacher.dependents[0] if teacher.dependents else None
            education = teacher.educations[0] if teacher.educations else None
            emergency_contact = teacher.emergency_contact[0] if teacher.emergency_contact else None
            language_spoken = teacher.languages_spoken[0] if teacher.languages_spoken else None
            skill = teacher.skills[0] if teacher.skills else None

            # Construct teacher data response
            teacher_data = {
                "Teacher_id": teacher.Teacher_id,
                "user_id": teacher.user_id,
                "name": teacher.name,
                "email": teacher.email,
                "profile_photo": teacher.profile_photo,
                "branch_name": teacher.branch.name,
                "employee": {
                    "dob": employee_info.dob if employee_info else None,
                    "gender": employee_info.gender if employee_info else None,
                    "nationality": employee_info.nationality if employee_info else None,
                    "marital_status": employee_info.marital_status if employee_info else None,
                    "date_of_hire": employee_info.date_of_hire if employee_info else None,
                },
                "contact_info": {
                    "primary_number": contact_info.primary_number if contact_info else None,
                    "secondary_number": contact_info.secondary_number if contact_info else None,
                    "primary_email_id": contact_info.primary_email_id if contact_info else None,
                    "secondary_email_id": contact_info.secondary_email_id if contact_info else None,
                    "current_address": contact_info.current_address if contact_info else None,
                    "permanent_address": contact_info.permanent_address if contact_info else None
                },
                "dependent": {
                    "id": dependent.id if dependent else None,
                    "dependent_name": dependent.dependent_name if dependent else None,
                    "relation": dependent.realtion if dependent else None,
                    "date_of_birth": dependent.date_of_birth if dependent else None
                },
                "education": {
                    "id": education.id if education else None,
                    "education_level": education.education_level if education else None,
                    "institution": education.institution if education else None,
                    "specialization": education.specialization if education else None,
                    "field_of_study": education.field_of_study if education else None,
                    "year_of_passing": education.year_of_passing if education else None,
                    "percentage": education.percentage if education else None
                },
                "emergency_contact": {
                    "id": emergency_contact.id if emergency_contact else None,
                    "emergency_contact_name": emergency_contact.emergency_contact_name if emergency_contact else None,
                    "relation": emergency_contact.relation if emergency_contact else None,
                    "emergency_contact_number": emergency_contact.emergency_contact_number if emergency_contact else None
                },
                "languages_spoken": {
                    "id": language_spoken.id if language_spoken else None,
                    "languages": language_spoken.languages if language_spoken else None
                },
                "skill": {
                    "id": skill.id if skill else None,
                    "skill": skill.skill if skill else None,
                    "certification": skill.certification if skill else None,
                    "license": skill.license if skill else None
                }
            }

            result.append(teacher_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch data for branch {branch_id}: {str(e)}")



