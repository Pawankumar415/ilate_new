from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
#from ..models.Questions import Question as QuestionModel
from ..models.Discount_assesment_paper import DiscountQuestion
from pydantic import BaseModel, Field
from ..schemas import QuestionCreate, QuestionGetResponse
#from ..models.Questions import Question, save_upload
from ..models import LmsUsers,Standard, Subject 
from typing import List, Optional
from fastapi import Form
import shutil
import uuid
import os
from auth.auth_bearer import JWTBearer,get_admin, get_teacher, get_admin_or_teacher
from ..endpoints.lms_users import router as lms_router, get_current_user
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
#from ..models.Discount_correct_ans import DiscountCorrectAnswer
from ..models.Discount_Ass_result import DiscountAssessmentResut
from pathlib import Path
import difflib


load_dotenv()
router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        # Discount Question paper
# ------------------------------------------------------------------------------------------------------------------

################### create question paper for admin #######################

@router.post("/Discount_questions/", response_model=None)
async def create_question(
    standard_id : int= Form(...),
    subject_id : int= Form(...),
    question_text: str = Form(None),
    option1_text: str = Form(None),
    option2_text: str = Form(None),
    option3_text: str = Form(None),
    option4_text: str = Form(None),
    correct_answer_text: str = Form(None),
    difficulty_level: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        
        db_question = DiscountQuestion(
            standard_id=standard_id,
            subject_id=subject_id,
            question_text=question_text,
            option1_text=option1_text,
            option2_text=option2_text,
            option3_text=option3_text,
            option4_text=option4_text,
            correct_ans_text=correct_answer_text,
            difficulty_level=difficulty_level
        )
        
        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        return db_question
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")

def is_answer_correct(selected_ans, correct_ans):
    selected_ans = selected_ans.lower()
    correct_ans = correct_ans.lower()
    similarity = difflib.SequenceMatcher(None, selected_ans, correct_ans).ratio()
    similarity_threshold = 0.9
    if similarity >= similarity_threshold or selected_ans == correct_ans:
        return True
    else:
        return False

#################### Route to handle answering a question #################

@router.post("/Discount_questions/{question_id}/answer")
async def answer_question(
    question_id: int,
    selected_ans_text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    question = db.query(DiscountQuestion).filter(DiscountQuestion.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    user_overall_result = db.query(DiscountAssessmentResut).filter(
        DiscountAssessmentResut.user_id == current_user.user_id
    ).first()
    
    if not user_overall_result:
        user_overall_result = DiscountAssessmentResut(
            user_id=current_user.user_id,
            total_questions=0,
            correct_answers=0,
            wrong_answer=0,
            score=0,
            passed=False
        )
        db.add(user_overall_result)
        db.commit()
        db.refresh(user_overall_result)

    try:
        is_correct = is_answer_correct(selected_ans_text, question.correct_ans_text)

        user_overall_result.total_questions += 1
        if is_correct:
            user_overall_result.correct_answers += 1
        else:
            user_overall_result.wrong_answer += 1
        obtain_marks = user_overall_result.correct_answers * 2  # 2 point for each correct answer
        # wrong_points = user_overall_result.wrong_answer * 0.25  # 0.25 point deduction for each wrong answer
        # total_points = correct_points - wrong_points
        total_marks = user_overall_result.total_questions*2 
        user_overall_result.score = (obtain_marks / total_marks) * 100 if total_marks > 0 else 0
        
        user_overall_result.score = max(user_overall_result.score, 0)
        user_overall_result.score = min(user_overall_result.score, 100)
        user_overall_result.passed = user_overall_result.score >= 75
        db.commit()
        db.refresh(user_overall_result)

        return {
            "user_id": current_user.user_id,
            "question_id": question_id,
            "question_text": question.question_text,
            "options": {
                "option1": question.option1_text,
                "option2": question.option2_text,
                "option3": question.option3_text,
                "option4": question.option4_text,
            },
            "correct_answer": question.correct_ans_text,
            "user_answer": selected_ans_text,
            "is_correct": is_correct,
            "score_in_%": user_overall_result.score,
            "total_questions_answered": user_overall_result.total_questions,
            "correct_answers": user_overall_result.correct_answers,
            "wrong_answers": user_overall_result.wrong_answer,
            "passed": user_overall_result.passed 
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating the assessment result")
########################################################################

class QuestionPaperResponse(BaseModel):
    subject_id: int
    subject_name: str
    standard_id: int
    standard_name: str
    option1_text: str
    option2_text: str
    option3_text: str
    option4_text: str
    correct_ans_text: str
    question_id: int
    question_text: str
    difficulty_level: str

    class Config:
        orm_mode = True

@router.get("/Discount_questions/start_&_limit/", response_model=List[QuestionPaperResponse])
async def get_question_paper(
    standard_id: int,
    subject_id: int,
    start: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    questions = db.query(DiscountQuestion, Subject.name.label('subject_name'), Standard.name.label('standard_name'))\
        .join(Subject, DiscountQuestion.subject_id == Subject.id)\
        .join(Standard, DiscountQuestion.standard_id == Standard.id)\
        .filter(DiscountQuestion.standard_id == standard_id,
                DiscountQuestion.subject_id == subject_id)\
        .offset(start).limit(limit).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for the given standard and subject")
    
    result = []
    for question, subject_name, standard_name in questions:
        result.append(QuestionPaperResponse(
            subject_id=question.subject_id,
            subject_name=subject_name,
            standard_id=question.standard_id,
            standard_name=standard_name,
            option1_text=question.option1_text,
            option2_text=question.option2_text,
            option3_text=question.option3_text,
            option4_text=question.option4_text,
            correct_ans_text=question.correct_ans_text,
            question_id=question.question_id,
            question_text=question.question_text,
            difficulty_level=question.difficulty_level
        ))
    
    return result

@router.get("/Discount_questions/{question_id}", response_model=None)
async def get_lesson_test_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        question = db.query(DiscountQuestion).filter(DiscountQuestion.question_id == question_id).first()
        
        if question is None:
            raise HTTPException(status_code=404, detail="Question not found")
        
        response_data = {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "option1_text": question.option1_text,
            "option2_text": question.option2_text,
            "option3_text": question.option3_text,
            "option4_text": question.option4_text,
            "difficulty_level": question.difficulty_level,
            
        }
        
        if current_user.user_type in ["admin", "teacher"]:
            response_data["correct_answer_text"] = question.correct_ans_text
            
        
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch question: {str(e)}")

@router.put("/Discount_questions/{question_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def update_question(
    question_id: int,
    question_text: str = Form(None),
    option1_text: str = Form(None),
    option2_text: str = Form(None),
    option3_text: str = Form(None),
    option4_text: str = Form(None),
    correct_answer_text: str = Form(None),
    difficulty_level: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        db_question = db.query(DiscountQuestion).filter(DiscountQuestion.question_id == question_id).first()

        if db_question is None:
            raise HTTPException(status_code=404, detail="Question not found")

        if question_text:
            db_question.question_text = question_text
        if option1_text:
            db_question.option1_text = option1_text
        if option2_text:
            db_question.option2_text = option2_text
        if option3_text:
            db_question.option3_text = option3_text
        if option4_text:
            db_question.option4_text = option4_text
        if correct_answer_text:
            db_question.correct_ans_text = correct_answer_text
        if difficulty_level:
            db_question.difficulty_level = difficulty_level
        db.commit()

        return {"message": "Question has been updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update question: {str(e)}")

@router.delete("/Discount_questions/{question_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    try:
        db_question = db.query(DiscountQuestion).filter(DiscountQuestion.question_id == question_id).first()
        if db_question is None:
            raise HTTPException(status_code=404, detail="Question not found")
        db.delete(db_question)
        db.commit()

        return {"message": "Question has been deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete question: {str(e)}")
