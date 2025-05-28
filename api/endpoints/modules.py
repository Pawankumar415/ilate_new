from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Module, Subject
from ..schemas import ModuleCreate, ModuleUpdate
from auth.auth_bearer import get_admin, JWTBearer
from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student

router = APIRouter()


@router.post("/modules/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def create_module(subject_id: int,module_data: ModuleCreate, db: Session = Depends(get_db)):
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="subject not found")
        module = Module(**module_data.dict(),subject_id=subject_id )
        db.add(module)
        db.commit()
        db.refresh(module)
        return module
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert module: {str(e)}")

@router.get("/modules/{module_id}", response_model=None)
async def read_module(module_id: int, db: Session = Depends(get_db)):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if module is None:
            raise HTTPException(status_code=404, detail="Module not found")
        return module
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch module: {str(e)}")

@router.get("/modules/", response_model=None)
async def read_all_modules(db: Session = Depends(get_db)):
    try:
        return db.query(Module).all()
    except Exception as e:
        raise HTTPException(status_code=404, detail="module not found")

@router.put("/modules/{module_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_module(module_id: int, module_update: ModuleUpdate, db: Session = Depends(get_db)):
    try:
        db_module = db.query(Module).filter(Module.id == module_id).first()
        if not db_module:
            raise HTTPException(status_code=404, detail="Module not found")
        if module_update.name:
            db_module.name = module_update.name
        if module_update.subject_id:
            subject = db.query(Subject).filter(Subject.id == module_update.subject_id).first()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            db_module.subject_id = module_update.subject_id
        db.commit()
        db.refresh(db_module)
        return db_module
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update module: {str(e)}")


@router.delete("/modules/{module_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_module(module_id: int, db: Session = Depends(get_db)):
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if module is None:
            raise HTTPException(status_code=404, detail="Module not found")
        db.delete(module)
        db.commit()
        return module
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete module: {str(e)}")
