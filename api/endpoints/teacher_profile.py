from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from fastapi import Header
from ..models import (Employee, TeacherContact, Dependents, Education, EmergencyContact,LanguagesSpoken, Skill, LmsUsers, Teacher,TeacherCourse)
from ..schemas import ( ContactInformationCreate, ContactInformationUpdate,EducationCreate, EducationUpdate, SkillCreate,SkillUpdate,
                        LanguagesSpokenCreate, LanguagesSpokenUpdate,EmergencyContactCreate, EmergencyContactUpdate,
                       DependentsCreate, DependentsUpdate, EmployeeCreate,EmployeeUpdate, TeacherCreate, TeacherUpdate, ContactInfoUpdate,TeacherUpdate1, 
                       DependentUpdate, EducationUpdate1, EmergencyContactUpdate1, LanguagesSpokenUpdate1, SkillUpdate1)
from auth.auth_bearer import JWTBearer, get_current_user, get_admin, get_admin_or_teacher
from typing import Optional
from pydantic import BaseModel
from datetime import date
from .std_profile import save_upload_file
from dotenv import load_dotenv
import re
import os
from .std_profile import validate_emails, validate_phone_number


load_dotenv()

router = APIRouter()

def get_teacher(db: Session, user_id: int):
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
    if user_id:
        return query.filter(Teacher.user_id == user_id).first()
    return query.all()

def get_teacher1(db: Session, Teacher_id: int):
    query = db.query(Teacher).options(
        joinedload(Teacher.employee),
        joinedload(Teacher.contact_information),
        joinedload(Teacher.educations),
        joinedload(Teacher.dependents),
        joinedload(Teacher.emergency_contact),
        joinedload(Teacher.skills),
        joinedload(Teacher.languages_spoken)
    )
    if Teacher_id:
        return query.filter(Teacher.Teacher_id == Teacher_id).first()
    return query.all()

def get_all_teacher( db: Session):
    return db.query(Teacher) \
        .options(joinedload(Teacher.employee),
        joinedload(Teacher.contact_information),
        joinedload(Teacher.educations),
        joinedload(Teacher.dependents),
        joinedload(Teacher.emergency_contact),
        joinedload(Teacher.skills),
        joinedload(Teacher.languages_spoken )) \
        .all()


def get_employee(db: Session,Teacher_id: int):
    return db.query(Employee).filter(Employee.Teacher_id == Teacher_id).first()

def get_teacher_contact_info(db: Session,Teacher_id: int):
    return db.query(TeacherContact).filter(TeacherContact.Teacher_id == Teacher_id).first()


def get_teacher_education(db: Session, Teacher_id: int):
    return db.query(Education).filter(Education.Teacher_id ==Teacher_id).first()


def get_teacher_depends(db: Session, Teacher_id: int):
    return db.query(Dependents).filter(Dependents.Teacher_id ==Teacher_id).first()

def get_teacher_emergency_contact(db: Session, Teacher_id: int):
    return db.query(EmergencyContact).filter(EmergencyContact.Teacher_id == Teacher_id).first()

def get_teacher_language_spoken(db: Session, Teacher_id: int):
    return db.query(LanguagesSpoken).filter(LanguagesSpoken.Teacher_id == Teacher_id).first()

def get_teacher_skills(db: Session, Teacher_id: int):
    return db.query(Skill).filter(Skill.Teacher_id == Teacher_id).first()



def update_teacher_data(db: Session, Teacher_id: int, teacher_data: TeacherUpdate):
    db_teacher_data = db.query(Teacher).filter(Teacher.Teacher_id ==Teacher_id).first()
    if db_teacher_data:
        for key, value in teacher_data.dict(exclude_unset=True).items():
            setattr(db_teacher_data, key, value)
        db.commit()
        db.refresh(db_teacher_data)
        return db_teacher_data
    else:
        raise HTTPException(status_code=404, detail="Teacher  not found")

def update_employee(db: Session, Teacher_id: int, employee_data: EmployeeUpdate):
    db_employee = db.query(Employee).filter(Employee.Teacher_id ==Teacher_id).first()
    if db_employee:
        for key, value in employee_data.dict(exclude_unset=True).items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    else:
        raise HTTPException(status_code=404, detail="Teacher  not found")


def update_teacher_contact_info(db: Session, Teacher_id: int, teacher_contact_info: ContactInformationUpdate):
    db_teacher_contact_info = db.query(TeacherContact).filter(TeacherContact.Teacher_id == Teacher_id).first()
    if  db_teacher_contact_info:
        for key, value in teacher_contact_info.dict(exclude_unset=True).items():
            setattr(db_teacher_contact_info, key, value)
        db.commit()
        db.refresh(db_teacher_contact_info)
    else:
        raise HTTPException(status_code=404, detail="Contact information not found")


def update_teacher_education(db: Session, Teacher_id: int, teacher_education: EducationUpdate):
    db_teacher_education = db.query(Education).filter(Education.Teacher_id == Teacher_id).first()
    if db_teacher_education:
        for key, value in teacher_education.dict(exclude_unset=True).items():
            setattr(db_teacher_education, key, value)
        db.commit()
        db.refresh(db_teacher_education)
    else:
        raise HTTPException(status_code=404, detail="education information not found")


def update_teacher_depends(db: Session, Teacher_id: int, teacher_depends: DependentsUpdate):
    db_teacher_depends = db.query(Dependents).filter(Dependents.Teacher_id == Teacher_id).first()
    if  db_teacher_depends:
        for key, value in teacher_depends.dict(exclude_unset=True).items():
            setattr( db_teacher_depends, key, value)
        db.commit()
        db.refresh( db_teacher_depends)
    else:
        raise HTTPException(status_code=404, detail="teacher_depends information not found")
    
def update_teacher_emergencyContact(db: Session, Teacher_id: int, teacher_emergencyContact: EmergencyContactUpdate):
    db_teacher_emergencyContact = db.query(EmergencyContact).filter(EmergencyContact.Teacher_id == Teacher_id).first()
    if  db_teacher_emergencyContact:
        for key, value in teacher_emergencyContact.dict(exclude_unset=True).items():
            setattr( db_teacher_emergencyContact, key, value)
        db.commit()
        db.refresh( db_teacher_emergencyContact)
    else:
        raise HTTPException(status_code=404, detail="teacher_emergencyContact information not found")
    
def update_teacher_LanguagesSpoken(db: Session, Teacher_id: int, teacher_LanguagesSpoken:  LanguagesSpokenUpdate):
    db_teacher_LanguagesSpoken = db.query(LanguagesSpoken).filter(LanguagesSpoken.Teacher_id == Teacher_id).first()
    if  db_teacher_LanguagesSpoken:
        for key, value in teacher_LanguagesSpoken.dict(exclude_unset=True).items():
            setattr( db_teacher_LanguagesSpoken, key, value)
        db.commit()
        db.refresh( db_teacher_LanguagesSpoken)
    else:
        raise HTTPException(status_code=404, detail="teacher_LanguagesSpoken information not found")
    
def update_skill(db: Session, Teacher_id: int, skill_update: SkillUpdate):
    db_skill = db.query(Skill).filter(Skill.Teacher_id == Teacher_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    for key, value in skill_update.dict().items():
        setattr(db_skill, key, value)
    db.commit()
    db.refresh(db_skill)
    return db_skill

base_url_path = os.getenv("BASE_URL_PATH")
@router.post("/teachers/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def fill_teacher_data(
    name: str = Form(...),
    email: str = Form(None),
    department: str = Form(None),
    profile_photo: UploadFile = File(None),
    f_name:str= Form(None),
    m_name: str = Form(None),
    l_name: str = Form(None),
    dob: date = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    marital_status: str = Form(...),
    citizenship_status: str = Form(None),
    date_of_hire: date = Form(...),
    date_of_termination: date = Form(None),
    primary_number: str = Form(...),
    secondary_number: str = Form(None),
    primary_email_id: str = Form(...),
    secondary_email_id: str = Form(None),
    current_address: str = Form(...),
    permanent_address: str = Form(...),
    dependent_name: str = Form(...),
    relation: str = Form(...),
    date_of_birth: date = Form(None),
    education_level: str = Form(...),
    institution: str = Form(...),
    specialization: str = Form(...),
    field_of_study: str = Form(...),
    year_of_passing: int = Form(...),
    percentage: float = Form(...),
    skill: str = Form(...),
    certification: str = Form(...),
    license: str = Form(None),
    emergency_contact_name: str = Form(None),
    emergency_contact_number: str = Form(...),
    languages: str = Form(...),
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    # if len(emergency_contact_number) != 10 or not emergency_contact_number.isdigit():
    #     raise HTTPException(status_code=400, detail="Emergency contact number must be 10-digit number.")
    profile_photo_url = save_upload_file(profile_photo)

    validate_phone_number(primary_number, "Primary contact number")
    validate_phone_number(emergency_contact_number, "Emergency contact number")
    validate_emails(primary_email_id)

    user_db=db.query(LmsUsers).filter(LmsUsers.user_id== current_user.user_id).first()
    if not user_db:
         raise HTTPException(status_code=404, detail="your are not correct user")

    try:
        existing_form = db.query(Teacher).filter(Teacher.user_id == current_user.user_id).first()
        if existing_form:
            raise HTTPException(status_code=400, detail="Teacher data has already been submitted")

        teacher_data = Teacher(
            user_id=current_user.user_id,
            name=name,
            email=email,
            department=department,
            profile_photo=profile_photo_url,
            branch_id=user_db.branch_id,
           
        )
        db.add(teacher_data)
        db.flush()
        db.refresh(teacher_data)

        employee_data = Employee(
            Teacher_id=teacher_data.Teacher_id,
            f_name=f_name,
            m_name=m_name,
            l_name=l_name,
            dob=dob,
            gender=gender,
            nationality=nationality,
            marital_status=marital_status,
            citizenship_status=citizenship_status,
            date_of_hire=date_of_hire,
            date_of_termination=date_of_termination,
           
        )
        db.add(employee_data)
        db.flush()

        teacher_contact_data = TeacherContact(
            Teacher_id=teacher_data.Teacher_id,
            primary_number=primary_number,
            secondary_number=secondary_number,
            primary_email_id=primary_email_id,
            secondary_email_id=secondary_email_id,
            current_address=current_address,
            permanent_address=permanent_address,
        )
        db.add(teacher_contact_data)
        db.flush()

        dependent_data = Dependents(
            Teacher_id=teacher_data.Teacher_id,
            dependent_name=dependent_name,
            realtion=relation,
            date_of_birth=date_of_birth
        )
        db.add(dependent_data)
        db.flush()

        # Create and save Education entry
        education_data = Education(
            Teacher_id=teacher_data.Teacher_id,
            education_level=education_level,
            institution=institution,
            specialization=specialization,
            field_of_study=field_of_study,
            year_of_passing=year_of_passing,
            percentage=percentage
        )
        db.add(education_data)
        db.flush()

        # Create and save Skill entry
        skill_data = Skill(
            Teacher_id=teacher_data.Teacher_id,
            skill=skill,
            certification=certification,
            license=license
        )
        db.add(skill_data)
        db.flush()

        # Create and save EmergencyContact entry
        emergency_contact_data = EmergencyContact(
            Teacher_id=teacher_data.Teacher_id,
            emergency_contact_name=emergency_contact_name,
            relation=relation,
            emergency_contact_number=emergency_contact_number
        )
        db.add(emergency_contact_data)
        db.flush()

        # Create and save LanguagesSpoken entry
        languages_spoken_data = LanguagesSpoken(
            Teacher_id=teacher_data.Teacher_id,
            languages=languages
        )
        db.add(languages_spoken_data)
        db.flush()

        current_user.user_type = 'teacher'
        current_user.is_formsubmited = True
        db.add(current_user)
        db.commit()


        return {"message": "Teacher data has been submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create teacher details{e}")



@router.get("/teachers/get_all", response_model=None,dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_all_teachers(db: Session = Depends(get_db)):
    try:
        teachers = get_all_teacher(db)
        if not teachers:
            raise HTTPException(status_code=404, detail="Teachers not found")
        
        teachers_data = []
        for teacher in teachers:
            id_proof_url = f"{base_url_path}/{teacher.profile_photo}" if teacher.profile_photo else None
            contact_info = teacher.contact_information[0] if teacher.contact_information else None
            dependent = teacher.dependents[0] if teacher.dependents else None
            education = teacher.educations[0] if teacher.educations else None
            emergency_contact = teacher.emergency_contact[0] if teacher.emergency_contact else None
            language_spoken = teacher.languages_spoken[0] if teacher.languages_spoken else None
            skill = teacher.skills[0] if teacher.skills else None
            
            teacher_data = {
                "Teacher_id": teacher.Teacher_id,
                "user_id": teacher.user_id,
                "name": teacher.name,
                "email": teacher.email,
                "profile_photo": id_proof_url,
                "contact_info": {
                    "primary_number": getattr(contact_info, 'primary_number', None),
                    "secondary_number": getattr(contact_info, 'secondary_number', None),
                    "primary_email_id": getattr(contact_info, 'primary_email_id', None),
                    "secondary_email_id": getattr(contact_info, 'secondary_email_id', None),
                    "current_address": getattr(contact_info, 'current_address', None),
                    "permanent_address": getattr(contact_info, 'permanent_address', None)
                },
                "dependent": {
                    "id": getattr(dependent, 'id', None),
                    "dependent_name": getattr(dependent, 'dependent_name', None),
                    "relation": getattr(dependent, 'realtion', None),  
                    "date_of_birth": getattr(dependent, 'date_of_birth', None)
                },
                "education": {
                    "id": getattr(education, 'id', None),
                    "education_level": getattr(education, 'education_level', None),
                    "institution": getattr(education, 'institution', None),
                    "specialization": getattr(education, 'specialization', None),
                    "field_of_study": getattr(education, 'field_of_study', None),
                    "year_of_passing": getattr(education, 'year_of_passing', None),
                    "percentage": getattr(education, 'percentage', None)
                },
                "emergency_contact": {
                    "id": getattr(emergency_contact, 'id', None),
                    "emergency_contact_name": getattr(emergency_contact, 'emergency_contact_name', None),
                    "relation": getattr(emergency_contact, 'relation', None),
                    "emergency_contact_number": getattr(emergency_contact, 'emergency_contact_number', None)
                },
                "languages_spoken": {
                    "id": getattr(language_spoken, 'id', None),
                    "languages": getattr(language_spoken, 'languages', None)
                },
                "skill": {
                    "id": getattr(skill, 'id', None),
                    "skill": getattr(skill, 'skill', None),
                    "certification": getattr(skill, 'certification', None),
                    "license": getattr(skill, 'license', None)
                }
            }
            
            teachers_data.append(teacher_data)
        
        return teachers_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch teacher details: {str(e)}")

@router.get("/teachers/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_Teacher_user_profile(user_id: int, db: Session = Depends(get_db)):
    try:
        teacher = get_teacher(db, user_id)
        
        if teacher is None:
            raise HTTPException(status_code=404, detail="Teacher not found")

        emplyee_info = teacher.employee[0] if teacher.employee else None
        contact_info = teacher.contact_information[0] if teacher.contact_information else None
        dependent = teacher.dependents[0] if teacher.dependents else None
        education = teacher.educations[0] if teacher.educations else None
        emergency_contact = teacher.emergency_contact[0] if teacher.emergency_contact else None
        language_spoken = teacher.languages_spoken[0] if teacher.languages_spoken else None
        skill = teacher.skills[0] if teacher.skills else None
        
        teacher_data = {
            "Teacher_id": teacher.Teacher_id,
            "user_id": teacher.user_id,
            "name": teacher.name,
            "email": teacher.email,
            "profile_photo": teacher.profile_photo,
            "branch_name": teacher.branch.name,
            "employee":{
                "dob" :emplyee_info.dob if emplyee_info else None,
                "gender":emplyee_info.gender if emplyee_info else None,
                "nationality" :emplyee_info.nationality if emplyee_info else None,
                "marital_status" :emplyee_info.marital_status if emplyee_info else None,
                "date_of_hire" :emplyee_info.date_of_hire if emplyee_info else None,
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
        
        return teacher_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch teacher details: {str(e)}")

def increment_content_file_count(db: Session, teacher_id: int):
    teacher = db.query(Teacher).filter(Teacher.Teacher_id == teacher_id).first()
    if teacher:
        teacher.content_file_count += 1
        db.commit()

def decrement_content_file_count(db: Session, teacher_id: int):
    teacher = db.query(Teacher).filter(Teacher.Teacher_id == teacher_id).first()
    if teacher:
        if teacher.content_file_count > 0:
            teacher.content_file_count -= 1
            db.commit()
            


@router.put("/teachers/{teacher_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def update_teacher(
    teacher_id: int,
    teacher_update_data: TeacherUpdate1,
    contact_info: ContactInfoUpdate,
    dependent: DependentUpdate,
    education: EducationUpdate1,
    emergency_contact: EmergencyContactUpdate1,
    languages_spoken: LanguagesSpokenUpdate1,
    skill: SkillUpdate1,
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        existing_teacher = db.query(Teacher).filter(Teacher.Teacher_id == teacher_id).first()
        if not existing_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        if teacher_update_data.name is not None:
            existing_teacher.name = teacher_update_data.name
        if teacher_update_data.department is not None:
            existing_teacher.department = teacher_update_data.department

        db.add(existing_teacher)

        existing_teacher_contact = db.query(TeacherContact).filter(TeacherContact.Teacher_id == teacher_id).first()
        if not existing_teacher_contact:
            existing_teacher_contact = TeacherContact(teacher_id=teacher_id)

        if contact_info.primary_number is not None:
            existing_teacher_contact.primary_number = contact_info.primary_number
        if contact_info.secondary_number is not None:
            existing_teacher_contact.secondary_number = contact_info.secondary_number
        if contact_info.primary_email_id is not None:
            existing_teacher_contact.primary_email_id = contact_info.primary_email_id
        if contact_info.secondary_email_id is not None:
            existing_teacher_contact.secondary_email_id = contact_info.secondary_email_id
        if contact_info.current_address is not None:
            existing_teacher_contact.current_address = contact_info.current_address
        if contact_info.permanent_address is not None:
            existing_teacher_contact.permanent_address = contact_info.permanent_address

        db.add(existing_teacher_contact)

        existing_dependent = db.query(Dependents).filter(Dependents.Teacher_id == teacher_id).first()
        if not existing_dependent:
            raise HTTPException(status_code=404, detail="Dependent not found")

        if dependent.dependent_name is not None:
            existing_dependent.dependent_name = dependent.dependent_name
        if dependent.relation is not None:
            existing_dependent.realtion = dependent.relation
        if dependent.date_of_birth is not None:
            existing_dependent.date_of_birth = dependent.date_of_birth

        db.add(existing_dependent)

        existing_education = db.query(Education).filter(Education.Teacher_id == teacher_id).first()
        if not existing_education:
            raise HTTPException(status_code=404, detail="Education details not found")

        if education.education_level is not None:
            existing_education.education_level = education.education_level
        if education.institution is not None:
            existing_education.institution = education.institution
        if education.specialization is not None:
            existing_education.specialization = education.specialization
        if education.field_of_study is not None:
            existing_education.field_of_study = education.field_of_study
        if education.year_of_passing is not None:
            existing_education.year_of_passing = education.year_of_passing
        if education.percentage is not None:
            existing_education.percentage = education.percentage

        db.add(existing_education)

        existing_emergency_contact = db.query(EmergencyContact).filter(EmergencyContact.Teacher_id == teacher_id).first()
        if not existing_emergency_contact:
            raise HTTPException(status_code=404, detail="Emergency contact details not found")

        if emergency_contact.emergency_contact_name is not None:
            existing_emergency_contact.emergency_contact_name = emergency_contact.emergency_contact_name
        if emergency_contact.relation is not None:
            existing_emergency_contact.relation = emergency_contact.relation
        if emergency_contact.emergency_contact_number is not None:
            existing_emergency_contact.emergency_contact_number = emergency_contact.emergency_contact_number

        db.add(existing_emergency_contact)

        existing_languages_spoken = db.query(LanguagesSpoken).filter(LanguagesSpoken.Teacher_id == teacher_id).first()
        if not existing_languages_spoken:
            raise HTTPException(status_code=404, detail="Languages spoken details not found")

        if languages_spoken.languages is not None:
            existing_languages_spoken.languages = languages_spoken.languages

        db.add(existing_languages_spoken)

        existing_skill = db.query(Skill).filter(Skill.Teacher_id == teacher_id).first()
        if not existing_skill:
            raise HTTPException(status_code=404, detail="Skills details not found")

        if skill.skill is not None:
            existing_skill.skill = skill.skill
        if skill.certification is not None:
            existing_skill.certification = skill.certification
        if skill.license is not None:
            existing_skill.license = skill.license

        db.add(existing_skill)

        db.commit()
        db.refresh(existing_teacher)

        response_data = {
            "teacher_id": existing_teacher.Teacher_id,
            "user_id":existing_teacher.user_id,
            "name": existing_teacher.name,
            "email": existing_teacher.email,
            "department": existing_teacher.department,
            "contact_info": {
                "primary_number": existing_teacher_contact.primary_number,
                "secondary_number": existing_teacher_contact.secondary_number,
                "primary_email_id": existing_teacher_contact.primary_email_id,
                "secondary_email_id": existing_teacher_contact.secondary_email_id,
                "current_address": existing_teacher_contact.current_address,
                "permanent_address": existing_teacher_contact.permanent_address
            },
            "dependent": {
                "dependent_name": existing_dependent.dependent_name,
                "relation": existing_dependent.realtion,
                "date_of_birth": existing_dependent.date_of_birth
            },
            "education": {
                "education_level": existing_education.education_level,
                "institution": existing_education.institution,
                "specialization": existing_education.specialization,
                "field_of_study": existing_education.field_of_study,
                "year_of_passing": existing_education.year_of_passing,
                "percentage": existing_education.percentage
            },
            "emergency_contact": {
                "emergency_contact_name": existing_emergency_contact.emergency_contact_name,
                "emergency_relation": existing_emergency_contact.relation,
                "emergency_contact_number": existing_emergency_contact.emergency_contact_number
            },
            "languages_spoken": {
                "languages": existing_languages_spoken.languages
            },
            "skill": {
                "skill": existing_skill.skill,
                "certification": existing_skill.certification,
                "license": existing_skill.license
            }
        }

        return response_data
    except Exception as e:
    
        raise HTTPException(status_code=500, detail=f"Failed to update teacher details: {str(e)}")

@router.delete("/teachers/{user_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_teacher(user_id: int, db: Session = Depends(get_db)):
    try:
        existing_teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if not existing_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        db.query(Employee).filter(Employee.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(TeacherContact).filter(TeacherContact.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(Education).filter(Education.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(Dependents).filter(Dependents.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(EmergencyContact).filter(EmergencyContact.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(LanguagesSpoken).filter(LanguagesSpoken.Teacher_id == existing_teacher.Teacher_id).delete()
        db.query(Skill).filter(Skill.Teacher_id == existing_teacher.Teacher_id).delete()

        db.delete(existing_teacher)
        db.commit()
        lms_user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
        if not lms_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        lms_user.user_type = 'teacher'
        lms_user.is_formsubmited = False
        db.commit()

        return {"message": "Teacher and associated data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete teacher details: {str(e)}")



@router.get("/teacher/dashboard_counts", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def get_teacher_dashboard_counts(db: Session = Depends(get_db)):
    try:
        total_teachers_from_users = db.query(LmsUsers).filter(LmsUsers.user_type == "teacher").count()
        total_employees = db.query(Teacher).count()
        total_teacher_contacts = db.query(TeacherContact).count()
        total_dependents = db.query(Dependents).count()
        total_educations = db.query(Education).count()
        total_languages_spoken = db.query(LanguagesSpoken).count()
        total_skills = db.query(Skill).count()
        total_emergency_contacts = db.query(EmergencyContact).count()

        return {
            "total_teachers_from_users": total_teachers_from_users,
            "employee_count": total_employees,
            "teacher_contact_count": total_teacher_contacts,
            "dependents_count": total_dependents,
            "education_count": total_educations,
            "languages_spoken_count": total_languages_spoken,
            "skills_count": total_skills,
            "emergency_contact_count": total_emergency_contacts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create teacher dashboard: {str(e)}")