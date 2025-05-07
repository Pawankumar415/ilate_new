from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from auth.auth_bearer import JWTBearer, get_admin,get_admin_student_teacher_parent
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
from ..models.announcement import Announcement
from typing import Optional
from datetime import datetime
import pytz
import re
from dotenv import load_dotenv


load_dotenv()
router = APIRouter()

def save_upload_file(upload_file: Optional[UploadFile]) -> Optional[str]:
    if not upload_file:
        return None
    
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "uploads", unique_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Convert backslashes to forward slashes
        file_path = file_path.replace("\\", "/")
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

@router.post("/announcement/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def create_content(
    title: str = Form(...),
    announcement_text: str = Form(None),
    announcement_images: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    announcement_images_path = save_upload_file(announcement_images)
    try:
        db_announcement = Announcement(
            title=title,
            announcement_text=announcement_text,
            announcement_images=announcement_images_path
        )
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_announcement.created_on = ist_now
        db.add(db_announcement)
        db.commit()
        db.refresh(db_announcement)
        return db_announcement 
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to insert an announcement")

@router.get("/announcement/{announcement_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_student_teacher_parent)])
async def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")

        base_url_path = os.getenv("BASE_URL_PATH")  

        announcement_images_path = announcement.announcement_images
        if announcement_images_path:
            announcement_images_url = f"{base_url_path}/{announcement_images_path}"
        else:
            announcement_images_url = None

        announcement_response = Announcement(
            id=announcement.id,
            title=announcement.title,
            announcement_text=announcement.announcement_text,
            announcement_images=announcement_images_url
        )

        return announcement_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to fetch an announcement")
    
@router.get("/announcements", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_student_teacher_parent)])
async def get_all_announcements(db: Session = Depends(get_db)):
    try:
        announcements = db.query(Announcement).all()
        if not announcements:
            raise HTTPException(status_code=404, detail="No announcements found")

        base_url_path = os.getenv("BASE_URL_PATH")  

        announcements_response = []
        for announcement in announcements:
            announcement_images_path = announcement.announcement_images
            if announcement_images_path:
                announcement_images_url = f"{base_url_path}/{announcement_images_path}"
            else:
                announcement_images_url = None

            announcement_response = {
                "id": announcement.id,
                "title": announcement.title,
                "announcement_text": announcement.announcement_text,
                "announcement_images": announcement_images_url,
                "created_on": announcement.created_on
            }
            announcements_response.append(announcement_response)

        return announcements_response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch announcements")

@router.put("/announcement/{announcement_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_announcement(
    announcement_id: int,
    title: str = Form(None),
    announcement_text: str = Form(None),
    announcement_images: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    announcement_images_path = announcement.announcement_images
    if announcement_images:
        announcement_images_path = save_upload_file(announcement_images)

    try:
        if title is not None:
            announcement.title = title
        if announcement_text is not None:
            announcement.announcement_text = announcement_text
        if announcement_images_path:
            announcement.announcement_images = announcement_images_path

        db.commit()
        db.refresh(announcement)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update announcement: {str(e)}")

    base_url_path = os.getenv("BASE_URL_PATH") 
    announcement_images_url = f"{base_url_path}/{announcement.announcement_images}" if announcement.announcement_images else None

    return {
        "id": announcement.id,
        "title": announcement.title,
        "announcement_text": announcement.announcement_text,
        "announcement_images": announcement_images_url
    }

@router.delete("/announcement/{announcement_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    try:
        db.delete(announcement)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=" failed to delete an announcement")

    return {"message": "Announcement deleted successfully"}