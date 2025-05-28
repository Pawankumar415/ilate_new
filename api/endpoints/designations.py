from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Designation
from ..schemas import DesignationUpdate, DesignationCreate

router = APIRouter()

@router.get("/designations/", response_model=None)
async def read_designations(db: Session = Depends(get_db)):
    try:
        return db.query(Designation).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Designation not found")

# Get a specific designation by ID
@router.get("/designations/{designation_id}", response_model=None)
async def read_designations(designation_id: int, db: Session = Depends(get_db)):
    try:
        designation = db.query(Designation).filter(Designation.id == designation_id).first()
        if designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        return designation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch designation: {str(e)}")

# Create a new designation
@router.post("/designations/", response_model=None)
async def create_designation(designation_data: DesignationCreate, db: Session = Depends(get_db)):
    try:
        designation = Designation(**designation_data.dict())
        db.add(designation)
        db.commit()
        db.refresh(designation)
        return designation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert designation: {str(e)}")

# Update a branch by ID
@router.put("/designations/{designation_id}", response_model=None)
async def update_designation(designation_id: int, designation_data: DesignationUpdate, db: Session = Depends(get_db)):
    try:
        designation = db.query(Designation).filter(Designation.id == designation_id).first()
        if designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        for key, value in designation_data.dict().items():
            setattr(designation, key, value)
        db.commit()
        db.refresh(designation)
        return designation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update designation: {str(e)}")

# Delete a branch by ID
@router.delete("/designations/{designation_id}", response_model=None)
async def delete_designation(designation_id: int, db: Session = Depends(get_db)):
    try:
        designation = db.query(Designation).filter(Designation.id == designation_id).first()
        if designation is None:
            raise HTTPException(status_code=404, detail="Designation not found")
        db.delete(designation)
        db.commit()
        return designation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete designation: {str(e)}")
