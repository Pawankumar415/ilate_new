from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Course, Subject, Standard, Module, Lesson, Content
from ..schemas import CourseCreate, CourseUpdate, ModuleCreate1, SubjectCreate1, StandardCreate1, CourseCreateWithHierarchy1
from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher
from pydantic import BaseModel,  Field
from typing import Optional, List
from fastapi import UploadFile, File
from datetime import date
from enum import Enum
from sqlalchemy import JSON
import os
from urllib.parse import quote
import os
import uuid
import shutil
from ..models.courses_content import Course_content
from ..models.fee import Fee
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from sqlalchemy import distinct
from sqlalchemy.orm import joinedload
from datetime import datetime
from ..models.teacher_course import TeacherCourse


load_dotenv()
router = APIRouter()

###################### create course by admin with Hierarchy (course, standard, subject, module) ########################

@router.post("/courses_create/", response_model=dict, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_course_with_hierarchy(course_data: CourseCreateWithHierarchy1, db: Session = Depends(get_db)):
    course_created = 0
    standards_created = 0
    subjects_created = 0
    modules_created = 0
    course_contents_created = 0
    course_contents_updated = 0
    
    try:
        # Check if the course already exists
        existing_course = db.query(Course).filter(Course.name == course_data.course_name).first()

        if existing_course:
            course = existing_course
        else:
            course = Course(name=course_data.course_name, description=course_data.description)
            db.add(course)
            db.flush()  # Ensures that the course ID is available
            course_created += 1

        # Process standards
        for standard_data in course_data.standards:
            standard_names = [name.strip() for name in standard_data.standard_name.split(',')]
            for standard_name in standard_names:
                existing_standard = db.query(Standard).filter(
                    Standard.name == standard_name,
                    Standard.course_id == course.id
                ).first()

                if existing_standard:
                    standard = existing_standard
                else:
                    standard = Standard(name=standard_name, course_id=course.id)
                    db.add(standard)
                    db.flush()  # Ensures that the standard ID is available
                    standards_created += 1

                # Process subjects
                for subject_data in standard_data.subjects:
                    subject_names = [name.strip() for name in subject_data.subject_name.split(',')]
                    for subject_name in subject_names:
                        existing_subject = db.query(Subject).filter(
                            Subject.name == subject_name,
                            Subject.standard_id == standard.id
                        ).first()

                        if existing_subject:
                            subject = existing_subject
                        else:
                            subject = Subject(name=subject_name, standard_id=standard.id)
                            db.add(subject)
                            db.flush()  # Ensures that the subject ID is available
                            subjects_created += 1

                        # Process modules
                        for module_data in subject_data.modules:
                            module_names = [name.strip() for name in module_data.module_name.split(',')]
                            for module_name in module_names:
                                existing_module = db.query(Module).filter(
                                    Module.name == module_name,
                                    Module.subject_id == subject.id
                                ).first()

                                if existing_module:
                                    module = existing_module
                                else:
                                    module = Module(name=module_name, subject_id=subject.id)
                                    db.add(module)
                                    db.flush()  # Ensures that the module ID is available
                                    modules_created += 1

                                # Manage Course_content
                                existing_content = db.query(Course_content).filter(
                                    Course_content.course_id == course.id,
                                    Course_content.standard_id == standard.id,
                                    Course_content.subject_id == subject.id,
                                    Course_content.module_id == module.id
                                ).first()

                                if existing_content:
                                    # If the content exists, update it if needed
                                    if not existing_content.is_active:
                                        existing_content.is_active = True
                                        course_contents_updated += 1
                                else:
                                    # Create a new Course_content if it does not exist
                                    new_content = Course_content(
                                        course_id=course.id,
                                        standard_id=standard.id,
                                        subject_id=subject.id,
                                        module_id=module.id,
                                        is_active=True
                                    )
                                    db.add(new_content)
                                    course_contents_created += 1

                                db.flush()  # Ensure that changes are flushed to the database

        db.commit()

        return {
            "message": "Course hierarchy created/updated successfully",
            "course_id": course.id,
            "course_name": course.name,
            "standards_created": standards_created,
            "subjects_created": subjects_created,
            "modules_created": modules_created,
            "course_contents_created": course_contents_created,
            "course_contents_updated": course_contents_updated
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create/update course hierarchy: {str(e)}")
    
@router.get("/courses_all/", response_model=None)
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    course_list = []
    
    for course in courses:
        standards = db.query(Standard).filter(Standard.course_id == course.id).all()
        standards_list = []
        
        for standard in standards:
            subjects = db.query(Subject).filter(Subject.standard_id == standard.id).all()
            subjects_list = []
            
            for subject in subjects:
                modules = db.query(Module).filter(Module.subject_id == subject.id).all()
                modules_list = [{"module_id": module.id,"module_name": module.name} for module in modules]
                
                subjects_list.append({
                     "subject_id": subject.id,
                    "subject_name": subject.name,
                    "modules": modules_list
                })
            
            standards_list.append({
                "standard_id": standard.id,
                "standard_name": standard.name,
                "subjects": subjects_list
            })
        
        course_list.append({
             "course_id": course.id,
            "course_name": course.name,
            "standards": standards_list
        })
    
    return {"course_list": course_list}

##################### only for create standard, subject, module ##########################################

class ModuleCreate(BaseModel):
    module_name: str

class SubjectCreate(BaseModel):
    subject_name: str
    modules: List[ModuleCreate]

class StandardCreate(BaseModel):
    standard_name: str
    subjects: List[SubjectCreate]

class HierarchyCreate(BaseModel):
    standards: List[StandardCreate]
@router.post("/course/{course_id}/add_hierarchy", response_model=dict)
def add_hierarchy_to_course(course_id: int, hierarchy_data: HierarchyCreate, db: Session = Depends(get_db)):
    standards_created = 0
    subjects_created = 0
    modules_created = 0
    course_contents_created = 0

    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        for standard_data in hierarchy_data.standards:
            standard = db.query(Standard).filter(
                Standard.name == standard_data.standard_name,
                Standard.course_id == course.id
            ).first()
            if not standard:
                standard = Standard(name=standard_data.standard_name, course_id=course.id)
                db.add(standard)
                db.flush()
                standards_created += 1

            for subject_data in standard_data.subjects:
                subject = db.query(Subject).filter(
                    Subject.name == subject_data.subject_name,
                    Subject.standard_id == standard.id
                ).first()
                if not subject:
                    subject = Subject(name=subject_data.subject_name, standard_id=standard.id)
                    db.add(subject)
                    db.flush()
                    subjects_created += 1

                for module_data in subject_data.modules:
                    module = db.query(Module).filter(
                        Module.name == module_data.module_name,
                        Module.subject_id == subject.id
                    ).first()
                    if not module:
                        module = Module(name=module_data.module_name, subject_id=subject.id)
                        db.add(module)
                        db.flush()
                        modules_created += 1

                    existing_content = db.query(Course_content).filter(
                        Course_content.course_id == course.id,
                        Course_content.standard_id == standard.id,
                        Course_content.subject_id == subject.id,
                        Course_content.module_id == module.id
                    ).first()

                    if not existing_content:
                        new_content = Course_content(
                            course_id=course.id,
                            subject_id=subject.id,
                            standard_id=standard.id,
                            module_id=module.id,
                            is_active=True
                        )
                        db.add(new_content)
                        course_contents_created += 1

        db.commit()

        return {
            "message": "Hierarchy added to course successfully",
            "course_id": course.id,
            "course_name": course.name,
            "standard_name": standard.name,
            "subject_name": subject.name,
            "module_name": module.name,
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add hierarchy to course: {str(e)}")
    

################################# get hreachy from different table bsed on  deidicated course table course id ###########################################################

class RelatedCourseDetail(BaseModel):
    id: int
    standard_name: str
    subject_name: str
    module_name: str

class CourseResponse(BaseModel):
    id: int
    name: str
    description: str
    related_course_details: List[RelatedCourseDetail]

@router.get("/course/{course_id}", response_model=CourseResponse)
def get_course_hierarchy(course_id: int, db: Session = Depends(get_db)):
    # Fetch the course with its related standards, subjects, and modules
    course = db.query(Course).options(
        joinedload(Course.standards)
        .joinedload(Standard.subject)  
        .joinedload(Subject.modules)
    ).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Fetch the course contents assigned to teachers for the given course ID
    assigned_course_contents = (
        db.query(Course_content)
        .join(TeacherCourse)
        .filter(TeacherCourse.course_id == course_id)
        .filter(TeacherCourse.course_content_id == Course_content.id)
        .all()
    )
    
    # Create a mapping of course content for easy access
    content_map = {(c.standard_id, c.subject_id, c.module_id): c for c in assigned_course_contents}
    
    related_course_details = []

    for standard in course.standards:
        for subject in standard.subject:  
            for module in subject.modules:
                content = content_map.get((standard.id, subject.id, module.id))
                if content:
                    related_course_details.append(RelatedCourseDetail(
                        id=content.id,
                        standard_name=standard.name,
                        subject_name=subject.name,
                        module_name=module.name
                    ))
    
    course_response = CourseResponse(
        id=course.id,
        name=course.name,
        description=course.description,
        related_course_details=related_course_details
    )
    
    return course_response

@router.get("/course/admin/{course_id}", response_model=CourseResponse)
def get_course_hierarchy(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).options(
        joinedload(Course.standards)
        .joinedload(Standard.subject)  
        .joinedload(Subject.modules)
    ).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_contents = db.query(Course_content).filter(Course_content.course_id == course_id).all()
    content_map = {(c.standard_id, c.subject_id, c.module_id): c for c in course_contents}
    
    related_course_details = []

    for standard in course.standards:
        for subject in standard.subject:  
            for module in subject.modules:
                content = content_map.get((standard.id, subject.id, module.id))
                if content:
                    related_course_details.append(RelatedCourseDetail(
                        id=content.id,
                        standard_name=standard.name,
                        subject_name=subject.name,
                        module_name=module.name
                    ))
    
    course_response = CourseResponse(
        id=course.id,
        name=course.name,
        description=course.description,
        related_course_details=related_course_details
    )
    
    return course_response
################################# get hreachy from different course and course_content table ###########################################################

@router.get("/course/{course_id}/content/{admin_course_id}", response_model=None)
def get_course_content_detail(course_id: int, admin_course_id: int, db: Session = Depends(get_db)):

    course_content = db.query(Course_content).options(
        joinedload(Course_content.standard),
        joinedload(Course_content.subject),
        joinedload(Course_content.module)
    ).filter(
        Course_content.id == admin_course_id,
        Course_content.course_id == course_id
    ).first()

    if not course_content:
        raise HTTPException(status_code=404, detail="Course content not found")
    
    data={
        "admin_course_id":course_content.id,
        "curse_id": course_content.course_id,
        "course_name":course_content.course.name,
        "standard_name":course_content.standard.name,
        "standard_id":course_content.standard.id,
        "subject_name":course_content.subject.name,
        "subject_id":course_content.subject.id,
        "module_name":course_content.module.name,
        "module_id":course_content.module.id
    }
    
    return data
############################### get data hirarchy besed on course id from the content table course_id ###############

@router.get("/course/{course_id}/content", response_model=List[dict])
def get_course_content_detail_course_id (course_id: int, db: Session = Depends(get_db)):
    course_contents = db.query(Course_content).options(
        joinedload(Course_content.course),
        joinedload(Course_content.standard),
        joinedload(Course_content.subject),
        joinedload(Course_content.module)
    ).filter(
        Course_content.course_id == course_id
    ).all()

    if not course_contents:
        raise HTTPException(status_code=404, detail="No course content found for this course")

    data = []
    for content in course_contents:
        content_data = {
            "admin_course_id": content.id,
            "course_id": content.course_id,
            "course_name": content.course.name,
            "standard_name": content.standard.name,
            "standard_id": content.standard.id,
            "subject_name": content.subject.name,
            "subject_id": content.subject.id,
            "module_name": content.module.name,
            "module_id": content.module.id
        }
        data.append(content_data)

    return data


 #########################################################################################################################   
 
class CourseBase(BaseModel):
    name: str
    description: Optional[str]

class CourseCreate(CourseBase):
    pass

class StandardBase(BaseModel):
    name: str
    course_id: int

class StandardCreate(StandardBase):
    pass

class SubjectBase(BaseModel):
    name: str
    standard_id:int


class SubjectCreate(SubjectBase):
    pass

class ModuleBase(BaseModel):
    name: str
    subject_id:int

class ModuleCreate(ModuleBase):
    pass

class CourseCreateWithHierarchy(BaseModel):
    course: CourseCreate
    standards: List[StandardCreate]
    subjects: List[SubjectCreate]
    modules: List[ModuleCreate]
    
def build_course_hierarchy(course_id: int, db: Session) -> CourseCreateWithHierarchy:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    standards = db.query(Standard).filter(Standard.course_id == course_id).all()
    subjects = []
    for standard in standards:
        subjects.extend(db.query(Subject).filter(Subject.standard_id == standard.id).all())
    
    modules = []
    for subject in subjects:
        modules.extend(db.query(Module).filter(Module.subject_id == subject.id).all())

    course_hierarchy = CourseCreateWithHierarchy(
        course=CourseCreate(name=course.name, description=course.description),
        standards=[StandardCreate(name=standard.name, course_id=standard.course_id) for standard in standards],
        subjects=[SubjectCreate(name=subject.name, standard_id=subject.standard_id) for subject in subjects],
        modules=[ModuleCreate(name=module.name, subject_id=module.subject_id) for module in modules]
    )

    return course_hierarchy
    
###############################################################################################################################
def save_upload(file_paths: List[str]) -> List[str]:
    try:
        saved_paths = []
        for file_path in file_paths:
            unique_filename = str(uuid.uuid4()) + "_" + os.path.basename(file_path)
            dest_path = os.path.join("static", "uploads", unique_filename)
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.copyfile(file_path, dest_path)
            
            # Convert backslashes to forward slashes
            dest_path = dest_path.replace("\\", "/")
            saved_paths.append(dest_path)
        return saved_paths
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

@router.get("/filter_criteria/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_course_content_by_criteria(
    course_name: Optional[str] = None,
    standard_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    module_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        result = {}
        base_url_path = os.getenv("BASE_URL_PATH")
        query = db.query(Content)

        if not course_name:
            courses = db.query(Course).all()
            result["courses"] = [{"id": c.id, "name": c.name} for c in courses]
            return result

        course = db.query(Course).filter(Course.name == course_name).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        if course_name and not standard_id:
            standards = db.query(Standard).filter(Standard.course_id == course.id).all()
            result["standards"] = [{"id": s.id, "name": s.name} for s in standards]
            return result

        if standard_id and not subject_id:
            subjects = db.query(Subject).filter(Subject.standard_id == standard_id).all()
            result["subjects"] = [{"id": s.id, "name": s.name} for s in subjects]
            return result

        if subject_id and not module_id:
            modules = db.query(Module).filter(Module.subject_id == subject_id).all()
            result["modules"] = [{"id": m.id, "name": m.name} for m in modules]
            return result

        if module_id and not lesson_id:
            lessons = db.query(Lesson).filter(Lesson.module_id == module_id).all()
            result["lessons"] = [{"id": l.id, "name": l.name} for l in lessons]
            return result

        if lesson_id:
            query = query.filter(Content.lesson_id == lesson_id)

        content = query.all()
        if not content:
            raise HTTPException(status_code=404, detail="No content found with the given criteria")

        content_data = []
        for c in content:
            paths_to_save = c.content_path.split(',') if c.content_path else []

            saved_paths = save_upload(paths_to_save)

            url_paths = [f"{base_url_path}/{os.path.basename(path)}" for path in saved_paths]

            content_data.append({
                "name": c.name,
                "description": c.description,
                "content_type": c.content_type,
                "content_paths": url_paths  
            })

        return content_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
######################################################################################################################################################

@router.get("/courses_hierarchy/{course_id}", response_model=CourseCreateWithHierarchy, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_course_hierarchy(course_id: int, db: Session = Depends(get_db)):
    try:
        course = db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        standards = db.query(Standard).filter(Standard.course_id == course_id).all()

        subjects = []
        for standard in standards:
            subjects.extend(db.query(Subject).filter(Subject.standard_id == standard.id).all())

        modules = []
        for subject in subjects:
            modules.extend(db.query(Module).filter(Module.subject_id == subject.id).all())
        course_hierarchy = CourseCreateWithHierarchy(
            course={
                "name": course.name,
                "description": course.description
            },
            standards=[{
                "name": standard.name,
                "course_id": standard.course_id
            } for standard in standards],
            subjects=[{
                "name": subject.name,
                "standard_id": subject.standard_id
            } for subject in subjects],
            modules=[{
                "name": module.name,
                "subject_id": module.subject_id
            } for module in modules]
        )

        return course_hierarchy

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve course hierarchy: {str(e)}")

@router.get("/courses_hierarchy", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def get_all_courses_hierarchy(db: Session = Depends(get_db)):
    try:
        courses = db.query(Course).all()
        all_courses_hierarchy = []
        for course in courses:
            course_hierarchy = get_course_hierarchy(course.id, db)
            all_courses_hierarchy.append(course_hierarchy)
        return all_courses_hierarchy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve all courses hierarchy: {str(e)}")
    


@router.delete("/courses_delete/{course_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_course_with_hierarchy(course_id: int, db: Session = Depends(get_db)):
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        content_paths = db.query(Content.content_path).filter(Content.lesson_id == course_id).all()
        content_paths = [path for path, in content_paths]

        
        db.delete(course)
        db.commit()

        for path in content_paths:
            if os.path.exists(path):
                os.remove(path)

        return {"message": "Course hierarchy deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete course hierarchy: {str(e)}")




    
    
##############################################################################################################################
@router.post("/courses/", response_model=None,
             dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    try:
        db_course = Course(**course.model_dump())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create course")
    
@router.get("/courses/", response_model=None)
def read_all_courses(db: Session = Depends(get_db)):
    try:
        return db.query(Course).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch courses")


@router.get("/courses/unique", response_model=None)
def read_all_courses(db: Session = Depends(get_db)):
    try:
        # Query distinct courses by name, id, and description
        unique_courses = db.query(Course.id, Course.name, Course.description).distinct(Course.name).all()

        # Map each course into a dictionary with the required fields
        courses_list = [{"id": course.id, "name": course.name} for course in unique_courses]

        return courses_list
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch courses")

@router.get("/courses/{course_id}", response_model=None)
def read_course(course_id: int, db: Session = Depends(get_db)):
    try:
        db_course = db.query(Course).filter(Course.id == course_id).first()
        if db_course is None:
            raise HTTPException(status_code=404, detail="Course not found")
        return db_course
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch course")


@router.put("/courses/{course_id}", response_model=None,
            dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    try:
        db_course = db.query(Course).filter(Course.id == course_id).first()
        if db_course is None:
            raise HTTPException(status_code=404, detail="Course not found")
        db_course.name = course.name
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update course")


@router.delete("/courses/{course_id}", response_model=None,
               dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    try:
        db_course = db.query(Course).filter(Course.id == course_id).first()
        if db_course is None:
            raise HTTPException(status_code=404, detail="Course not found")
        db.delete(db_course)
        db.commit()
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete course")
    
