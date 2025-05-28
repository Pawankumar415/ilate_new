from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from auth.auth_bearer import JWTBearer, get_current_user, get_admin
from ..models import DemoFormFill, LmsUsers
from ..schemas import DemoformfillCreate
from datetime import datetime
import pytz

router = APIRouter()

@router.post("/demoformfill/", response_model=None,  dependencies=[Depends(JWTBearer())])
def create_demoformfill(demo_form: DemoformfillCreate, current_user:LmsUsers = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    try:
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_demoformfill = DemoFormFill(**demo_form.dict(), user_id=current_user.user_id)
        db_demoformfill.created_on = ist_now
        db.add(db_demoformfill)
        db.commit()
        db.refresh(db_demoformfill)
        return db_demoformfill
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert demo form: {str(e)}")

@router.get("/demoformfill/", response_model=None)
def get_all_demoformfill(db: Session = Depends(get_db)):
    try:
        demo_formfills = db.query(DemoFormFill).all()
        return demo_formfills
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch demo form : {str(e)}")


@router.get("/demoformfill{id}/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def read_demoformfill(demofill_id :int,db: Session = Depends(get_db)):
     try:
        db_demoformfill = db.query(DemoFormFill).filter(DemoFormFill.id == demofill_id).first()
        if db_demoformfill is None:

            raise HTTPException(status_code=404, detail="Demoformfill not found")
        return db_demoformfill
     except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch demo fill: {str(e)}")

@router.put("/demoformfill/{demoformfill_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def update_demoformfill(demoformfill_id: int, demo_form: DemoformfillCreate, db: Session = Depends(get_db)):
    try:
        db_demoformfill = db.query(DemoFormFill).filter(DemoFormFill.id == demoformfill_id).first()
        if db_demoformfill is None:
            raise HTTPException(status_code=404, detail="DemoFormFill not found")
        
        for attr, value in demo_form.dict().items():
            setattr(db_demoformfill, attr, value)

        db.commit()
        db.refresh(db_demoformfill)
        return db_demoformfill
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update demo fill: {str(e)}")
    
@router.delete("/demoformfill/{demoformfill_id}", dependencies=[Depends(JWTBearer()), Depends(get_admin)])
def delete_demoformfill(demoformfill_id: int, db: Session = Depends(get_db)):
    try:
        db_demoformfill = db.query(DemoFormFill).filter(DemoFormFill.id == demoformfill_id).first()
        if db_demoformfill is None:
            raise HTTPException(status_code=404, detail="DemoFormFill not found")

        db.delete(db_demoformfill)
        db.commit()
        return {"message": "DemoFormFill deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete demo fill: {str(e)}")



    


