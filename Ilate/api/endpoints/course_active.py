from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from ..models.payment import Payment
from ..models import Student, Course, LmsUsers, Batch,Module,Standard,Subject
from pydantic import BaseModel
from ..schemas import PaymentCreate,PaymentResponse
from auth.auth_bearer import JWTBearer, get_current_user,get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student
from ..models import Student, ContactInformation, PreEducation, Parent, LmsUsers, Inquiry, DemoFormFill, CourseDetails,Course, Standard, module,Subject, Module, Payment
from typing import List
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, Dict
import pytz
from sqlalchemy import desc, func
from api.models import CourseDetails, Content, LmsUsers, Course_content, Lesson
from typing import List
from pydantic import BaseModel
from sqlalchemy import and_
import os
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

base_url_path = os.getenv("BASE_URL_PATH")  

############################ student get course only after admin payment verify ###############################

def get_user_contents(db: Session, user_id: int):
    contents_query = db.query(Content).join(
        CourseDetails,
        and_(
            Content.course_content_id == CourseDetails.course_content_id,
            CourseDetails.user_id == user_id,
            CourseDetails.is_active_course == True
        )
    ).options(
        joinedload(Content.lesson),
        joinedload(Content.course_contents).joinedload(Course_content.course),
        joinedload(Content.course_contents).joinedload(Course_content.subject),
        joinedload(Content.course_contents).joinedload(Course_content.standard),
        joinedload(Content.course_contents).joinedload(Course_content.module)
    )

    contents = contents_query.all()

    # If no contents found, query course details to return those
    if not contents:
        courses_query = db.query(CourseDetails).filter(
            CourseDetails.user_id == user_id,
            CourseDetails.is_active_course == True
        ).options(
            joinedload(CourseDetails.course),
            joinedload(CourseDetails.subject),
            joinedload(CourseDetails.standard),
            joinedload(CourseDetails.module)
        )

        courses = courses_query.all()

        if not courses:
            raise HTTPException(status_code=404, detail="No active courses found for this user.")

        # Format response with course details but no content
        response = []
        for course_detail in courses:
            response.append({
                "course_info": {
                    "course_name": course_detail.course.name if course_detail.course else None,
                    "subject_name": course_detail.subject.name if course_detail.subject else None,
                    "standard_name": course_detail.standard.name if course_detail.standard else None,
                    "module_name": course_detail.module.name if course_detail.module else None,
                },
                "lessons": []  # No lessons available
            })

        return response

    # Create the result dictionary when content is available
    result = {}

    for content in contents:
        course_data = content.course_contents.course
        subject_data = content.course_contents.subject
        standard_data = content.course_contents.standard
        module_data = content.course_contents.module

        # Create a unique identifier for each course by combining the key elements
        course_key = (course_data.name, subject_data.name, standard_data.name, module_data.name)

        # Initialize course entry if it doesn't exist in the result dictionary
        if course_key not in result:
            result[course_key] = {
                "course_info": {
                    "course_name": course_data.name if course_data else None,
                    "subject_name": subject_data.name if subject_data else None,
                    "standard_name": standard_data.name if standard_data else None,
                    "module_name": module_data.name if module_data else None,
                },
                "lessons": []
            }

        # Add the lesson data under the appropriate course
        lesson_data = {
            "lesson_id": content.lesson.lesson_id,
            "title": content.lesson.title,
            "course_content_id": content.lesson.course_content_id,
            "content_info": {
                "id": content.id,
                "description": content.content_description,
                "content_path": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None,
                "created_on":content.created_on 
            }
        }
        result[course_key]["lessons"].append(lesson_data)

    # Convert the dictionary back to a list to match the response model
    response = []
    for course_key, course_data in result.items():
        response.append(course_data)

    return response


@router.get("/course_active/enlrolled_course", response_model=List[dict])
def get_user_contents_endpoint(current_user: LmsUsers = Depends(get_current_user), db: Session = Depends(get_db)):
    contents = get_user_contents(db, current_user.user_id)
    return contents


##################################### get content based on  course_content_id from the content table  ##############################

@router.get("/course_contents/{content_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_course_content_by_id(content_id: int, db: Session = Depends(get_db)):
    try:
        course_content = db.query(Course_content).filter(Course_content.id == content_id).first()
        
        if not course_content:
            raise HTTPException(status_code=404, detail="Course content not found")

        contents_query = db.query(Content).filter(
            Content.course_content_id == content_id
        ).options(joinedload(Content.lesson))

        contents = contents_query.all()

        if not contents:
            raise HTTPException(status_code=404, detail="No content found for this course content.")

        result = {
            "id": course_content.id,
            "course_name": course_content.course.name,
            "subject_name": course_content.subject.name,
            "standard_name": course_content.standard.name,
            "module_name": course_content.module.name,
            "is_active": course_content.is_active,
            "lessons": []
        }

        for content in contents:
            lesson_data = {
                "lesson_id": content.lesson.lesson_id,
                "title": content.lesson.title,
                "content_info": {
                    "id": content.id,
                    "description": content.content_description,
                    "content_path": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
                }
            }
            
            # Check if the lesson is already in the result (generator)
            existing_lesson = next((l for l in result["lessons"] if l["lesson_id"] == lesson_data["lesson_id"]), None)
            if existing_lesson:
                existing_lesson["content_info"].append(lesson_data["content_info"])
            else:
                lesson_data["content_info"] = [lesson_data["content_info"]]
                result["lessons"].append(lesson_data)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve course content: {str(e)}")
##################################### get content based on  course_content_id from the content table  ##############################

@router.get("/course_contents/{content_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_course_content_by_id(content_id: int, db: Session = Depends(get_db)):
    try:
        course_content = db.query(Course_content).filter(Course_content.id == content_id).first()
        
        if not course_content:
            raise HTTPException(status_code=404, detail="Course content not found")

        contents_query = db.query(Content).filter(
            Content.course_content_id == content_id
        ).options(joinedload(Content.lesson))

        contents = contents_query.all()

        if not contents:
            raise HTTPException(status_code=404, detail="No content found for this course content.")

        result = {
            "id": course_content.id,
            "course_name": course_content.course.name,
            "subject_name": course_content.subject.name,
            "standard_name": course_content.standard.name,
            "module_name": course_content.module.name,
            "is_active": course_content.is_active,
            "lessons": []
        }

        for content in contents:
            lesson_data = {
                "lesson_id": content.lesson.lesson_id,
                "title": content.lesson.title,
                "content_info": {
                    "id": content.id,
                    "description": content.content_description,
                    "content_path": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
                }
            }
            
            # Check if the lesson is already in the result (generator)
            existing_lesson = next((l for l in result["lessons"] if l["lesson_id"] == lesson_data["lesson_id"]), None)
            if existing_lesson:
                existing_lesson["content_info"].append(lesson_data["content_info"])
            else:
                lesson_data["content_info"] = [lesson_data["content_info"]]
                result["lessons"].append(lesson_data)

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve course content: {str(e)}")
    
############################### get only lession and content baase on course_content_id from course_content table  #######################

def get_lessons_by_course_content(db: Session, course_content_id: int):
    return db.query(Content).options(joinedload(Content.lesson)).filter(Content.course_content_id == course_content_id).all()

@router.get("/course_contents", response_model=None)
async def get_lessons_and_content_based_on_content_id(
    course_content_id: int,
    db: Session = Depends(get_db)
):
    # Check if the course content exists
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

######################### based on course_id, subject_id , standard_id, module_id get lession & content ######################################

@router.get("/course_content_lesson/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_course_content(
    course_id: int = None,
    subject_id: int = None,
    standard_id: int = None,
    module_id: int = None,
    #is_active: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course_content)
    
    if course_id:
        query = query.filter(Course_content.course_id == course_id)
    if subject_id:
        query = query.filter(Course_content.subject_id == subject_id)
    if standard_id:
        query = query.filter(Course_content.standard_id == standard_id)
    if module_id:
        query = query.filter(Course_content.module_id == module_id)
    
    results = query.all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching course content found")
    
    final_results = []
    for result in results:
        course = db.query(Course).filter(Course.id == result.course_id).first()
        subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
        standard = db.query(Standard).filter(Standard.id == result.standard_id).first()
        module = db.query(Module).filter(Module.id == result.module_id).first()
        
        contents_query = db.query(Content).filter(
            Content.course_content_id == result.id
        ).options(joinedload(Content.lesson))
        
        contents = contents_query.all()
        
        course_content_data = {
            "id": result.id,
            "course_name": course.name if course else None,
            "subject_name": subject.name if subject else None,
            "standard_name": standard.name if standard else None,
            "module_name": module.name if module else None,
            "is_active": result.is_active,
            "lessons": []
        }
        
        for content in contents:
            lesson_data = {
                "lesson_id": content.lesson.lesson_id,
                "title": content.lesson.title,
                "content_info": {
                    "id": content.id,
                    "description": content.content_description,
                    "content_path": [f"{base_url_path}/{path}" for path in content.content_path] if content.content_path else None
                }
            }
            
            # Check if the lesson is already in the result
            existing_lesson = next((l for l in course_content_data["lessons"] if l["lesson_id"] == lesson_data["lesson_id"]), None)
            if existing_lesson:
                existing_lesson["content_info"].append(lesson_data["content_info"])
            else:
                lesson_data["content_info"] = [lesson_data["content_info"]]
                course_content_data["lessons"].append(lesson_data)
        
        final_results.append(course_content_data)
    
    return final_results

################################ update lesson and content by admin & teacher ##################################
class ContentInfoUpdate(BaseModel):
    id: int
    description: Optional[str]
    content_path: Optional[List[str]]

class LessonUpdate(BaseModel):
    lesson_id: int
    title: Optional[str]
    content_info: List[ContentInfoUpdate]

class CourseContentUpdate(BaseModel):
    course_name: Optional[str]
    subject_name: Optional[str]
    standard_name: Optional[str]
    module_name: Optional[str]
    is_active: Optional[bool]
    lessons: List[LessonUpdate]

@router.put("/course_contents/{content_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def update_course_content(content_id: int, update_data: CourseContentUpdate, db: Session = Depends(get_db)):
    try:
        course_content = db.query(Course_content).filter(Course_content.id == content_id).first()

        if not course_content:
            raise HTTPException(status_code=404, detail="Course content not found")

        if update_data.course_name is not None:
            course_content.course.name = update_data.course_name
        if update_data.subject_name is not None:
            course_content.subject.name = update_data.subject_name
        if update_data.standard_name is not None:
            course_content.standard.name = update_data.standard_name
        if update_data.module_name is not None:
            course_content.module.name = update_data.module_name
        if update_data.is_active is not None:
            course_content.is_active = update_data.is_active

        for lesson_update in update_data.lessons:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_update.lesson_id).first()
            if not lesson:
                raise HTTPException(status_code=404, detail=f"Lesson with id {lesson_update.lesson_id} not found")

            if lesson_update.title is not None:
                lesson.title = lesson_update.title

            for content_info in lesson_update.content_info:
                content = db.query(Content).filter(Content.id == content_info.id).first()
                if not content:
                    raise HTTPException(status_code=404, detail=f"Content with id {content_info.id} not found")

                if content_info.description is not None:
                    content.content_description = content_info.description
                if content_info.content_path is not None:
                    content.content_path = content_info.content_path

        db.commit()

        return {"message": f"Course content with id {content_id} has been updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update course content: {str(e)}")
    
################  delete content and lesson  by admin & teacher #########################################################

@router.delete("/content_lesson/{lesson_id}" , dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def delete_content_lesson(lesson_id: int, db: Session = Depends(get_db)):
    try:
        db_lesson = db.query(Lesson).options(joinedload(Lesson.content)).filter(Lesson.lesson_id == lesson_id).first()
        
        if db_lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        for content in db_lesson.content:
            db.delete(content)
        
        db.delete(db_lesson)
        db.commit()
        
        return {"message": f"Lesson with id {lesson_id} and its content have been deleted"}
    
    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

############ get couse content deatils  from course content tables ####################

@router.get("/course_content/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def get_course_content(
    course_id: int = None,
    subject_id: int = None,
    standard_id: int = None,
    module_id: int = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course_content)
    
    if course_id:
        query = query.filter(Course_content.course_id == course_id)
    if subject_id:
        query = query.filter(Course_content.subject_id == subject_id)
    if standard_id:
        query = query.filter(Course_content.standard_id == standard_id)
    if module_id:
        query = query.filter(Course_content.module_id == module_id)
    if is_active is not None:
        query = query.filter(Course_content.is_active == is_active)
    
    results = query.all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching course content found")
    
    for result in results:
        if result.course_id:
            course = db.query(Course).filter(Course.id == result.course_id).first()
            result.course_name = course.name if course else None
        
        if result.subject_id:
            subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
            result.subject_name = subject.name if subject else None
        
        if result.standard_id:
            standard = db.query(Standard).filter(Standard.id == result.standard_id).first()
            result.standard_name = standard.name if standard else None
        
        if result.module_id:
            module = db.query(Module).filter(Module.id == result.module_id).first()
            result.module_name = module.name if module else None
    
    return results

