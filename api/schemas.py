from pydantic import BaseModel,  Field, EmailStr, root_validator
from typing import Any, Dict, Optional, List
from fastapi import UploadFile, File
from datetime import date, datetime
from enum import Enum
from sqlalchemy import JSON

#######################Company################################
class CompanyCreate(BaseModel):
    name: str


class CompanyUpdate(BaseModel):
    name: str


####################Branch#######################################
class BranchCreate(BaseModel):
    name: str


class BranchUpdate(BaseModel):
    name: str


###################Designation###################################
class DesignationCreate(BaseModel):
    name: str


class DesignationUpdate(BaseModel):
    name: str


#####################Usertype#######################################
class UserTypeCreate(BaseModel):
    name: str


class UserTypeUpdate(BaseModel):
    name: str


####################Student###########################################
class StudentBase(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    date_of_birth: date
    gender: str
    nationality: str
    citizenship_status: str
    date_of_joining: date
    date_of_completion: Optional[date]
    

class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    nationality: Optional[str]
    citizenship_status: Optional[str]
    date_of_joining: Optional[date]
    date_of_completion: Optional[date]
    id_proof: Optional[str]
    address_proof: Optional[str]


class StudentSchema(StudentBase):
    students_id: int



class Student(StudentBase):
    id: int
    user_id: int




    class Config:
        orm_mode = True
class StudentUpdate_all_data(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    referral: Optional[str] = None
    date_of_joining: Optional[date] = None
    date_of_completion: Optional[date] = None
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    student_class: Optional[str] = None
    school: Optional[str] = None
    year_of_passing: Optional[int] = None
    percentage: Optional[float] = None
    p_first_name: Optional[str] = None
    p_middle_name: Optional[str] = None
    p_last_name: Optional[str] = None
    guardian: Optional[str] = None
    

##############################CoureDetails########################
from pydantic import BaseModel

class CourseDetailsCreate(BaseModel):
    subject: str
    standard: str
    module: str
    course: str

class CourseDetailsUpdate(BaseModel):
    subject: str
    standard: str
    module: str
    course: str


##################################user#############################
class LoginInput(BaseModel):
    email: str
    user_password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    class Config:
        from_attributes = True


class UserType(str, Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"
    user = "user"
    parent = "parent"


class UserCreate(BaseModel):
    user_name: str
    user_email: str
    user_password: str
    user_type: UserType = UserType.user
    phone_no: str
    branch_id:int

    class Config:
        from_attributes = True


class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    phone_no: Optional[int] = None
    user_type: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


################################DemoFormFill###############################
class DemoformfillCreate(BaseModel):
    #user_id: int
    name: str
    email_id: str
    contact_no: str
    standard: str
    course: str
    subject:str
    school: str
    teaching_mode: str
    other_info: str


class DemoformfillResponse(BaseModel):
    FormID: int
    GuestId: int
    Name: str
    EmailId: str
    ContactNo: str
    Standard: str
    Course: str
    School: str
    TeachingMode: str
    OtherInfo: str


##############################Parent#################################
class ParentBase(BaseModel):
    p_first_name: str
    p_middle_name: Optional[str]
    p_last_name: str
    guardian: str
    primary_no: str
    secondary_no: Optional[str]
    primary_email: str
    secondary_email: Optional[str]


class ParentCreate(ParentBase):
    pass


class ParentInfoUpdate(ParentBase):
    p_first_name: Optional[str] = None
    p_middle_name: Optional[str] = None
    p_last_name: Optional[str] = None
    guardian: Optional[str] = None
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None


class Parent(ParentBase):
    parent_id: int
    student_id: int

    class Config:
        orm_mode = True
class ParentUpdate(BaseModel):
    p_first_name: Optional[str] = None
    p_middle_name: Optional[str] = None
    p_last_name: Optional[str] = None
    guardian: Optional[str] = None
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None

#########################studentContact#####################################
class StudentContactBase(BaseModel):
    primary_no: str
    secondary_no: Optional[str]
    primary_email: str
    secondary_email: Optional[str]
    current_address: str
    permanent_address: str


class StudentContactCreate(StudentContactBase):
    pass


class StudentContactUpdate(StudentContactBase):
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None


class StudentContact(StudentContactBase):
    student_id: int

    class Config:
        orm_mode = True


#######################StudentEducation######################################
class PreEducationBase(BaseModel):
    student_class: str
    school: str
    year_of_passing: int
    percentage: float


class PreEducationCreate(PreEducationBase):
    pass


class PreEducationUpdate(PreEducationBase):
    student_class: Optional[str] = None
    school: Optional[str] = None
    year_of_passing: Optional[int] = None
    percentage: Optional[float] = None


class PreEducation(PreEducationBase):
    id: int
    student_id: int

    class Config:
        orm_mode = True


############# courses ########################################################


class CourseBase(BaseModel):
    name: str


class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name:str


################## subjects ################################################

class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    name: str

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    standard_id:Optional[int] =None


#############################Standard##########################################
class StandardBase(BaseModel):
    name: str

class StandardCreate(StandardBase):
    name: str


class StandardUpdate(BaseModel):
    name: Optional[str] = None
    course_id:Optional[int] =None


####################Module#########################################
class ModuleBase(BaseModel):
    name: str


class ModuleCreate(ModuleBase):
    name: str

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    subject_id:Optional[int] =None


  
###################Lesson##########################################
class LessonCreate(BaseModel):
    title: str
    description: str

class LessonResponse(BaseModel):
    lesson_id: int
    title: str
    description: str

##############################DemoVideo#############################
# class DemoVideoCreate(BaseModel):
#     title: str
#     url: str
#     course_id: int
#     subject_id: int
#     standard_id: int

class VideoBase(BaseModel):
    name: str
    url: str


class VideoCreate(VideoBase):
    pass


class Video(VideoBase):
    id: int
    course_id: int
    standard_id: int
    subject_id: int

    class Config:
        orm_mode = True


######################################Inquiry##################################################
class InquiryCreate(BaseModel):
    name: str
    email: str
    phone: str
    message: str

class InquiryUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    message: Optional[str]

#####################################fees######################################################
class FeeCreate(BaseModel):
    course_id : int
    standard_id : int
    year : int 
    subject_id : int
    module_id: int 
    batch_id : int
    amount : float 
    

# class FeeUpdate(BaseModel):
#     course_id : int
#     standard_id : int
#     year : int 
#     subject_id : int
#     modules_id : int
#     batch_id : int
#     amount : float 
class FeeUpdate(BaseModel):
    course_id: Optional[int] = None
    standard_id: Optional[int] = None
    year: Optional[int] = None
    subject_id: Optional[int] = None
    modules_id: Optional[int] = None
    batch_id: Optional[int] = None
    amount: Optional[float] = None

###################Batches###################################
class BatchCreate(BaseModel):
    size:str

class BatchUpdate(BaseModel):
    size:str


######################################  paper  Table ##################################################

# Pydantic schema for Paper
class PaperCreate(BaseModel):
    title: str
    description: str
    user_id: int

# Pydantic schema for Paper response
class PaperResponse(BaseModel):
    paper_id: int
    title: str
    description: str
    user_id: int

#########################################################
#####################################  Question ##################################################

class QuestionCreate(BaseModel):
    question_text: str
    question_image: Optional[str] = None
    options1_text: str
    options1_images: Optional[str] = None
    options2_text: str
    options2_images: Optional[str] = None
    options3_text: str
    options3_images: Optional[str] = None
    options4_text: str
    options4_images: Optional[str] = None
    correct_answer_text: str
    correct_answer_image: Optional[str] = None
    difficulty_level: str



from pydantic import BaseModel, Field
from typing import Optional, List

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




class QuestionGetResponse(BaseModel):
    question_id: int
    question_text: str
    question_image: Optional[str] = None
    options1_text: str
    options1_images: Optional[str] = None
    options2_text: str
    options2_images: Optional[str] = None
    options3_text: str
    options3_images: Optional[str] = None
    options4_text: str
    options4_images: Optional[str] = None
    correct_answer_text: str
    correct_answer_image: Optional[str] = None
    given_answer_text: Optional[str] = None  
    given_answer_image: Optional[str] = None  
    difficulty_level: str

###################################### Question  paper Table ##################################################

class QuestionPaperCreate(BaseModel):
    title: str
    description: str
    teacher_id: int
    student_id: int
    subject_id: int
    module_id: int
    lesson_id: int
    test_id: int 


class QuestionPaperResponse(BaseModel):
    id: int
    title: str
    description: str
    teacher_id: int
    student_id: int
    subject_id: int
    module_id: int
    lesson_id: int
    test_id: Optional[int]
######################################  Question  paper with mapping ID ##################################################


# Pydantic schema for QuestionMapping
class QuestionMappingCreate(BaseModel):
    paper_id: int
    question_id: int

class QuestionMappingResponse(BaseModel):
    mapping_id: int
    paper_id: int
    question_id: int

######################################  Test ##################################################

class TestBase(BaseModel):
    description: str
    teacher_id: int
    student_id: int
    lesson_id: int


class TestCreate(TestBase):
    pass


class TestUpdate(TestBase):
    pass


class TestResponse(TestBase):
    test_id: int


######################################  payments ##################################################

# Pydantic schemas for request and response models
class PaymentCreate(BaseModel):
    course_id: int
    standard_id: int
    subject_id: int
    module_id: int
    batch_id: int
    years: Optional[int] = None
    amount: Optional[float] = None
    payment_mode: Optional[str] = None
    payment_info: Optional[str] = None
    other_info: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_id: int
    student_id: int
    course_id: int
    payment_date: date
    amount: float
    payment_status: str
    description: str
######################################  Installmenst ##################################################

class PaymentDetails(BaseModel):
    installment_id: int
    payment_id: int
    total_amount: float
    installment_number: int
    due_dates: List[str]
    installments: List[dict]

class InstallmentResponse(BaseModel):
    installment_id: int
    total_amount: float
    installment_number: int
    installments: str
    due_dates: str
   
    

class Installment(BaseModel):
    installment_id: int
    payment_id: int
    total_amount: float
    installment_number: int
    due_date: date
    installment_amount: float

######################################  contents ##################################################

class ContentCreate(BaseModel):
    name: str
    description: str
    content_type: str
    lesson_id: int

class ContentCreateRequest(BaseModel):
    name: str
    description: str = None
    content_type: str = None
    lesson_id: int
    files:List[UploadFile]= None


######################################  students ##################################################

class StudentSchema(BaseModel):
    
    user_id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    date_of_birth: date
    gender: str
    nationality: str
    citizenship_status: str
    date_of_joining: date
    date_of_completion: Optional[date]

class StudentGetResponse(BaseModel):
    id: int
    user_id: Optional[int] = None  # Make it optional
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    gender: str
    nationality: str
    citizenship_status: str
    date_of_joining: str
    date_of_completion: Optional[str] = None

#  ------------------------------------------------------------------------------------------------------------------
                       #Teacher All data
#  ------------------------------------------------------------------------------------------------------------------


######################### teacher contact info  #####################################

class ContactInformationBase(BaseModel):
    primary_number: str = Field(..., max_length=50)
    secondary_number: str = Field(None, max_length=50)
    primary_email_id: str = Field(..., max_length=50)
    secondary_email_id: str = Field(None, max_length=50)
    current_address: str = Field(..., max_length=255)
    permanent_address: str = Field(..., max_length=255)

class ContactInformationCreate(ContactInformationBase):
    pass

class ContactInformationUpdate(ContactInformationBase):
    pass

######################### teacher education  #####################################

class EducationBase(BaseModel):
    education_level: str
    institution: str
    specialization: str
    field_of_study: str
    year_of_passing: int
    percentage: float

class EducationCreate(EducationBase):
    pass

class EducationUpdate(EducationBase):
    pass

class Education(EducationBase):
    id: int

######################### teacher skills  #####################################
class SkillBase(BaseModel):
    skill: str
    certification: str
    license: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    pass

class Skill(SkillBase):
    id: int

######################### teacher language knowledge  #####################################

class LanguagesSpokenBase(BaseModel):
    languages: str

class LanguagesSpokenCreate(LanguagesSpokenBase):
    pass

class LanguagesSpokenUpdate(LanguagesSpokenBase):
    pass

class LanguagesSpoken(LanguagesSpokenBase):
    id: int

######################### teacher EmergencyContact #####################################

class EmergencyContactBase(BaseModel):
    emergency_contact_name:Optional[str] = None
    relation: Optional[str] = None
    emergency_contact_number: int

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(EmergencyContactBase):
    pass

class EmergencyContact(EmergencyContactBase):
    id: int

######################### teacher depends #####################################
class DependentsBase(BaseModel):
    dependent_name: str
    realtion: str
    date_of_birth: Optional[date]=None
   

class DependentsCreate(DependentsBase):
    pass

class DependentsUpdate(DependentsBase):
    pass


######################### Employee Master Table #####################################
class EmployeeBase(BaseModel):
    f_name: Optional[str] = None
    m_name: Optional[str] = None
    l_name: Optional[str] = None
    dob: date
    gender: str
    nationality: str
    marital_status: str
    citizenship_status: Optional[str] = None
    date_of_hire: Optional[date]
    date_of_termination: Optional[date]=None
   

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass


######################### Manager #####################################

class ManagerBase(BaseModel):
    name: str
    gender: str
    department: str

class ManagerCreate(ManagerBase):
    pass

class ManagerUpdate(ManagerBase):
    pass

class ManagerInDBBase(ManagerBase):
    manager_id: int


######################################  Teacher ##################################################

# Pydantic schema for Teacher
class TeacherCreate(BaseModel):
    name: str
    email: Optional[str] = None
    department: Optional[str] = None

# Pydantic schema for Teacher response
class TeacherResponse(BaseModel):
    Teacher_id: int
    name: str
    email: str
    department: str
    
class TeacherUpdate(BaseModel):
    name: str
    email: str
    department: str


class CourseDetailsResponse(BaseModel):
    subjects: List[int]
    standards: List[int]
    modules: List[int]
    courses: List[int]

class StudentResponse(BaseModel):
    user_id: int
    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: str
    gender: str
    nationality: str
    referral: str
    date_of_joining: str
    date_of_completion: str
    id_proof_url: str
    address_proof_url: str
    contact_info: dict
    pre_education: dict
    parent_info: dict
    course_details: CourseDetailsResponse

######################################  Mail ##################################################
class MailCreate(BaseModel):
    email: Optional[str] = None
    message: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None


######################### teacher put method only #####################################
class ConfigModel(BaseModel):
    class Config:
        from_attributes = True

class TeacherUpdate1(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department:Optional[str] = None

class ContactInfoUpdate(BaseModel):
    primary_number: Optional[str] = None
    secondary_number: Optional[str] = None
    primary_email_id: Optional[str] = None
    secondary_email_id: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

class DependentUpdate(BaseModel):
    dependent_name: Optional[str] = None
    relation: Optional[str] = None
    date_of_birth: Optional[date] = None

class EducationUpdate1(BaseModel):
    education_level: Optional[str] = None
    institution: Optional[str] = None
    specialization: Optional[str] = None
    field_of_study: Optional[str] = None
    year_of_passing: Optional[int] = None
    percentage: Optional[float] = None

class EmergencyContactUpdate1(BaseModel):
    emergency_contact_name: Optional[str] = None
    relation: Optional[str] = None
    emergency_contact_number: Optional[int] = None

class LanguagesSpokenUpdate1(BaseModel):
    languages: Optional[str] = None

class SkillUpdate1(BaseModel):
    skill: Optional[str] = None
    certification: Optional[str] = None
    license: Optional[str] = None

    class Config:
        orm_mode = True

###################################### only for student addmsion put api update ##########################
class StudentUpdate_data(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    referral: Optional[str] = None
    date_of_joining: Optional[date] = None
    date_of_completion: Optional[date] = None

class ContactInfoUpdate_data(BaseModel):
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

class PreEducationUpdate_data(BaseModel):
    student_class: Optional[str] = None
    school: Optional[str] = None
    year_of_passing: Optional[int] = None
    percentage: Optional[float] = None

class ParentInfoUpdate_data(BaseModel):
    p_first_name: Optional[str] = None
    p_middle_name: Optional[str] = None
    p_last_name: Optional[str] = None
    guardian: Optional[str] = None
    primary_no: Optional[str] = None
    primary_email: Optional[EmailStr] = None

#######################################mm create course by admin with Hierarchy  #######################################################################################   
class ModuleCreate1(BaseModel):
    module_name: str

class SubjectCreate1(BaseModel):
    subject_name: str
    modules: List[ModuleCreate1]

class StandardCreate1(BaseModel):
    standard_name: str
    subjects: List[SubjectCreate1]

class CourseCreateWithHierarchy1(BaseModel):
    course_name: str
    description: Optional[str]
    standards: List[StandardCreate1]


################################ for attendence ######################
class AttendanceStatus(str, Enum):
    absent = "absent"
    present = "present"

class AttendanceCreate(BaseModel):
    date: date
    status: AttendanceStatus

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_attendance_status: str
    date: datetime

    class Config:
        orm_mode = True


##################### Razorpay ########################


class InstallmentData(BaseModel):
    installment_number: int
    due_date: date
    amount_due: Optional[float] = None
    # amount: Optional[float] = None  # Accept either one

    @root_validator(pre=True)
    def set_amount_due(cls, values):
        # if amount_due not given, use amount
        if 'amount_due' not in values and 'amount' in values:
            values['amount_due'] = values['amount']
        return values


class CreateOrderRequest(BaseModel):
    course_id: int
    standard_id: int
    subject_id: int
    module_id: int
    batch_id: int
    years: Optional[int] = None
    amount: Optional[float] = None
    discount :Optional[float] = None
    final_amount: Optional[float] = None
    payment_mode: Optional[str] = None
    payment_info: Optional[str] = None
    other_info: Optional[str] = None
    amount: float
    currency: str = "INR"
    receipt: str
    referral_code: Optional[str] = None  
    installments: Optional[int] = 1 
    installment_number: Optional[int] = 1  # Which installment user is paying
    admin_installment_id: Optional[int] = None  # Admin installment ID
    installments_data: List[InstallmentData] = []    
    process_first_installment_only: Optional[bool] = False  # Add this field
    gst: Optional[str] = None
    

class VerifyPaymentRequest(BaseModel):
    installments_data: List[Dict[str, Any]] = []  # Correct way
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


##################### Referral Code ########################


# updated by bhavan kumar

from pydantic import BaseModel
from typing import Optional

class ReferralCodeCreate(BaseModel):
    code: str
    discount_rupees: Optional[int] = 0  # Default to 0
    is_enabled: bool = True  # Default to True

class ReferralCodeResponse(BaseModel):
    status: str
    message: str
    code: str
    discount_rupees: Optional[int] = None
    created_by: Optional[str] = None
    is_enabled: bool




###################################################################################################

from decimal import Decimal

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





class InstallmentInput(BaseModel):
    installment_number: int = Field(..., gt=0, le=3)  # le=3 => max 3 installments
    amount: Decimal = Field(..., gt=0)
    due_date: date


class AdminInstallmentUpdate(BaseModel):  # Changed class name
    number_of_installments: int = Field(..., gt=0, le=3)
    total_amount: Decimal = Field(..., gt=0)
    installments_data: List[InstallmentInput]
    course_id: int
    standard_id: Optional[int] = None
    year: Optional[int] = None
    subject_id: Optional[int] = None
    module_id: Optional[int] = None
    batch_id: Optional[int] = None




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




####################################################################################################


class InstallmentResponse(BaseModel):  # Added InstallmentResponse here
    installment_id: int
    user_id: int
    payment_id: int
    admin_installment_id: int
    installment_number: int
    due_date: date
    installment_amount: float
    total_amount: float
    paid_amount: float
    status: str

    class Config:
        orm_mode = True



    