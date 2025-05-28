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

router = APIRouter()

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
    "user": {"username": "user", "password": "userpass", "is_admin": False}
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

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}

@router.get("/login", response_class=HTMLResponse)
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
            <form action="/login" method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="submit" value="Log In">
            </form>
        </div>
    </body>
    </html>
    """

@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    session_id = secrets.token_urlsafe(32)
    SESSIONS[session_id] = user
    response = RedirectResponse(url="/docs", status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@router.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(request: Request):
    current_user = get_current_user(request)
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return JSONResponse(get_openapi(title="FastAPI", version="1.0.0", routes=router.routes))

@router.get("/docs", include_in_schema=False)
async def get_documentation(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return RedirectResponse(url="/login")
    current_user = User(**SESSIONS[session_id])
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")