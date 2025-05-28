from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import (companies_router, branches_router, usertypes_router, modules_router, designations_router,
                           users_router,  demo_router, demovideos_router, subjects_router,lessons_router,
                           standards_router, courses_router, admission_router, inquiry_router,payments_router,content_router,
                           batches_router, fees_router,  parents_router, teachers_Data_router,installments_router,mail_router,announcement_router, 
                           teacher_course_router,course_active, google_map_router, attendances_router, discount_assement_router, lesson_test_router,razor_payment_processing,
                           referal_code_router,social_auth_router,admin_installment_router
)

##################################################################################
                # for swagger security
#################################################################################
from typing import Sequence, Any
from fastapi import FastAPI, Request, Depends, HTTPException, status, APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import secrets
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

####################################################################################
                        #for google login
###################################################################################
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse,JSONResponse
from sqlalchemy.orm import Session
import secrets
import logging
from api.models.user import LmsUsers
from db.session import get_db
##################################################################################
from db.base import Base
from db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

###################################################################################
                        # for Swagger security all code
##################################################################################

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    is_admin: bool = False

USERS_DB = {
    "vinay": {"username": "vinay", "password": "vinay231", "is_admin": True},
    
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for sessions
SECRET_KEY = secrets.token_urlsafe(32)
SESSIONS = {}
SESSION_DURATION = 1

def authenticate_user(username: str, password: str):
    user = USERS_DB.get(username)
    if not user or user["password"] != password:
        return False
    return user

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return User(**SESSIONS[session_id])

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}

@app.get("/swagger", response_class=HTMLResponse)
async def login_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .login-container {
                background-color: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 300px;
            }
            h2 {
                text-align: center;
                color: #1a73e8;
                margin-bottom: 1.5rem;
            }
            form {
                display: flex;
                flex-direction: column;
            }
            input {
                margin-bottom: 1rem;
                padding: 0.5rem;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 1rem;
            }
            input[type="submit"] {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 0.7rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
                transition: background-color 0.3s;
            }
            input[type="submit"]:hover {
                background-color: #155cbd;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Login</h2>
            <form action="/swagger" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="submit" value="Log In">
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/swagger")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    session_id = secrets.token_urlsafe(32)
    SESSIONS[session_id] = user
    response = RedirectResponse(url="/docs", status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(request: Request):
    current_user = get_current_user(request)
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return JSONResponse(get_openapi(title="FastAPI", version="1.0.0", routes=app.routes))

@app.get("/docs", include_in_schema=False)
async def get_documentation(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return RedirectResponse(url="/swagger")
    current_user = User(**SESSIONS[session_id])
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


app.mount("/static", StaticFiles(directory="static"), name="static")

#################################################################################
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


app.include_router(companies_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(branches_router, prefix="/api")
app.include_router(google_map_router, prefix="/api")
app.include_router(courses_router, prefix="/api", tags=["Admin Routes"])
app.include_router(standards_router, prefix="/api", tags=["Admin Routes"])
app.include_router(subjects_router, prefix="/api", tags=["Admin Routes"])
app.include_router(modules_router, prefix="/api", tags=["Admin Routes"])
app.include_router(lessons_router, prefix="/api", tags=["Admin Routes"])
app.include_router(content_router, prefix="/api", tags=["Admin Routes"])
app.include_router(batches_router, prefix="/api", tags=["Admin Routes"])
app.include_router(announcement_router, prefix="/api", tags=["Admin Routes"])
app.include_router(teacher_course_router, prefix="/api", tags=["Admin Routes"])
app.include_router(demo_router, prefix="/api", tags=["Student Routes"])
app.include_router(demovideos_router, prefix="/api", tags=["Student Routes"])
app.include_router(inquiry_router, prefix="/api", tags=["Student Routes"])
app.include_router(fees_router, prefix="/api", tags=["Student Routes"])
app.include_router(payments_router, prefix="/api", tags=["Student Routes"])
app.include_router(installments_router, prefix="/api", tags=["Student Routes"])
app.include_router(mail_router, prefix="/api", tags=["Student Routes"])
app.include_router(course_active, prefix="/api", tags=["Student Routes"])
app.include_router(attendances_router, prefix="/api", tags=["Student Routes"])
app.include_router(discount_assement_router, prefix="/api", tags=["Discount Routes"])
app.include_router(lesson_test_router, prefix="/api", tags=["lesson test Routes"])
app.include_router( parents_router, prefix="/api", tags=["parent_&_Admin Routes"])
app.include_router(teachers_Data_router, prefix="/api", tags=["Teacher_&_Admin Routes"])
app.include_router(admission_router, prefix="/api", tags=["Student_&_Admin Routes"])
app.include_router(razor_payment_processing, prefix="/api", tags=["razor payment processing Routes"])
app.include_router(referal_code_router, prefix="/api", tags=["referal code Routes"])
app.include_router(admin_installment_router, prefix="/api", tags=["admin installment Routes"])

app.include_router(social_auth_router)




##################################################################################################################
                        #for google login
##################################################################################################################

SECRET_KEY = "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"
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

oauth = OAuth()
oauth.register(
    name='google',
    client_id="1060983306336-bg15c4kcvbd51jjj0p08pd68rp7uis6l.apps.googleusercontent.com",
    client_secret="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",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid profile email'}
)

@app.get("/login11")
async def google_login(request: Request):
    redirect_uri = request.url_for('auth')
    logging.info(f"Redirect URI for Google login: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

logging.basicConfig(level=logging.INFO)

@app.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        logging.info(f"Token retrieved: {token}")
        print("Token:", token)
        
        if 'id_token' not in token:
            print("ID token not found in the token response:", token)
            logging.error("ID token not found in the token response")
            raise HTTPException(status_code=400, detail="ID token not found in the token response")
        
        user_info = await oauth.google.parse_id_token(request, token)
        logging.info(f"User information: {user_info}")
        print("User Information:", user_info)

        db_user = db.query(LmsUsers).filter(LmsUsers.user_email == user_info['email']).first()
        if not db_user:
            db_user = LmsUsers(
                email=user_info['email'],
                name=user_info['name'],
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)  
            logging.info(f"New user created: {db_user}")

        return RedirectResponse(url="/")
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=400, detail="Google authentication failed")

########################################################################################################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8006, reload=True, host="0.0.0.0")


    # uvicorn main:app --port 8007 --reload --host 0.0.0.0 --reload