from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Lesson
from pydantic import BaseModel, Field
from ..schemas import LessonCreate, LessonResponse
from ..models.module import Module
from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student

router = APIRouter()

@router.post("/lessons/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def create_lesson(module_id: int, lesson: LessonCreate, db: Session = Depends(get_db)):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        db_lesson = Lesson(**lesson.dict(), module_id=module_id)
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert lesson: {str(e)}")

@router.get("/lessons/get_all_lessons/", response_model=None,dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def read_lessons(db: Session = Depends(get_db)):
    try:
        lessons = db.query(Lesson).all()
        return lessons
    except Exception as e:
        raise HTTPException(status_code=404, detail="lesson not found")

@router.get("/lessons/{lesson_id}", response_model=LessonResponse, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    try:
        db_lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if db_lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return db_lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/lessons/{lesson_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def update_lesson(lesson_id: int, lesson: LessonCreate, db: Session = Depends(get_db)):
    try:
        db_lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if db_lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        for key, value in lesson.dict().items():
            setattr(db_lesson, key, value)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update lesson: {str(e)}")

@router.delete("/lessons/{lesson_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    try:
        db_lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if db_lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        db.delete(db_lesson)
        db.commit()
        return {"message": "Lesson deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete lesson: {str(e)}")
