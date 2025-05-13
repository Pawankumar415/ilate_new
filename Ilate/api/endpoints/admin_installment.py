


from sqlalchemy import select
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from db.session import get_db
from ..models import AdminInstallment, Installment, Course, Fee, Standard, Subject, Module, Batch
from ..schemas import AdminInstallmentCreate, AdminInstallmentResponse
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()


class InstallmentInput(BaseModel):
    installment_number: int = Field(..., gt=0, le=3)  # le=3 => max 3 installments
    amount: Decimal = Field(..., gt=0)
    due_date: date


class AdminInstallmentCreate(BaseModel):  
    number_of_installments: int = Field(..., gt=0, le=3)
    total_amount: Decimal = Field(..., gt=0)
    installments_data: List[InstallmentInput]
    course_id: int
    standard_id: Optional[int] = None
    year: Optional[int] = None
    subject_id: Optional[int] = None
    module_id: Optional[int] = None
    batch_id: Optional[int] = None
    


@router.post("/admin_installments/")
def create_admin_installment(
    installment_data: AdminInstallmentCreate,
    db: Session = Depends(get_db)
):
    # Validate course, standard, subject, etc. before creating the AdminInstallment
    # Validate Course
    course = db.query(Course).filter(Course.id == installment_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id {installment_data.course_id} not found.")

    # Validate Standard
    if installment_data.standard_id:
        standard = db.query(Standard).filter(Standard.id == installment_data.standard_id).first()
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with id {installment_data.standard_id} not found.")
    
    # Validate Subject
    if installment_data.subject_id:
        subject = db.query(Subject).filter(Subject.id == installment_data.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail=f"Subject with id {installment_data.subject_id} not found.")
    
    # Validate Module
    if installment_data.module_id:
        module = db.query(Module).filter(Module.id == installment_data.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail=f"Module with id {installment_data.module_id} not found.")
    
    # Validate Batch
    if installment_data.batch_id:
        batch = db.query(Batch).filter(Batch.id == installment_data.batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch with id {installment_data.batch_id} not found.")
    
    # Validate Fee Record
    fee = db.query(Fee).filter(
        Fee.course_id == installment_data.course_id,
        Fee.standard_id == installment_data.standard_id,
        Fee.subject_id == installment_data.subject_id,
        Fee.year == installment_data.year,
        Fee.module_id == installment_data.module_id,
        Fee.batch_id == installment_data.batch_id,
    ).first()

    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found for the given details.")
    
    # Check if admin installment already exists
    existing = db.query(AdminInstallment).filter(
        AdminInstallment.course_id == installment_data.course_id,
        AdminInstallment.standard_id == installment_data.standard_id,
        AdminInstallment.subject_id == installment_data.subject_id,
        AdminInstallment.year == installment_data.year,
        AdminInstallment.module_id == installment_data.module_id,
        AdminInstallment.batch_id == installment_data.batch_id,
        AdminInstallment.number_of_installments == installment_data.number_of_installments,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Installment plan already exists for the given details.")

    # # Validate total amount matches fee
    # if installment_data.total_amount != Decimal(fee.amount):
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Total installment amount ({installment_data.total_amount}) does not match fee amount ({fee.amount})"
    #     )

    # Validate sum of parts
    # total_parts = sum([i.amount for i in installment_data.installments_data])
    # if total_parts != installment_data.total_amount:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Sum of installments ({total_parts}) does not match total_amount ({installment_data.total_amount})"
    #     )

    if len(installment_data.installments_data) != installment_data.number_of_installments:
        raise HTTPException(
            status_code=400,
            detail=f"Number of installment entries ({len(installment_data.installments_data)}) does not match 'number_of_installments' ({installment_data.number_of_installments})"
        )

    # Save to DB
    admin_installment = AdminInstallment(
        course_id=installment_data.course_id,
        number_of_installments=installment_data.number_of_installments,
        total_amount=installment_data.total_amount,
        standard_id=installment_data.standard_id,
        subject_id=installment_data.subject_id,
        year=installment_data.year,
        module_id=installment_data.module_id,
        batch_id=installment_data.batch_id,
        
    )

    for installment in installment_data.installments_data:
        if installment.installment_number == 1:
            admin_installment.installment_1_amount = installment.amount
            admin_installment.installment_1_due_date = installment.due_date
        elif installment.installment_number == 2:
            admin_installment.installment_2_amount = installment.amount
            admin_installment.installment_2_due_date = installment.due_date
        elif installment.installment_number == 3:
            admin_installment.installment_3_amount = installment.amount
            admin_installment.installment_3_due_date = installment.due_date
        else:
            raise HTTPException(status_code=400, detail="Installment number must be 1 to 3")

    db.add(admin_installment)
    db.commit()
    db.refresh(admin_installment)

    return {
        "message": "Installment plan created successfully",
        "admin_installment_id": admin_installment.id
    }



class Installment(BaseModel):
    installment_number: int
    amount: float
    due_date: date


class AdminInstallmentCleanedResponse(BaseModel):
    id: int
    course_id: int
    number_of_installments: int
    total_amount: float
    standard_id: int
    year: int
    subject_id: int
    module_id: int
    batch_id: int
    
    installments: List[Installment]


@router.get("/admin_installments/bycriteria", response_model=List[AdminInstallmentCleanedResponse])
async def get_installments_by_criteria(
    course_id: Optional[int] = None,
    standard_id: Optional[int] = None,
    year: Optional[int] = None,
    subject_id: Optional[int] = None,
    module_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    number_of_installments: Optional[int] = None, 
    db: Session = Depends(get_db),
):
    # Start query
    query = select(AdminInstallment)

    # Validate each field
    if course_id is not None:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found.")
        query = query.filter(AdminInstallment.course_id == course_id)

    if standard_id is not None:
        standard = db.query(Standard).filter(Standard.id == standard_id).first()
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with id {standard_id} not found.")
        query = query.filter(AdminInstallment.standard_id == standard_id)

    if subject_id is not None:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found.")
        query = query.filter(AdminInstallment.subject_id == subject_id)

    if module_id is not None:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail=f"Module with id {module_id} not found.")
        query = query.filter(AdminInstallment.module_id == module_id)

    if batch_id is not None:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch with id {batch_id} not found.")
        query = query.filter(AdminInstallment.batch_id == batch_id)

    if number_of_installments is not None:
        query = query.filter(AdminInstallment.number_of_installments == number_of_installments)

    # Execute query
    rows = db.execute(query).scalars().all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No installments found for the given criteria."
        )

    # Prepare response
    response = []
    for row in rows:
        installments = []

        if row.installment_1_amount:
            installments.append({
                "installment_number": 1,
                "amount": row.installment_1_amount,
                "due_date": row.installment_1_due_date
            })
        if row.installment_2_amount:
            installments.append({
                "installment_number": 2,
                "amount": row.installment_2_amount,
                "due_date": row.installment_2_due_date
            })
        if row.installment_3_amount:
            installments.append({
                "installment_number": 3,
                "amount": row.installment_3_amount,
                "due_date": row.installment_3_due_date
            })

        response.append({
            "id": row.id,
            "course_id": row.course_id,
            "number_of_installments": row.number_of_installments,
            "total_amount": row.total_amount,
            "standard_id": row.standard_id,
            "year": row.year,
            "subject_id": row.subject_id,
            "module_id": row.module_id,
            "batch_id": row.batch_id,
            "installments": installments
        })

    return response
