from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from fastapi import Header
from ..models.teacher_course import TeacherCourse
from ..models import Course_content
from ..models import (Employee, TeacherContact, Dependents, Education, EmergencyContact,LanguagesSpoken, Skill, LmsUsers, Teacher, Course)
from ..schemas import ( ContactInformationCreate, ContactInformationUpdate,EducationCreate, EducationUpdate, SkillCreate,SkillUpdate,
                        LanguagesSpokenCreate, LanguagesSpokenUpdate,EmergencyContactCreate, EmergencyContactUpdate,
                       DependentsCreate, DependentsUpdate, EmployeeCreate,EmployeeUpdate, TeacherCreate, TeacherUpdate)
from auth.auth_bearer import JWTBearer, get_current_user, get_admin, get_admin_or_teacher
from typing import List, Dict
from ..models.user import LmsUsers
from sqlalchemy import and_
from pydantic import BaseModel
from sqlalchemy import select

router = APIRouter()

class AssignCoursesRequest(BaseModel):
    teacher_id: int
    course_id: int
    course_content_id: int  

    class Config:
        from_attributes = True

@router.post("/teachers/assign_courses")
def assign_courses_to_teacher(
    request: AssignCoursesRequest,
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(Teacher.Teacher_id == request.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_content = (
        db.query(Course_content)
        .filter(Course_content.id == request.course_content_id)
        .first()
    )
    if not course_content:
        raise HTTPException(
            status_code=404, 
            detail="Course content not found"
        )

    existing_assignment = (
        db.query(TeacherCourse)
        .filter(
            TeacherCourse.teacher_id == request.teacher_id,
            TeacherCourse.course_id == request.course_id,
            TeacherCourse.course_content_id == request.course_content_id
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=400, 
            detail="This course is already assigned to this teacher"
        )

    try:
        teacher_course = TeacherCourse(
            teacher_id=teacher.Teacher_id,
            course_id=request.course_id,
            course_content_id=course_content.id,
            user_id=teacher.user_id,
            is_assign_course=True
        )
        
        db.add(teacher_course)

        assigned_course = {
            "course_id": request.course_id,
            "course_name": course_content.course.name,
            "course_content_id": course_content.id,
            "course_content_standard_name": course_content.standard.name,
            "course_content_subject_name": course_content.subject.name,
            "course_content_module_name": course_content.module.name,
        }

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign course to teacher: {str(e)}"
        )

    return {
        "message": "Course assigned successfully",
        "teacher_id": teacher.Teacher_id,
        "teacher_name": teacher.name,
        "assigned_course": assigned_course
    }

class CourseResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True  # T
        
@router.get("/assigned_courses", response_model=List[CourseResponse])
def get_assigned_courses(
    current_user: LmsUsers = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(LmsUsers).filter(LmsUsers.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    assigned_courses = db.query(Course).join(
        TeacherCourse, 
        and_(
            TeacherCourse.course_id == Course.id,
            TeacherCourse.user_id == current_user.user_id,
            TeacherCourse.is_assign_course == True
        )
    ).all()

    if not assigned_courses:
        raise HTTPException(status_code=404, detail="No assigned courses found for this user")

    
    return [CourseResponse.from_orm(course) for course in assigned_courses]

class TeacherCourseResponse(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str  # New field for teacher name
    course_id: int
    course_content_id: int
    user_id: int
    is_assign_course: bool
    course_name: str
    subject_name: str
    standard_name: str
    module_name: str

    class Config:
        orm_mode = True

@router.get("/teacher_assigned_courses/", response_model=List[TeacherCourseResponse],dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_all_teacher_courses(db: Session = Depends(get_db)):
    # Query to get all teacher courses with related information
    teacher_courses_query = (
        select(TeacherCourse)
        .options(
            joinedload(TeacherCourse.course_Assign)  # Load Course_content
            .joinedload(Course_content.course),      # Load Course
            joinedload(TeacherCourse.course_Assign)  # Load Course_content again for subject
            .joinedload(Course_content.subject),     # Load Subject
            joinedload(TeacherCourse.course_Assign)  # Load Course_content again for standard
            .joinedload(Course_content.standard),    # Load Standard
            joinedload(TeacherCourse.course_Assign)  # Load Course_content again for module
            .joinedload(Course_content.module),       # Load Module
            joinedload(TeacherCourse.teacher_Assign)  # Load Teacher
        )
    )

    teacher_courses = db.execute(teacher_courses_query).scalars().all()

    if not teacher_courses:
        raise HTTPException(status_code=404, detail="No teacher courses found.")

    # Prepare the response
    return [
        TeacherCourseResponse(
            id=course.id,
            teacher_id=course.teacher_id,
            teacher_name=course.teacher_Assign.name if course.teacher_Assign else None,  # Get teacher name
            course_id=course.course_id,
            course_content_id=course.course_content_id,
            user_id=course.user_id,
            is_assign_course=course.is_assign_course,
            course_name=course.course_Assign.course.name if course.course_Assign and course.course_Assign.course else None,
            subject_name=course.course_Assign.subject.name if course.course_Assign and course.course_Assign.subject else None,
            standard_name=course.course_Assign.standard.name if course.course_Assign and course.course_Assign.standard else None,
            module_name=course.course_Assign.module.name if course.course_Assign and course.course_Assign.module else None
        )
        for course in teacher_courses
    ]