from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session,joinedload
from db.session import get_db
from pydantic import BaseModel, Field
from ..schemas import BulkQuestionCreate, QuestionGetResponse
from ..models import LmsUsers 
from typing import List, Optional
from fastapi import Form
import shutil
import uuid
import os
from auth.auth_bearer import JWTBearer,get_admin, get_teacher, get_admin_or_teacher
from .lms_users import router as lms_router, get_current_user
from sqlalchemy.exc import IntegrityError
import difflib
from ..models.lesson_student_test_ans import StudentAnswer
from ..models import QuestionPaper1,Lesson
from ..models import LessontestQuestion
import difflib
from PIL import Image
import numpy as np
from dotenv import load_dotenv
from typing import List, Dict
from ..models.course_detail import CourseDetails
from ..models.teacher_course import TeacherCourse
from ..models.courses_content import Course_content

load_dotenv()
router = APIRouter()

# ------------------------------------------------------------------------------------------------------------------
                        #Question
# ------------------------------------------------------------------------------------------------------------------


# def save_upload(upload_file: Optional[UploadFile]) -> Optional[str]:
#     if not upload_file:
#         return None
    
#     try:
#         unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
#         file_path = os.path.join("static", "uploads", unique_filename)
        
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(upload_file.file, buffer)
        
#         file_path = file_path.replace("\\", "/")
#         return file_path
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

# @router.post("/lesson-test-questions/", response_model=None,  dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
# async def create_question(
#     question_paper_id: int = Form(None),
#     question_text: str = Form(None),
#     question_images: UploadFile = File(None),
#     option1_text: str = Form(None),
#     option1_images: UploadFile = File(None),
#     option2_text: str = Form(None),
#     option2_images: UploadFile = File(None),
#     option3_text: str = Form(None),
#     option3_images: UploadFile = File(None),
#     option4_text: str = Form(None),
#     option4_images: UploadFile = File(None),
#     correct_ans_text: str = Form(None),
#     correct_ans_images: UploadFile = File(None),
#     difficulty_level: str = Form(None),
#     per_question_marks: int = Form(None),
#     db: Session = Depends(get_db)
# ):
#     try:
#         question_paper = db.query(QuestionPaper1).filter(QuestionPaper1.id == question_paper_id).first()
#         if not question_paper:
#             raise HTTPException(status_code=404, detail=f"Question paper with id {question_paper_id} not found")

#         lesson = db.query(Lesson).filter(Lesson.lesson_id == question_paper.lesson_id).first()
#         if not lesson:
#             raise HTTPException(status_code=404, detail=f"Lesson with id {question_paper.lesson_id} not found")

#         db_question = LessontestQuestion(
#             question_paper_id=question_paper_id,
#             question_text=question_text,
#             question_images=save_upload(question_images),
#             option1_text=option1_text,
#             option1_images=save_upload(option1_images),
#             option2_text=option2_text,
#             option2_images=save_upload(option2_images),
#             option3_text=option3_text,
#             option3_images=save_upload(option3_images),
#             option4_text=option4_text,
#             option4_images=save_upload(option4_images),
#             correct_ans_text=correct_ans_text,
#             correct_ans_images=save_upload(correct_ans_images),
#             difficulty_level=difficulty_level,
#             per_question_marks=per_question_marks
#         )

#         db.add(db_question)
#         db.commit()
#         db.refresh(db_question)

#         return {"message": "Question created successfully"}

#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         db.rollback()  
#         print(f"Detailed error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")





class BulkQuestionCreate(BaseModel):
    question_paper_id: int
    question_text: str
    question_images: Optional[str] = None
    option1_text: str
    option1_images: Optional[str] = None
    option2_text: str
    option2_images: Optional[str] = None
    option3_text: str
    option3_images: Optional[str] = None
    option4_text: str
    option4_images: Optional[str] = None
    correct_ans_text: str
    correct_ans_images: Optional[str] = None
    difficulty_level: str
    per_question_marks: int




def save_upload(upload_file: Optional[UploadFile]) -> Optional[str]:
    if not upload_file:
        return None
    try:
        unique_filename = str(uuid.uuid4()) + "_" + upload_file.filename
        file_path = os.path.join("static", "uploads", unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        file_path = file_path.replace("\\", "/")
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    

@router.post("/upload/")
async def upload_file(file:UploadFile=File(...)):
    try:
        file_path = save_upload(file)
        return {"filePath":file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@router.post("/lesson-test-questions/", response_model=Dict[str, str], dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def create_bulk_questions(questions: List[BulkQuestionCreate], db: Session = Depends(get_db)):
    try:
        created_count = 0
        for question_data in questions:
            question_paper = db.query(QuestionPaper1).filter(QuestionPaper1.id == question_data.question_paper_id).first()
            if not question_paper:
                raise HTTPException(status_code=400, detail=f"Question paper with id {question_data.question_paper_id} not found")

            lesson = db.query(Lesson).filter(Lesson.lesson_id == question_paper.lesson_id).first()
            if not lesson:
                raise HTTPException(status_code=400, detail=f"Lesson with id {question_paper.lesson_id} not found")

            db_question = LessontestQuestion(
                question_paper_id=question_data.question_paper_id,
                question_text=question_data.question_text,
                question_images=question_data.question_images.replace("\\", "/").replace("\\\\", "/") if question_data.question_images else None,
                option1_text=question_data.option1_text,
                option1_images=question_data.option1_images.replace("\\", "/").replace("\\\\", "/") if question_data.option1_images else None,
                option2_text=question_data.option2_text,
                option2_images=question_data.option2_images.replace("\\", "/").replace("\\\\", "/") if question_data.option2_images else None,
                option3_text=question_data.option3_text,
                option3_images=question_data.option3_images.replace("\\", "/").replace("\\\\", "/") if question_data.option3_images else None,
                option4_text=question_data.option4_text,
                option4_images=question_data.option4_images.replace("\\", "/").replace("\\\\", "/") if question_data.option4_images else None,
                correct_ans_text=question_data.correct_ans_text,
                correct_ans_images=question_data.correct_ans_images.replace("\\", "/").replace("\\\\", "/") if question_data.correct_ans_images else None,
                difficulty_level=question_data.difficulty_level,
                per_question_marks=question_data.per_question_marks
            )
            db.add(db_question)
            created_count += 1

        db.commit()
        return {"message": f"{created_count} questions created successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Detailed error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create bulk questions: {str(e)}")









   
base_url_path = os.getenv("BASE_URL_PATH")

def prepend_base_url(path: Optional[str]) -> Optional[str]:
    if path:
        return f"{base_url_path}/{path}"
    return None








@router.post("/lesson-test-questions/student-answers/{question_id}/answer")
async def answer_question(
    question_id: int,
    user_answer: str = Form(...),  
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    question = db.query(LessontestQuestion).filter(LessontestQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    student_answer = db.query(StudentAnswer).filter(
        StudentAnswer.user_id == current_user.user_id,
        StudentAnswer.question_paper_id == question.question_paper_id
    ).first()
    
    if not student_answer:
        student_answer = StudentAnswer(
            user_id=current_user.user_id,
            question_paper_id=question.question_paper_id,
            total_questions=0,
            correct_answer=0,
            wrong_answer=0,
            score=0,
            passed=False
        )
        db.add(student_answer)
        db.commit()
        db.refresh(student_answer)

    try:
        def get_option_number(answer):
            options = {
                (question.option1_text or "").lower().strip(): "option1",
                (question.option1_images or "").lower().strip(): "option1",
                (question.option2_text or "").lower().strip(): "option2",
                (question.option2_images or "").lower().strip(): "option2",
                (question.option3_text or "").lower().strip(): "option3",
                (question.option3_images or "").lower().strip(): "option3",
                (question.option4_text or "").lower().strip(): "option4",
                (question.option4_images or "").lower().strip(): "option4",
            }
            return options.get(answer.lower().strip())

        user_option = get_option_number(user_answer)

        if not user_option:
            raise HTTPException(status_code=400, detail="Invalid answer")

        is_correct = user_option == question.correct_ans_text

        student_answer.total_questions += 1
        student_answer.given_ans_text = user_option  
        student_answer.is_correct = is_correct
        if is_correct:
            student_answer.correct_answer += 1
        else:
            student_answer.wrong_answer += 1

       # Calculate score
        correct_points = student_answer.correct_answer * question.per_question_marks  
        # wrong_points = student_answer.wrong_answer * 0.25  
        # total_points = correct_points - wrong_points
        #max_possible_points = student_answer.total_questions*2 
        # student_answer.score = (total_points / max_possible_points) * 100 if max_possible_points > 0 else 0
        student_answer.score = correct_points

        # Ensure score is between 0 and 100
        #student_answer.score = max(min(student_answer.score, 100), 0)
        student_answer.passed = student_answer.score >= 40
        
        db.commit()
        db.refresh(student_answer)

        return {
            "student_id": current_user.user_id,
            "question_id": question_id,
            "question_text": question.question_text,
            "question_images": prepend_base_url(question.question_images),
            "options": {
                "option1_text": question.option1_text,
                "option1_images": prepend_base_url(question.option1_images),
                "option2_text": question.option2_text,
                "option2_images": prepend_base_url(question.option2_images),
                "option3_text": question.option3_text,
                "option3_images": prepend_base_url(question.option3_images),
                "option4_text": question.option4_text,
                "option4_images": prepend_base_url(question.option4_images),
            },
            "correct_ans": question.correct_ans_text,
            "user_answer": user_answer,
            "user_answer_image": student_answer.given_ans_image,
            "user_selected_option": user_option,  
            "is_correct": is_correct,
            "obtain_marks": student_answer.score,
            "total_questions_answered": student_answer.total_questions,
            "correct_answers": student_answer.correct_answer,
            "wrong_answers": student_answer.wrong_answer,
            "passed": student_answer.passed 
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating the student answer")

##########################################################################
class AnswerRequest(BaseModel):
    question_id: int
    user_answer: Optional[str] = None

@router.post("/lesson-test-questions/student-answers/all/")
async def answer_questions(
    answers: List[AnswerRequest],
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        if not answers:
            raise HTTPException(status_code=400, detail="provide at leat one Answer.")

        question_ids = [answer.question_id for answer in answers]
        questions = db.query(LessontestQuestion).filter(LessontestQuestion.id.in_(question_ids)).all()

        if not questions:
            raise HTTPException(status_code=404, detail="Some questions not found.")
        
        question_paper_id = questions[0].question_paper_id

        question_paper = db.query(QuestionPaper1).filter(QuestionPaper1.id == question_paper_id).first()
        if question_paper and question_paper.is_test_completed:
            raise HTTPException(status_code=400, detail='You have already submitted the test for this lesson')

        student_test = db.query(StudentAnswer).filter(
            StudentAnswer.user_id == current_user.user_id,
            StudentAnswer.question_paper_id == question_paper_id,
            StudentAnswer.is_test_completed == True
        ).first()
        if student_test:
            raise HTTPException(status_code=400, detail='You have already submitted this Test')
        
        student_answer = db.query(StudentAnswer).filter(
            StudentAnswer.user_id == current_user.user_id,
            StudentAnswer.question_paper_id == question_paper_id
        ).first()

        if not student_answer:
            student_answer = StudentAnswer(
                user_id=current_user.user_id,
                question_paper_id=question_paper_id,
                total_questions=0,
                correct_answer=0,
                wrong_answer=0,
                score=0,
                passed=False
            )
            db.add(student_answer)
            db.commit()
            db.refresh(student_answer)

        total_correct_points = 0
        total_max_points = 0

        results = []
        for answer in answers:
            question = next((q for q in questions if q.id == answer.question_id), None)
            if not question:
                raise HTTPException(status_code=404, detail=f"Question with ID {answer.question_id} not found")

            def get_option_number(user_answer):
                options = {
                    (question.option1_text or "").lower().strip(): "A",
                    (question.option1_images or "").lower().strip(): "A",
                    (question.option2_text or "").lower().strip(): "B",
                    (question.option2_images or "").lower().strip(): "B",
                    (question.option3_text or "").lower().strip(): "C",
                    (question.option3_images or "").lower().strip(): "C",
                    (question.option4_text or "").lower().strip(): "D",
                    (question.option4_images or "").lower().strip(): "D",
                }
                return options.get(user_answer.lower().strip())

            user_option = get_option_number(answer.user_answer)

            is_correct = answer.user_answer == question.correct_ans_text

            student_answer.total_questions += 1
            if is_correct:
                student_answer.correct_answer += 1
                total_correct_points += question.per_question_marks  
            else:
                student_answer.wrong_answer += 1
            
            total_max_points += question.per_question_marks  

            result = {
                "question_id": question.id,
                "question_text": question.question_text,
                "user_answer": answer.user_answer,
                "user_selected_option": user_option,
                "correct_ans": question.correct_ans_text,
                "is_correct": is_correct,
                "obtain_marks": question.per_question_marks if is_correct else 0
            }
            results.append(result)

        student_answer.score = total_correct_points
        score_in_percentage = (total_correct_points / total_max_points) * 100 if total_max_points > 0 else 0
        student_answer.passed = score_in_percentage >= 35
        student_answer.is_test_completed = True

        if question_paper:
            question_paper.is_test_completed = True

        db.commit()
        db.refresh(student_answer)

        return {
            "student_id": current_user.user_id,
            "total_questions_answered": student_answer.total_questions,
            "correct_answers": student_answer.correct_answer,
            "wrong_answers": student_answer.wrong_answer,
            "score": student_answer.score,
            "passed": student_answer.passed,
            "answers": results
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating the student answers")
        
@router.get("/student_result/")
async def student_result(
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        result_db = (
            db.query(StudentAnswer)
            .options(
                joinedload(StudentAnswer.users),
                joinedload(StudentAnswer.question_paper),joinedload(StudentAnswer.question_paper)
            )
            .join(QuestionPaper1, QuestionPaper1.id == StudentAnswer.question_paper_id)  
            .join(CourseDetails, CourseDetails.course_content_id == QuestionPaper1.course_content_id)
            .filter(
                QuestionPaper1.created_by == current_user.user_id
            )
            .all()
        )
        
        all_data = []
        for result in result_db:
            data = {
                "lesson_name":result.question_paper.lesson_title,
                "Student_name": result.users.user_name,
                "total_questions": result.total_questions,
                "total_correct_answer": result.correct_answer,
                "total_wrong_answer": result.wrong_answer,
                "Total_marks": result.score,
                "Result_status": result.passed,
            }
            all_data.append(data)

        return all_data

    except Exception as e:
        raise HTTPException(status_code=404, detail="Not found")
    

@router.get("/completed-tests/get_all/")
async def completed_tests(db: Session = Depends(get_db),current_user: LmsUsers = Depends(get_current_user)):
    try:
        all_data = []
        test_db=db.query(StudentAnswer).join(StudentAnswer.question_paper).join(CourseDetails, CourseDetails.course_content_id == QuestionPaper1.course_content_id).filter(
                and_(
                    CourseDetails.user_id == current_user.user_id,
                    StudentAnswer.is_test_completed == True
                )
            ).options(
                joinedload(StudentAnswer.users),
                joinedload(StudentAnswer.question_paper)
            ).all()
        
        for test in test_db:
            if test.is_test_completed:  
                data = {
                    "lesson_id": test.question_paper.lesson_id,
                    "lesson_title": test.question_paper.lesson_title,
                    "is_test_completed": test.question_paper.is_test_completed,
                    "created_on": test.created_on,
                    # "result":{
                    #     "student_name":test.users.user_name,
                    # "total_questions_attempt":test.total_questions,
                    # "total_correct_ans":test.correct_answer,
                    # "wrong_answer":test.wrong_answer,
                    # "total_marks":test.score,
                    # } 
                }
            
                all_data.append(data)
        
        return all_data  
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/lesson_name-tests/get_all/")
async def completed_tests(db: Session = Depends(get_db),current_user: LmsUsers = Depends(get_current_user)):
    try:
        lesson_db = db.query(QuestionPaper1).filter(QuestionPaper1.created_by==current_user.user_id).all()
        if not lesson_db:
            raise HTTPException(status_code=404, detail="not found lesson")
        all_data=[]
        for lesson in lesson_db:
            data={
                "id":lesson.id,
                "lesson_id" :lesson.lesson_id,
                "lesson_title" :lesson.lesson_title,
                "is_test_completed" :lesson.is_test_completed,
                "created_on" :lesson.created_on,
                "created_by":lesson.created_by

            }
            all_data.append(data)

        return all_data  
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@router.get("/lesson_name-tests/get_all/for_student/")
async def completed_tests(db: Session = Depends(get_db), current_user: LmsUsers = Depends(get_current_user)):
    try:
        # Fetch lessons for the current user based on their associated course content
        lesson_db = (
            db.query(QuestionPaper1)
            .join(CourseDetails, CourseDetails.course_content_id == QuestionPaper1.course_content_id)
            .filter(CourseDetails.user_id == current_user.user_id)
            .all()
        )

        # Raise a 404 if no lessons are found
        if not lesson_db:
            raise HTTPException(status_code=404, detail="No lessons found for the user")

        all_data=[]
        for lesson in lesson_db:
            data={
                "id":lesson.id,
                "lesson_id" :lesson.lesson_id,
                "lesson_title" :lesson.lesson_title,
                "is_test_completed" :lesson.is_test_completed,
                "created_on" :lesson.created_on,
                "created_by":lesson.created_by

            }
            all_data.append(data)

        return all_data  
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    
@router.get("/lesson_test_questions/new/{lesson_id}", response_model=None)
async def get_lesson_test_question(
    lesson_id: int,
    db: Session = Depends(get_db),
) :
    try:
        all_questions = []
        questions = db.query(LessontestQuestion).filter(LessontestQuestion.question_paper_id == lesson_id).all()
        
        for question in questions:
            response_data = {
                "id": question.id,
                "question_paper_id": question.question_paper_id,
                "question_text": question.question_text,
                "question_image": prepend_base_url(question.question_images),
                "option1_text": question.option1_text,
                "option1_image": prepend_base_url(question.option1_images),
                "option2_text": question.option2_text,
                "option2_image": prepend_base_url(question.option2_images),
                "option3_text": question.option3_text,
                "option3_image": prepend_base_url(question.option3_images),
                "option4_text": question.option4_text,
                "option4_image": prepend_base_url(question.option4_images),
                "difficulty_level": question.difficulty_level,
                "per_question_marks": question.per_question_marks,
            }

            all_questions.append(response_data)

        return all_questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")

##########################################################################

@router.get("/lesson-test-questions/{question_id}", response_model=None)
async def get_lesson_test_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: LmsUsers = Depends(get_current_user)
):
    try:
        question = db.query(LessontestQuestion).filter(LessontestQuestion.id == question_id).first()
        
        if question is None:
            raise HTTPException(status_code=404, detail="Question not found")
        
        response_data = {
            "id": question.id,
            "question_paper_id": question.question_paper_id,
            "question_text": question.question_text,
            "question_image": prepend_base_url(question.question_images),
            "option1_text": question.option1_text,
            "option1_image": prepend_base_url(question.option1_images),
            "option2_text": question.option2_text,
            "option2_image": prepend_base_url(question.option2_images),
            "option3_text": question.option3_text,
            "option3_image": prepend_base_url(question.option3_images),
            "option4_text": question.option4_text,
            "option4_image": prepend_base_url(question.option4_images),
            "difficulty_level": question.difficulty_level,
            "per_question_marks": question.per_question_marks
        }
        
        if current_user.user_type in ["admin", "teacher"]:
            response_data["correct_answer_text"] = question.correct_ans_text
            response_data["correct_answer_image"] = prepend_base_url(question.correct_ans_images)
        
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch question: {str(e)}")
    
@router.get("/lesson_test_questions/get_all/", response_model=None)
async def get_lesson_test_question(
    db: Session = Depends(get_db),
):
    try:
        all_questions = []
        questions = db.query(LessontestQuestion).all()
        
        for question in questions:
            response_data = {
                "id": question.id,
                "question_paper_id": question.question_paper_id,
                "question_text": question.question_text,
                "question_image": prepend_base_url(question.question_images),
                "option1_text": question.option1_text,
                "option1_image": prepend_base_url(question.option1_images),
                "option2_text": question.option2_text,
                "option2_image": prepend_base_url(question.option2_images),
                "option3_text": question.option3_text,
                "option3_image": prepend_base_url(question.option3_images),
                "option4_text": question.option4_text,
                "option4_image": prepend_base_url(question.option4_images),
                "difficulty_level": question.difficulty_level,
                "per_question_marks": question.per_question_marks
            }

            all_questions.append(response_data)

        return all_questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")


@router.put("/questions/{question_id}", response_model=None)
async def update_question(
    question_id: int,
    question_text: str = Form(None),
    question_image: UploadFile = File(default=None),
    option1_text: str = Form(None),
    option1_image: UploadFile = File(default=None),
    option2_text: str = Form(None),
    option2_image: UploadFile = File(default=None),
    option3_text: str = Form(None),
    option3_image: UploadFile = File(default=None),
    option4_text: str = Form(None),
    option4_image: UploadFile = File(default=None),
    correct_answer_text: str = Form(None),
    correct_answer_image: UploadFile = File(default=None),
    difficulty_level: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        db_question = db.query(LessontestQuestion).filter(LessontestQuestion.id == question_id).first()

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

        if question_image:
            question_image_path = save_upload(question_image)
            db_question.question_images = question_image_path
        if option1_image:
            option1_image_path = save_upload(option1_image)
            db_question.option1_images = option1_image_path
        if option2_image:
            option2_image_path = save_upload(option2_image)
            db_question.option2_images = option2_image_path
        if option3_image:
            option3_image_path = save_upload(option3_image)
            db_question.option3_images = option3_image_path
        if option4_image:
            option4_image_path = save_upload(option4_image)
            db_question.option4_images = option4_image_path
        if correct_answer_image:
            correct_answer_image_path = save_upload(correct_answer_image)
            db_question.correct_ans_images = correct_answer_image_path
        

        # Commit the changes
        db.add(db_question)
        db.commit()

        return {"message": "Question has been updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/questions/{question_id}", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin_or_teacher)])
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    try:
        db_question = db.query(LessontestQuestion).filter(LessontestQuestion.id == question_id).first()

        if db_question is None:
            raise HTTPException(status_code=404, detail="Question not found")

        db.delete(db_question)
        db.commit()

        return {"message": "Question has been deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



