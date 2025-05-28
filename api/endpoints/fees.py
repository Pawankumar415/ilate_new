from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from ..models import Fee, Course, Standard, Subject, Module, Batch
from ..schemas import FeeCreate, FeeUpdate
from auth.auth_bearer import JWTBearer, get_admin, get_teacher, get_admin_or_teacher, get_admin_or_student
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

@staticmethod
def get_amount_by_criteria(
    course_id: int, standard_id: int, year: int, subject_id: int, module_id: int, batch_id: int, db: Session
) -> float:
    try:
        course = db.query(Course).filter_by(id=course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found")

        standard = db.query(Standard).filter_by(id=standard_id).first()
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with id {standard_id} not found")

        subject = db.query(Subject).filter_by(id=subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found")

        module = db.query(Module).filter_by(id=module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail=f"Module with id {module_id} not found")

        batch = db.query(Batch).filter_by(id=batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch with id {batch_id} not found")

        query = select(Fee.amount).filter(
            Fee.course_id == course_id,
            Fee.standard_id == standard_id,
            Fee.year == year,
            Fee.subject_id == subject_id,
            Fee.module_id == module_id,
            Fee.batch_id == batch_id
        )
        result = db.execute(query).fetchone()
        if result:
            return {"amount":result[0]}
        else:
            raise HTTPException(status_code=404, detail="No record found with the given criteria")
    except HTTPException as e:
        raise e

        

# # Create a new fee
# @router.post("/fees/create_fees/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
# async def create_fee(fee_data: FeeCreate, db: Session = Depends(get_db)):
#     try:
#         related_entities = [
#             (Course, fee_data.course_id, "Course"),
#             (Subject, fee_data.subject_id, "Subject"),
#             (Standard, fee_data.standard_id, "Standard"),
#             (Module, fee_data.module_id, "Module"),
#             (Batch, fee_data.batch_id, "Batch")
#         ]

#         for entity_cls, entity_id, entity_name in related_entities:
#             entity_exists = db.query(entity_cls).filter(entity_cls.id == entity_id).first()
#             if not entity_exists:
#                 raise HTTPException(status_code=404, detail=f"{entity_name} with id {entity_id} not found")

#         fee = Fee(**fee_data.dict())
#         db.add(fee)
#         db.commit()
#         db.refresh(fee)
#         return fee
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to insert fees: {str(e)}")
    
# updated by bhavan kumar


# Create a new fee
@router.post("/fees/create_fees/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_student)])
async def create_fee(fee_data: FeeCreate, db: Session = Depends(get_db)):
    try:
        related_entities = [
            (Course, fee_data.course_id, "Course"),
            (Subject, fee_data.subject_id, "Subject"),
            (Standard, fee_data.standard_id, "Standard"),
            (Module, fee_data.module_id, "Module"),
            (Batch, fee_data.batch_id, "Batch")
        ]

        for entity_cls, entity_id, entity_name in related_entities:
            entity_exists = db.query(entity_cls).filter(entity_cls.id == entity_id).first()
            if not entity_exists:
                raise HTTPException(status_code=404, detail=f"{entity_name} with id {entity_id} not found")

        # Check for duplicate before creating
        existing_fee = db.query(Fee).filter(
            Fee.course_id == fee_data.course_id,
            Fee.subject_id == fee_data.subject_id,
            Fee.standard_id == fee_data.standard_id,
            Fee.module_id == fee_data.module_id,
            Fee.batch_id == fee_data.batch_id
        ).first()

        if existing_fee:
            raise HTTPException(status_code=400, detail="Fee with these details already exists")

        fee = Fee(**fee_data.dict())
        db.add(fee)
        db.commit()
        db.refresh(fee)
        return fee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert fees: {str(e)}")




@router.get("/fees/bycriteria", response_model=None)
async def read_fees(
    course_id: int = None, standard_id: int = None, year: int = None, subject_id: int = None,
    module_id: int = None, batch_id: int = None, db: Session = Depends(get_db)
):
    return get_amount_by_criteria(course_id, standard_id, year, subject_id, module_id, batch_id, db)




@router.get("/fees/all_fees/", response_model=list[dict], dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def read_fees(db: Session = Depends(get_db)):
    try:
        fees = db.query(Fee).options(
            joinedload(Fee.course),
            joinedload(Fee.standard),
            joinedload(Fee.subject),
            joinedload(Fee.module),
            joinedload(Fee.batch)
        ).all()

        data = [
            {
                "fee_id": fee.id,
                "course_id": fee.course_id,
                "course_name": fee.course.name if fee.course else None,
                "standard_name": fee.standard.name if fee.standard else None,
                "standard_id": fee.standard.id if fee.standard else None,
                "subject_name": fee.subject.name if fee.subject else None,
                "subject_id": fee.subject.id if fee.subject else None,
                "module_name": fee.module.name if fee.module else None,
                "module_id": fee.module.id if fee.module else None,
                "batch_id": fee.batch.id if fee.batch else None,
                "batch_name": fee.batch.size if fee.batch else None,
                "year": fee.year if fee.batch else None,
                "amount": fee.amount
            }
            for fee in fees
        ]

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch fees: {str(e)}")

# Get a specific fee by ID
@router.get("/fees/{fee_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def read_fee(fee_id: int, db: Session = Depends(get_db)):
    try:
        fee = db.query(Fee).filter(Fee.id == fee_id).first()
        if fee is None:
            raise HTTPException(status_code=404, detail="Fee not found")
        return fee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch fees: {str(e)}")


@router.put("/fees/update_fees/{fee_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_fee(fee_id: int, fee_data: FeeUpdate, db: Session = Depends(get_db)):
    try:
        fee = db.query(Fee).filter(Fee.id == fee_id).first()
        if fee is None:
            raise HTTPException(status_code=404, detail="Fee record not found")

        if fee_data.course_id is not None:
            course_exists = db.query(Course).filter(Course.id == fee_data.course_id).first()
            if not course_exists:
                raise HTTPException(status_code=400, detail=f"Course ID {fee_data.course_id} does not exist")

        if fee_data.standard_id is not None:
            standard_exists = db.query(Standard).filter(Standard.id == fee_data.standard_id).first()
            if not standard_exists:
                raise HTTPException(status_code=400, detail=f"Standard ID {fee_data.standard_id} does not exist")

        if fee_data.subject_id is not None:
            subject_exists = db.query(Subject).filter(Subject.id == fee_data.subject_id).first()
            if not subject_exists:
                raise HTTPException(status_code=400, detail=f"Subject ID {fee_data.subject_id} does not exist")

        if fee_data.modules_id is not None:
            module_exists = db.query(Module).filter(Module.id == fee_data.modules_id).first()
            if not module_exists:
                raise HTTPException(status_code=400, detail=f"Module ID {fee_data.modules_id} does not exist")

        if fee_data.batch_id is not None:
            batch_exists = db.query(Batch).filter(Batch.id == fee_data.batch_id).first()
            if not batch_exists:
                raise HTTPException(status_code=400, detail=f"Batch ID {fee_data.batch_id} does not exist")

        if fee_data.course_id is not None:
            fee.course_id = fee_data.course_id
        if fee_data.standard_id is not None:
            fee.standard_id = fee_data.standard_id
        if fee_data.year is not None:
            fee.year = fee_data.year
        if fee_data.subject_id is not None:
            fee.subject_id = fee_data.subject_id
        if fee_data.modules_id is not None:
            fee.module_id = fee_data.modules_id
        if fee_data.batch_id is not None:
            fee.batch_id = fee_data.batch_id
        if fee_data.amount is not None:
            fee.amount = fee_data.amount

        db.commit()
        db.refresh(fee)
        return fee

    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating fees.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error while updating fees: {str(e)}")


@router.delete("/fees/delete_fees/{fee_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def delete_fee(fee_id: int, db: Session = Depends(get_db)):
    try:
        fee = db.query(Fee).filter(Fee.id == fee_id).first()
        if fee is None:
            raise HTTPException(status_code=404, detail="fee not found")
        db.delete(fee)
        db.commit()
        return fee
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete fees: {str(e)}")