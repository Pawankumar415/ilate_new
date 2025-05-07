from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import UserType
from ..schemas import UserTypeCreate, UserTypeUpdate

router = APIRouter()

@router.get("/usertypes/", response_model=None)
async def read_usertypes(db: Session = Depends(get_db)):
    try:
        return db.query(UserType).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="user type not found")

@router.get("/usertypes/{usertype_id}", response_model=None)
async def read_usertype(usertype_id: int, db: Session = Depends(get_db)):
    try:
        usertype = db.query(UserType).filter(UserType.id == usertype_id).first()
        if usertype is None:
            raise HTTPException(status_code=404, detail="User type not found")
        return usertype
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch usertype: {str(e)}")
 
@router.post("/usertypes/", response_model=None)
async def create_usertype(usertype_data: UserTypeCreate, db: Session = Depends(get_db)):
    try:
        usertype = UserType(**usertype_data.dict())
        db.add(usertype)
        db.commit()
        db.refresh(usertype)
        return usertype
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create usertype: {str(e)}")

@router.put("/usertypes/{usertype_id}", response_model=None)
async def update_usertype(usertype_id: int, usertype_data: UserTypeUpdate, db: Session = Depends(get_db)):
    try:
        usertype = db.query(UserType).filter(UserType.id == usertype_id).first()
        if usertype is None:
            raise HTTPException(status_code=404, detail="User type not found")
        for key, value in usertype_data.dict().items():
            setattr(usertype, key, value)
        db.commit()
        db.refresh(usertype)
        return usertype
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update usertype: {str(e)}")

@router.delete("/usertypes/{usertype_id}", response_model=None)
async def delete_usertype(usertype_id: int, db: Session = Depends(get_db)):
    try:
        usertype = db.query(UserType).filter(UserType.id == usertype_id).first()
        if usertype is None:
            raise HTTPException(status_code=404, detail="User type not found")
        db.delete(usertype)
        db.commit()
        return usertype
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete usertype: {str(e)}")
