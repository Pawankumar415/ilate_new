from fastapi import FastAPI, Depends, HTTPException,APIRouter, Form
from datetime import datetime
from sqlalchemy.orm import Session
from db.session import get_db
from pydantic import BaseModel
from datetime import date
from typing import List
from auth.auth_bearer import JWTBearer, get_current_user,get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student
from enum import Enum
from ..models.attendance import Attendance
from ..models.user import LmsUsers
from ..schemas import AttendanceStatus, AttendanceCreate, AttendanceResponse
import pytz
from ..models import Student
from ..models import Student,Course
from ..models import Course_content,CourseDetails
from ..models.teacher_course import TeacherCourse
import json
from pytz import timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List
from sqlalchemy import cast, Date

router = APIRouter()


class AttendanceBase(BaseModel):
    student_id: int
    course_content_id: int
    date: datetime
    status: List[str]

@router.post("/attendance/", response_model=List[AttendanceBase], dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def create_attendance(
    student_ids: str = Form(...),
    course_content_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    student_ids_list = student_ids.split(',')
    student_status_list = status.split(',')
    
    ist_now = datetime.now(timezone('Asia/Kolkata'))
    
    attendance_records = []
    
    for i, student_id in enumerate(student_ids_list):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        
        existing_attendance = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.course_content_id == course_content_id,
            cast(Attendance.date, Date) == ist_now.date()
        ).first()
        
        if existing_attendance:
            existing_attendance.status = [student_status_list[i]],
            existing_attendance.date = ist_now
        else:
            db_attendance = Attendance(
                student_id=student_id,
                course_content_id=course_content_id,
                status=[student_status_list[i]], 
                date=ist_now
            )
            db.add(db_attendance)
        
        db.commit()
        attendance_records.append(AttendanceBase(
            student_id=student_id,
            course_content_id=course_content_id,
            date=ist_now,
            status=[student_status_list[i]]
        ))
    
    return attendance_records

@router.get("/attendance/", response_model=None)
def get_attendance(
    student_ids: str,
    db: Session = Depends(get_db)
):
    student_ids_list = student_ids.split(',')
    all_records = db.query(Attendance).all()
    attendance_records = [record for record in all_records if record.student_id in student_ids_list]

    if not attendance_records:
        raise HTTPException(status_code=404, detail="No attendance records found for the provided student IDs")
    return attendance_records

# @router.get("/attendance_students/", response_model=None)
# def get_all_students(db: Session = Depends(get_db)):
#     students = db.query(Student).all()
#     return students


class StudentAttendance(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    course_name: str  

    class Config:
        orm_mode = True

@router.get("/attendance_students/", response_model=List[StudentAttendance])
def get_attendance_students(current_user: LmsUsers = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find the course_content_id for the teacher automatically
    teacher_course_content_id_query = select(
        TeacherCourse.course_content_id
    ).filter(
        TeacherCourse.user_id ==current_user.user_id
    ).distinct()

    teacher_course_content_ids = db.execute(teacher_course_content_id_query).scalars().all()

    if not teacher_course_content_ids:
        raise HTTPException(status_code=404, detail="No course content found for this teacher.")

    # Fetch students with joined loading for CourseDetails, Course_content, and Course
    result = db.query(Student).options(
        joinedload(Student.course_details).joinedload(CourseDetails.course_contents).joinedload(Course_content.course)  # Use proper join paths
    ).join(
        CourseDetails, CourseDetails.students == Student.id
    ).filter(
        CourseDetails.course_content_id.in_(teacher_course_content_ids)
    ).all()

    if not result:
        raise HTTPException(status_code=404, detail="No matching students found")

    # Return student info with the course name
    return [
        StudentAttendance(
            student_id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            course_name=student.course_details.course_contents.course.name  # Access course name through relationships
        )
        for student in result
    ]

@router.get("/attendance_students/module_wise/", response_model=List[StudentAttendance])
def get_attendance_students(course_id: int, admin_course_id: int, current_user: LmsUsers = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get course content details
    course_content = db.query(Course_content).filter(
        Course_content.id == admin_course_id,
        Course_content.course_id == course_id
    ).first()

    if not course_content:
        raise HTTPException(status_code=404, detail="Course content not found")

    # Find the course_content_id for the teacher automatically
    teacher_course_content_id_query = select(
        TeacherCourse.course_content_id
    ).filter(
        TeacherCourse.user_id == current_user.user_id
    ).distinct()

    teacher_course_content_ids = db.execute(teacher_course_content_id_query).scalars().all()

    if not teacher_course_content_ids:
        raise HTTPException(status_code=404, detail="No course content found for this teacher.")

    # Fetch students with joined loading for CourseDetails, Course_content, and Course
    result = db.query(Student).options(
        joinedload(Student.course_details).joinedload(CourseDetails.course_contents).joinedload(Course_content.course)
    ).join(
        CourseDetails, CourseDetails.students == Student.id
    ).filter(
        CourseDetails.course_content_id.in_(teacher_course_content_ids),
        CourseDetails.course_content_id == admin_course_id  # Filter by specific course content
    ).all()

    if not result:
        raise HTTPException(status_code=404, detail="No matching students found")

    # Return student info with the course name
    return [
        StudentAttendance(
            student_id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            course_name=student.course_details.course_contents.course.name  # Access course name through relationships
        )
        for student in result
   ]  

@router.put("/attendance/{attendance_id}", response_model=None)
def update_attendance(attendance_id: int, status: AttendanceStatus, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    attendance.status = status
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/attendance/")
def attendance_delete(attendance_id:int, db:Session=Depends(get_db)):
    Attendance_db=db.query(Attendance).filter(Attendance.id== attendance_id).first()
    if not Attendance_db:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(Attendance_db)
    db.commit()
    return {"detail": "Attendance deleted successfully"}