from ..models.proof import Image, save_image_to_db, get_image_by_user_id,update_image_in_db, delete_image_from_db
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from ..schemas import ImageResponse
from pydantic import BaseModel, Field
from db.session import get_db
from typing import List, Optional
import shutil
import uuid
import os



router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        #ID and Address proof
# ------------------------------------------------------------------------------------------------------------------
    
@router.post("/proof", response_model=ImageResponse)
async def upload_proof(
    user_id: int,
    id_prof: UploadFile = File(default=None),
    Address_prof: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    unique_id_prof_filename = None
    unique_address_prof_filename = None

    if id_prof:
        unique_id_prof_filename = str(uuid.uuid4()) + "_" + id_prof.filename
        id_prof_file_path = os.path.join("uploads", unique_id_prof_filename)
    
    if Address_prof:
        unique_address_prof_filename = str(uuid.uuid4()) + "_" + Address_prof.filename
        Address_prof_file_path = os.path.join("uploads", unique_address_prof_filename)
    
    try:
        if id_prof:
            with open(id_prof_file_path, "wb") as buffer:
                shutil.copyfileobj(id_prof.file, buffer)
        
        if Address_prof:
            with open(Address_prof_file_path, "wb") as buffer:
                shutil.copyfileobj(Address_prof.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create prrof_id: {str(e)}")
    
    db_image = save_image_to_db(db, user_id, id_prof=unique_id_prof_filename, Address_prof=unique_address_prof_filename)
    return db_image


@router.get("/proof/{user_id}", response_model=ImageResponse)
async def get_image(user_id: int, db: Session = Depends(get_db)):
    try:
        db_image = get_image_by_user_id(user_id, db)
        if db_image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return ImageResponse(user_id=db_image.user_id, id_prof=db_image.id_prof, Address_prof=db_image.Address_prof)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prrof_id: {str(e)}")

@router.put("/proof/{user_id}")
async def update_image(
    user_id: int,
    id_prof: UploadFile = File(None),
    Address_prof: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        return update_image_in_db(db, user_id, id_prof, Address_prof)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update prrof_id: {str(e)}")

@router.delete("/proof/{user_id}")
async def delete_image(user_id: int, db: Session = Depends(get_db)):
    try:
        return delete_image_from_db(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete prrof_id: {str(e)}")
