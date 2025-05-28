from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import json
import os
from ..models.Teacher import Teacher
from ..models import Lesson
from typing import List, Optional
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Content, Module
from ..schemas import ContentCreate
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher,get_current_user
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
from pydantic import BaseModel
from sqlalchemy.orm import joinedload 
from ..models. courses_content import Course_content
import os
from dotenv import load_dotenv
from ..models import Course, TeacherCourse, LmsUsers,QuestionPaper1
from sqlalchemy import and_
from datetime import datetime
import pytz


load_dotenv()

router = APIRouter()

############################ post only content in content table #########################

@router.post("/content/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def create_content(
    name: str = Form(...),
    description: str = Form(None),
    content_type: str = Form(None),
    lesson_id: int = Form(...),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    try:
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        file_paths = []

        for upload_file in files:
            unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
            file_path = os.path.join("static", "uploads", unique_filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            file_path = file_path.replace("\\", "/")
            
            file_paths.append(file_path)
        
        db_content = Content(
            name=name,
            description=description,
            content_type=content_type,
            lesson_id=lesson_id,
            content_path=file_paths
        )

        db.add(db_content)
        db.commit()
        db.refresh(db_content)

        return {"file_paths": file_paths}  
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to insert content")

############################ post  content and lession in content and lession table #########################
class ContentResponse(BaseModel):
    id: int
    name: str
    description: str
    content_path: List[str]

    class Config:
        from_attributes = True

class LessonResponse(BaseModel):
    lesson_id: int
    title: str
    contents: List[ContentResponse]

    class Config:
        from_attributes = True

@router.post("/content/with_lesson", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def create_lesson_and_content(
    course_content_id: int = Form(...),
    lesson_title: str = Form(None),
    content_descriptions: str = Form(None),
    files: List[UploadFile] = File(None),
    current_user: LmsUsers = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.user_id).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Current user is not a teacher")
    # Check if the course content exists and is associated with an assigned course
    course_content = db.query(Course_content).join(
        Course,
        Course.id == Course_content.course_id
    ).join(
        TeacherCourse,
        and_(
            TeacherCourse.course_id == Course.id,
            TeacherCourse.is_assign_course == True
        )
    ).filter(Course_content.id == course_content_id).first()

    if not course_content:
        raise HTTPException(status_code=404, detail="No assigned course content found for the given ID")
    
    if not lesson_title:
         raise HTTPException(status_code=400, detail="Please provide lesson name")
    if not content_descriptions:
         raise HTTPException(status_code=400, detail="Please provide content descriptions")
    if not files:
         raise HTTPException(status_code=400, detail="Please upload at least one content")

    new_lesson = Lesson(
        title=lesson_title,
        course_content_id=course_content.id
    )
    db.add(new_lesson)
    db.flush()

    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    
    lesson_for_test = QuestionPaper1(
    lesson_id=new_lesson.lesson_id,
    lesson_title=lesson_title,
    course_content_id=course_content.id,
    created_by=teacher.user_id,
    created_on=ist_now
)
    db.add(lesson_for_test)
    db.commit()

    file_paths = []
    for upload_file in files:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "uploads", unique_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        file_path = file_path.replace("\\", "/")
        file_paths.append(file_path)

    new_content = Content(
        content_description=content_descriptions,
        content_path=file_paths,  
        lesson_id=new_lesson.lesson_id,
        course_content_id=course_content.id, 
        created_on=ist_now
    )
    db.add(new_content)

    db.commit()
    return {"message": "Lesson and content created successfully"}

############################### get lession and content baase on course_content_id from course_content table  #######################


def get_lessons_by_course_content(db: Session, course_content_id: int):
    return db.query(Content).options(joinedload(Content.lesson)).filter(Content.course_content_id == course_content_id).all()

@router.get("/content", response_model=None)
async def get_lessons_and_content_based_on_content_id(
    course_content_id: int,
    db: Session = Depends(get_db)
):
    course_content = db.query(Course_content).filter(Course_content.id == course_content_id).first()
    if not course_content:
        raise HTTPException(status_code=404, detail="Course content not found")
    
    contents = get_lessons_by_course_content(db, course_content_id)
    if not contents:
        raise HTTPException(status_code=404, detail="No lessons found for this course content")
    
    base_url_path = os.getenv("BASE_URL_PATH")  
    result = []
    
    for content in contents:
        
        lesson_data = {
            "lesson_id": content.lesson.lesson_id,  
            "title": content.lesson.title,   
            "course_content_id": content.lesson.course_content_id,
            "content_info": {  
                "id": content.id,
                "description": content.content_description,
                "content_path": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
            }
        }
        
        result.append(lesson_data)
    
    return result

########################################


    
@router.get("/content/get_all", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def get_all_content(db: Session = Depends(get_db)):
    try:
        contents = db.query(Content).all()
        if not contents:
            raise HTTPException(status_code=404, detail="No content found")
        
        base_url_path = os.getenv("BASE_URL_PATH")  

        all_content_data = []
        for content in contents:
            content_data = {
                "id": content.id,
                "description": content.content_description,
                "lesson_id": content.lesson_id,
                "content_paths": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
            }
            all_content_data.append(content_data)

        return JSONResponse(content=all_content_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="failed to fetch content")

@router.get("/content/{content_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def get_content_by_id(content_id: int, db: Session = Depends(get_db)):
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        base_url_path = os.getenv("BASE_URL_PATH")  

        content_data = {
            "id": content.id,
            "description": content.content_description,
            "lesson_id": content.lesson_id,
            "content_paths": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
        }

        return content_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="failed to fetch content")

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

def delete_file_from_storage(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File deleted successfully: {file_path}")
        else:
            print(f"File does not exist: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

from ..models.content import save_upload

def save_upload(files: List[UploadFile]) -> List[str]:
    file_paths = []
    try:
        for upload_file in files:
            unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
            file_path = os.path.join("static", "uploads", unique_filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            file_path = file_path.replace("\\", "/")
            file_paths.append(file_path)
        return file_paths
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

@router.put("/content/{content_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_content(
    content_id: int,
    name: str = Form(None),
    description: str = Form(None),
    content_type: str = Form(None),
    lesson_id: int = Form(...),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        db_content = db.query(Content).filter(Content.id == content_id).first()
        if not db_content:
            raise HTTPException(status_code=404, detail="Content not found")

        original_content_path_count = len(db_content.content_path)
        original_content_paths = db_content.content_path[:]

        if name is not None:
            db_content.name = name
        if description is not None:
            db_content.description = description

        if content_type is not None:
            db_content.content_type = content_type

        db_content.lesson_id = lesson_id

        if files:
            content_path_list = save_upload(files)
            db_content.content_path = content_path_list

        new_content_path_count = len(db_content.content_path)

        if new_content_path_count > original_content_path_count:
            increment_content_file_count(db, db_content.id)
        elif new_content_path_count < original_content_path_count:
            excess_files = original_content_paths[new_content_path_count:]
            for file_path in excess_files:
                delete_file_from_storage(file_path)
            db_content.content_path = db_content.content_path[:new_content_path_count]

        db.commit()
        return {"message": "Content updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="failed to update content")


@router.delete("/content/{content_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_content(content_id: int, db: Session = Depends(get_db)):
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        db.delete(content)
        db.commit()

        if content.content_path:
            for file_path in content.content_path:
                if os.path.exists(file_path):
                    os.remove(file_path)

        return {"message": "Content deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="failed to delete content")
    
