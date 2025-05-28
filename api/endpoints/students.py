from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Student
from ..schemas import StudentCreate, StudentUpdate
from pydantic import BaseModel
from typing import Optional
from datetime import date
from ..schemas import StudentSchema, StudentGetResponse
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from ..models.Students import save_upload
from ..models.user import LmsUsers
import shutil
import uuid
import os




router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        #Students
# ------------------------------------------------------------------------------------------------------------------

@router.post("/students/", response_model=None)
async def create_student(
    user_id: int = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    date_of_joining: date = Form(...),
    date_of_completion: date = Form(None),
    id_proof: UploadFile = File(default=None),
    Address_proof: UploadFile = File(default=None),  
    db: Session = Depends(get_db)
):
    try:
        id_proof_path = save_upload(id_proof) if id_proof else None
        address_proof_path = save_upload(Address_proof) if Address_proof else None

        user = db.query(LmsUsers).filter(LmsUsers. user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        student = Student(
            user_id= user.user_id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            nationality=nationality,
            date_of_joining=date_of_joining,
            date_of_completion=date_of_completion,
            id_proof=id_proof_path,
            Address_proof=address_proof_path  
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student details: {str(e)}")

@router.get("/students/{student_id}", response_model=None)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student details: {str(e)}")


@router.put("/students/{student_id}", response_model=None)
async def update_student(
    student_id: int,
    user_id: int = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    nationality: str = Form(...),
    date_of_joining: date = Form(...),
    date_of_completion: date = Form(None),
    id_proof: UploadFile = File(default=None),
    Address_proof: UploadFile = File(default=None),  
    db: Session = Depends(get_db)
):
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if user_id:
            user = db.query(LmsUsers).filter(LmsUsers.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            student.user_id = user_id
        if first_name:
            student.first_name = first_name
        if middle_name:
            student.middle_name = middle_name
        if last_name:
            student.last_name = last_name
        if date_of_birth:
            student.date_of_birth = date_of_birth
        if gender:
            student.gender = gender
        if nationality:
            student.nationality = nationality
        if date_of_joining:
            student.date_of_joining = date_of_joining
        if date_of_completion:
            student.date_of_completion = date_of_completion

        if id_proof:
            id_proof_path = save_upload(id_proof)
            student.id_proof = id_proof_path
        if Address_proof:
            Address_proof_path = save_upload(Address_proof)
            student.Address_proof = Address_proof_path

        db.commit()

        return {"message": "Student updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update student details: {str(e)}")


@router.delete("/students/{student_id}", response_model=None)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        db.delete(student)
        db.commit()

        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete student details: {str(e)}")
