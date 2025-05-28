# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request , Form
# from sqlalchemy.orm import Session
# from auth.auth_bearer import JWTBearer
# from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher
# from db.session import get_db
# from ..models import Video, Course, Subject, Standard
# from ..schemas import VideoCreate
# import os
# from typing import Optional, List
# import os
# import uuid
# import shutil
# from dotenv import load_dotenv
# from sqlalchemy.orm import Session, joinedload



# load_dotenv()
# router = APIRouter()

# # def get_course_id(course_name: str, db: Session):
# #     course = db.query(Course).filter(Course.name == course_name).first()
# #     if not course:
# #         raise HTTPException(status_code=404, detail="Course not found")
# #     return course.id

# # def get_subject_id(subject_name: str, db: Session):
# #     subject = db.query(Subject).filter(Subject.name == subject_name).first()
# #     if not subject:
# #         raise HTTPException(status_code=404, detail="Subject not found")
# #     return subject.id

# # def get_standard_id(standard_name: str, db: Session):
# #     standard = db.query(Standard).filter(Standard.name == standard_name).first()
# #     if not standard:
# #         raise HTTPException(status_code=404, detail="Standard not found")
# #     return standard.id

# # base_url_path = os.getenv("BASE_URL_PATH")


# # def save_upload_file(upload_file: UploadFile) -> str:
# #     try:
# #         unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
# #         file_path = os.path.join("static", "uploads", unique_filename)
        
# #         os.makedirs(os.path.dirname(file_path), exist_ok=True)

# #         with open(file_path, "wb") as buffer:
# #             shutil.copyfileobj(upload_file.file, buffer)
        
# #         file_path = file_path.replace("\\", "/")
# #         return file_path
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

# # @router.post("/videos/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# # def create_video(
# #     course_name:str = Form(...),
# #     subject_name: str = Form(None),
# #     standard_name: str = Form(None),
# #     name: str = Form(None),
# #     video_file: UploadFile = File(...),
# #     db: Session = Depends(get_db),
# #     token: str = Depends(JWTBearer())
# # ):
# #     try:
# #         course_id = get_course_id(course_name, db)
# #         subject_id = get_subject_id(subject_name, db)
# #         standard_id = get_standard_id(standard_name, db)

# #         file_location = save_upload_file(video_file)

# #         new_video = Video(
# #             name=name,
# #             url=file_location,
# #             course_id=course_id,
# #             standard_id=standard_id,
# #             subject_id=subject_id
# #         )

# #         db.add(new_video)
# #         db.commit()
# #         db.refresh(new_video)
# #         return new_video
    
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to insert demo video: {str(e)}")

# ###############################################################################################

# # updated by bhavan kumar
# base_url_path = os.getenv("BASE_URL_PATH")

# UPLOAD_FOLDER = "static/uploads/temp_chunks"
# FINAL_UPLOAD_FOLDER = "static/uploads/final_videos"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(FINAL_UPLOAD_FOLDER, exist_ok=True)


# def get_course_id(course_name: str, db: Session):
#     course = db.query(Course).filter(Course.name == course_name).first()
#     if not course:
#         raise HTTPException(status_code=404, detail="Course not found")
#     return course.id


# def get_subject_id(subject_name: str, db: Session):
#     subject = db.query(Subject).filter(Subject.name == subject_name).first()
#     if not subject:
#         raise HTTPException(status_code=404, detail="Subject not found")
#     return subject.id


# def get_standard_id(standard_name: str, db: Session):
#     standard = db.query(Standard).filter(Standard.name == standard_name).first()
#     if not standard:
#         raise HTTPException(status_code=404, detail="Standard not found")
#     return standard.id


# def _save_chunk_to_disk(file_chunk: UploadFile, chunk_number: int, file_name: str) -> str:
#     try:
#         unique_chunk_file_name = f"{uuid.uuid4()}_{file_name}.part.{chunk_number}"
#         chunk_path = os.path.join(UPLOAD_FOLDER, unique_chunk_file_name)
#         with open(chunk_path, "wb") as buffer:
#             shutil.copyfileobj(file_chunk.file, buffer)
#         return f"Chunk {chunk_number} saved to disk"
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving chunk {chunk_number}: {str(e)}")


# # def _merge_video_chunks(file_name: str) -> str:
# #     output_file_name = f"{uuid.uuid4()}_{file_name}"
# #     output_file_path = os.path.join(FINAL_UPLOAD_FOLDER, output_file_name)
# #     temp_file_prefix = f"_{file_name}.part."
# #     chunk_files = sorted([f for f in os.listdir(UPLOAD_FOLDER) if file_name in f and ".part." in f],
# #                          key=lambda x: int(x.split(".part.")[2]))  # Corrected sorting key
# #     try:
# #         with open(output_file_path, "wb") as output_file:
# #             for chunk_file in chunk_files:
# #                 chunk_path = os.path.join(UPLOAD_FOLDER, chunk_file)
# #                 with open(chunk_path, "rb") as chunk_file_handle:
# #                     shutil.copyfileobj(chunk_file_handle, output_file)
# #                 os.remove(chunk_path)
# #         return output_file_path.replace("\\", "/")
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error merging chunks: {str(e)}")


# @router.post("/videos/upload_chunk", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# async def upload_chunk(
#     file_chunk: UploadFile = File(...),
#     chunk_number: int = Form(...),
#     total_chunks: int = Form(...),
#     file_name: str = Form(...)
# ):
#     return _save_chunk_to_disk(file_chunk, chunk_number, file_name)


# @router.post("/videos/merge_chunks/{video_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# async def merge_chunks_update(video_id: int, db: Session = Depends(get_db)):
#     temp_upload_folder = os.path.join(UPLOAD_FOLDER, str(video_id))
#     output_file_name = f"{uuid.uuid4()}_updated_video_{video_id}"
#     output_file_path = os.path.join(FINAL_UPLOAD_FOLDER, output_file_name)
#     chunk_files = sorted([f for f in os.listdir(temp_upload_folder) if f.endswith(".part.")],
#                          key=lambda x: int(x.split(".part.")[0].split("_")[-1]))

#     try:
#         with open(output_file_path, "wb") as output_file:
#             for chunk_file in chunk_files:
#                 chunk_path = os.path.join(temp_upload_folder, chunk_file)
#                 with open(chunk_path, "rb") as chunk_file_handle:
#                     shutil.copyfileobj(chunk_file_handle, output_file)
#                 os.remove(chunk_path)
#         shutil.rmtree(temp_upload_folder)

#         final_file_url = output_file_path.replace("\\", "/")

        
#         db_video = db.query(Video).filter(Video.id == video_id).first()
#         if db_video:
#             db_video.url = final_file_url
#             db.commit()
#             db.refresh(db_video)
#             return {"file_url": final_file_url}
#         else:
#             raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error merging chunks for video ID {video_id}: {str(e)}")



# @router.post("/videos/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# async def create_video(
#     course_name: str = Form(...),
#     subject_name: str = Form(None),
#     standard_name: str = Form(None),
#     name: str = Form(None),
#     file_name: str = Form(...),
#     total_chunks: int = Form(...),
#     db: Session = Depends(get_db),
#     token: str = Depends(JWTBearer())
# ):
#     return {"message": "Initiate chunk upload", "file_name": file_name, "total_chunks": total_chunks}








# @router.get("/videos", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
# def get_all_videos(db: Session = Depends(get_db)):
#     try:
#         videos = (
#             db.query(Video)
#             .options(
#                 joinedload(Video.course),
#                 joinedload(Video.subject),
#                 joinedload(Video.standard)
#             ).all()
#         )

#         video_list = []
#         for video in videos:
#             video_url = f"{base_url_path}/{video.url}"

#             video_data = {
#                 "course_name": video.course.name,
#                 "standard_name": video.standard.name,
#                 "subject_name": video.subject.name,
#                 "name": video.name,
#                 "url": video_url,
#                 "subject_id": video.subject_id,
#                 "id": video.id,
#                 "course_id": video.course_id,
#                 "standard_id": video.standard_id
#             }
#             video_list.append(video_data)

#         return video_list
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get videos: {str(e)}")

# ##############################################################################

# def save_upload(file_path: str) -> str:
#     try:
#         unique_filename = str(uuid.uuid4()) + "_" + os.path.basename(file_path)
#         dest_path = os.path.join("static", "uploads", unique_filename)
        
#         os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
#         shutil.copyfile(file_path, dest_path)
        
#         dest_path = dest_path.replace("\\", "/")
#         return dest_path
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    

# @router.get("/videos_by_criteria/", response_model=None)
# def get_videos_by_criteria(
#     course_name: Optional[str] = None,
#     standard_id: Optional[int] = None,
#     subject_id: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     try:
#         result = {}
#         base_url_path = os.getenv("BASE_URL_PATH")
        
#         query = db.query(Video)
        
#         if not course_name:
#             courses = db.query(Course).all()
#             result["courses"] = [{"id": c.id, "name": c.name} for c in courses]
        
#         if course_name and not standard_id:
#             course = db.query(Course).filter(Course.name == course_name).first()
#             if course:
#                 standards = db.query(Standard).filter(Standard.course_id == course.id).all()
#                 result["standards"] = [{"id": s.id, "name": s.name} for s in standards]
        
#         if standard_id and not subject_id:
#             subjects = db.query(Subject).filter(Subject.standard_id == standard_id).all()
#             result["subjects"] = [{"id": s.id, "name": s.name} for s in subjects]
        
#         if subject_id:
#             query = query.filter(Video.subject_id == subject_id)
        
#         videos = query.all()
#         if not videos:
#             raise HTTPException(status_code=404, detail="Videos not found")
        
#         video_data = []
#         for video in videos:
#             video_path = save_upload(video.url)
#             video_url = f"{base_url_path}/{video_path}"
#             video_info = {
#                 "name": video.name,
#                 "url": video_url,
#             }
#             video_data.append(video_info)
        
#         result["videos"] = video_data
#         return result
    
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get demo video: {str(e)}")

# ##############################################################################

# @router.get("/videos/", response_model=None, dependencies=[Depends(JWTBearer())])
# def get_videos(course_name: str, standard_name: str, subject_name: str, db: Session = Depends(get_db)):
#     try:
#         course_id = get_course_id(course_name, db)
#         subject_id = get_subject_id(subject_name, db)
#         standard_id = get_standard_id(standard_name, db)
#     except HTTPException as e:
#         raise (f"Failed to get demo video: {str(e)}")

#     videos = db.query(Video).filter(
#         Video.course_id == course_id,
#         Video.standard_id == standard_id,
#         Video.subject_id == subject_id
#     ).all()
#     if not videos:
#         raise HTTPException(status_code=404, detail="Videos not found")

#     video_data = []
#     for video in videos:
#         video_url = f"{base_url_path}/{video.url}"  
#         video_info = {
#             "name": video.name,
#             "url": video_url,
#             "subject_id": video.subject_id,
#             "id": video.id,
#             "course_id": video.course_id,
#             "standard_id": video.standard_id
#         }
#         video_data.append(video_info)

#     return video_data



# @router.get("/videos/{video_id}", response_model=None)
# def get_video(video_id: int, request: Request, db: Session = Depends(get_db)):
#     try:
#         video = db.query(Video).filter(Video.id == video_id).first()
#         if video is None:
#             raise HTTPException(status_code=404, detail="Video not found")

#         video_url = f"{base_url_path}/{video.url}"
#         print(video_url)

#         video_data = {
#             "name": video.name,
#             "url": video_url,
#             "subject_id": video.subject_id,
#             "id": video.id,
#             "course_id": video.course_id,
#             "standard_id": video.standard_id
#         }

#         return video_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to get demo video: {str(e)}")
    


# # @router.put("/videos/{video_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# # def update_video(
# #     video_id: int,
# #     name: str,
# #     video_file: UploadFile = File(None),
# #     db: Session = Depends(get_db)
# # ):
# #     try:
# #         db_video = db.query(Video).filter(Video.id == video_id).first()
# #         if db_video is None:
# #             raise HTTPException(status_code=404, detail="Video not found")

# #         if name:
# #             db_video.name = name

# #         if video_file:
# #             file_location = save_upload_file(video_file)
# #             db_video.url = file_location

# #         subject_id = db_video.subject_id
# #         standard_id = db_video.standard_id
# #         course_id = db_video.course_id

# #         db.commit()
# #         db.refresh(db_video)

# #         return {"message": "Video and file updated successfully"}
    
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to update demo video: {str(e)}")








# @router.delete("/videos/{video_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
# def delete_video(video_id: int, db: Session = Depends(get_db)):
#     try:
#         db_video = db.query(Video).filter(Video.id == video_id).first()
#         if db_video is None:
#             raise HTTPException(status_code=404, detail="Video not found")

#         filename = db_video.url.split("/")[-1]

#         file_path = f"uploads/{filename}"

#         if os.path.exists(file_path):
#             os.remove(file_path)
#             db.delete(db_video)
#             db.commit()
#             return {"message": "Video and file deleted successfully"}
#         else:
#             db.delete(db_video)
#             db.commit()
#             return {"message": "Video deleted successfully, but file not found"}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete demo video: {str(e)}")







#########################################################################################################




from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form,Request
from sqlalchemy.orm import Session, joinedload
from auth.auth_bearer import JWTBearer, get_admin_or_teacher
from db.session import get_db
from ..models import Video, Course, Subject, Standard
import os
import uuid
import shutil
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
router = APIRouter()

UPLOAD_FOLDER = "static/uploads/temp_chunks"
FINAL_UPLOAD_FOLDER = "static/uploads/final_videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FINAL_UPLOAD_FOLDER, exist_ok=True)

base_url_path = os.getenv("BASE_URL_PATH")

def _get_course_id(course_name: str, db: Session):
    course = db.query(Course).filter(Course.name == course_name).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.id

def _get_subject_id(subject_name: str, db: Session):
    subject = db.query(Subject).filter(Subject.name == subject_name).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject.id

def _get_standard_id(standard_name: str, db: Session):
    standard = db.query(Standard).filter(Standard.name == standard_name).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    return standard.id

async def _save_chunk_to_disk(file_chunk: UploadFile, chunk_number: int, video_id: int, file_name: str):
    temp_upload_folder = os.path.join(UPLOAD_FOLDER, str(video_id))
    os.makedirs(temp_upload_folder, exist_ok=True)
    try:
        unique_chunk_file_name = f"{uuid.uuid4()}_{file_name}.part.{chunk_number}"
        chunk_path = os.path.join(temp_upload_folder, unique_chunk_file_name)
        with open(chunk_path, "wb") as buffer:
            shutil.copyfileobj(file_chunk.file, buffer)
        return {"message": f"Chunk {chunk_number} saved for video ID {video_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving chunk {chunk_number} for video ID {video_id}: {str(e)}")

async def _merge_video_chunks(video_id: int):
    temp_upload_folder = os.path.join(UPLOAD_FOLDER, str(video_id))
    output_file_name = f"{uuid.uuid4()}_merged_video_{video_id}"
    output_file_path = os.path.join(FINAL_UPLOAD_FOLDER, output_file_name)
    chunk_files = sorted([f for f in os.listdir(temp_upload_folder) if f.endswith(".part.")],
                         key=lambda x: int(x.split(".part.")[-1]))
    try:
        with open(output_file_path, "wb") as output_file:
            for chunk_file in chunk_files:
                chunk_path = os.path.join(temp_upload_folder, chunk_file)
                with open(chunk_path, "rb") as chunk_file_handle:
                    shutil.copyfileobj(chunk_file_handle, output_file)
                os.remove(chunk_path)
        shutil.rmtree(temp_upload_folder)
        return output_file_path.replace("\\", "/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging chunks for video ID {video_id}: {str(e)}")

@router.post("/videos/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def create_video(
    course_name: str = Form(...),
    subject_name: Optional[str] = Form(None),
    standard_name: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    file_name: str = Form(...),
    total_chunks: int = Form(...),
    db: Session = Depends(get_db)
):
    course_id = _get_course_id(course_name, db)
    subject_id = _get_subject_id(subject_name, db) if subject_name else None
    standard_id = _get_standard_id(standard_name, db) if standard_name else None

    new_video = Video(
        name=name,
        course_id=course_id,
        standard_id=standard_id,
        subject_id=subject_id
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    temp_upload_folder = os.path.join(UPLOAD_FOLDER, str(new_video.id))
    os.makedirs(temp_upload_folder, exist_ok=True)
    return {"video_id": new_video.id, "message": "Initiate chunk upload"}

@router.post("/videos/upload_chunk/{video_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def upload_chunk(
    video_id: int,
    file_chunk: UploadFile = File(...),
    chunk_number: int = Form(...),
    total_chunks: int = Form(...),
    file_name: str = Form(...)
):
    return await _save_chunk_to_disk(file_chunk, chunk_number, video_id, file_name)

@router.post("/videos/merge_chunks/{video_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def merge_chunks(video_id: int, db: Session = Depends(get_db)):
    final_file_url = await _merge_video_chunks(video_id)
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if db_video:
        db_video.url = final_file_url
        db.commit()
        db.refresh(db_video)
        return {"file_url": final_file_url}
    else:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")

@router.put("/videos/{video_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def update_video(
    video_id: int,
    request: Request,
    name: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None),
    subject_name: Optional[str] = Form(None),
    standard_name: Optional[str] = Form(None),
    is_chunked_update: Optional[bool] = Form(False),
    file_name: Optional[str] = Form(None),
    total_chunks: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    if name:
        db_video.name = name
    if course_name:
        db_video.course_id = _get_course_id(course_name, db)
    if subject_name:
        db_video.subject_id = _get_subject_id(subject_name, db)
    if standard_name:
        db_video.standard_id = _get_standard_id(standard_name, db)

    if is_chunked_update:
        if not file_name or not total_chunks:
            raise HTTPException(status_code=400, detail="Filename and total chunks are required for chunked update")
        temp_upload_folder = os.path.join(UPLOAD_FOLDER, str(video_id))
        os.makedirs(temp_upload_folder, exist_ok=True)
        return {"message": f"Initiate chunked update for video ID {video_id}"}
    else:
        video_file: UploadFile = await request.form().get("video_file")
        if video_file and video_file.filename:
            try:
                unique_filename = str(uuid.uuid4()) + "_" + video_file.filename
                file_path = os.path.join("static", "uploads", unique_filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(video_file.file, buffer)
                db_video.url = file_path.replace("\\", "/")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    db.commit()
    db.refresh(db_video)
    return {"message": f"Video with ID {video_id} updated successfully"}

@router.get("/videos", response_model=None, dependencies=[Depends(JWTBearer())])
def get_all_videos(db: Session = Depends(get_db)):
    videos = (
        db.query(Video)
        .options(joinedload(Video.course), joinedload(Video.subject), joinedload(Video.standard))
        .all()
    )
    video_list = []
    for video in videos:
        video_url = f"{base_url_path}/{video.url}" if video.url else None
        video_data = {
            "id": video.id,
            "name": video.name,
            "url": video_url,
            "course_id": video.course_id,
            "course_name": video.course.name,
            "standard_id": video.standard_id,
            "standard_name": video.standard.name,
            "subject_id": video.subject_id,
            "subject_name": video.subject.name if video.subject else None,
        }
        video_list.append(video_data)
    return video_list

def _save_uploaded_file(file_path: str) -> str:
    try:
        unique_filename = str(uuid.uuid4()) + "_" + os.path.basename(file_path)
        dest_path = os.path.join("static", "uploads", unique_filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copyfile(file_path, dest_path)
        return dest_path.replace("\\", "/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

@router.get("/videos_by_criteria/", response_model=None)
def get_videos_by_criteria(
    course_name: Optional[str] = None,
    standard_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    result = {}
    query = db.query(Video)

    if not course_name:
        courses = db.query(Course).all()
        result["courses"] = [{"id": c.id, "name": c.name} for c in courses]

    if course_name and not standard_id:
        course = db.query(Course).filter(Course.name == course_name).first()
        if course:
            standards = db.query(Standard).filter(Standard.course_id == course.id).all()
            result["standards"] = [{"id": s.id, "name": s.name} for s in standards]

    if standard_id and not subject_id:
        subjects = db.query(Subject).filter(Subject.standard_id == standard_id).all()
        result["subjects"] = [{"id": s.id, "name": s.name} for s in subjects]

    if subject_id:
        query = query.filter(Video.subject_id == subject_id)

    videos = query.all()
    if videos:
        video_data = []
        for video in videos:
            video_path = _save_uploaded_file(video.url) if video.url else None
            video_url = f"{base_url_path}/{video_path}" if video_path else None
            video_info = {"name": video.name, "url": video_url}
            video_data.append(video_info)
        result["videos"] = video_data
    elif course_name or standard_id or subject_id:
        raise HTTPException(status_code=404, detail="Videos not found for the given criteria")

    return result

@router.get("/videos/{video_id}", response_model=None)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    video_url = f"{base_url_path}/{video.url}" if video.url else None
    return {
        "id": video.id,
        "name": video.name,
        "url": video_url,
        "course_id": video.course_id,
        "standard_id": video.standard_id,
        "subject_id": video.subject_id,
    }

@router.delete("/videos/{video_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
def delete_video(video_id: int, db: Session = Depends(get_db)):
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    if db_video.url:
        file_path = os.path.join("static", "uploads", os.path.basename(db_video.url))
        if os.path.exists(file_path):
            os.remove(file_path)
        temp_folder_path = os.path.join(UPLOAD_FOLDER, str(video_id))
        if os.path.exists(temp_folder_path):
            shutil.rmtree(temp_folder_path)

    db.delete(db_video)
    db.commit()
    return {"message": f"Video with ID {video_id} deleted successfully"}