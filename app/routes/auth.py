from fastapi import APIRouter, HTTPException, status, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token
from database.config import get_settings
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from pydantic import BaseModel, Field
from typing import Dict
from auth.hash_password import HashPassword
import logging

logger = logging.getLogger(__name__)

auth_route = APIRouter()
templates = Jinja2Templates(directory="view")
hash_password = HashPassword()
settings = get_settings()

@auth_route.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session)
) -> Dict[str, str]:
    user = UserService.get_user_by_email(form_data.username, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )

    if not hash_password.verify_hash(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(user.email)

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )

    return {
        settings.COOKIE_NAME: access_token,
        "token_type": "bearer"
    }

@auth_route.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )

@auth_route.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"error": None}
    )

@auth_route.post("/signup/web", response_class=HTMLResponse)
async def signup_web(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session=Depends(get_session)
):
    try:
        if UserService.get_user_by_email(email, session):
            return templates.TemplateResponse(
                request=request,
                name="signup.html",
                context={
                    "error": "Пользователь с таким email уже существует"
                }
            )

        hashed_password = hash_password.create_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        UserService.create_user(new_user, session)

        return RedirectResponse(
            url="/auth/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:
        logger.error(f"Error during web signup: {str(e)}")
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "error": "Ошибка при регистрации"
            }
        )

@auth_route.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session=Depends(get_session)
):
    user = UserService.get_user_by_email(email, session)

    if user is None or not user.check_password(password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Неверный email или пароль"
            }
        )
    response = RedirectResponse(
        url="/private",
        status_code=status.HTTP_303_SEE_OTHER
    )
    access_token = create_access_token(user.email)
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True
    )
    return response

class UserSignup(BaseModel):
     username: str
     email: str
     password: str = Field(..., min_length=4)

class UserSignin(BaseModel):
     email: str
     password: str

@auth_route.post(
    '/signup',
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    description="Register a new user with email and password"
)
async def signup(data: UserSignup, session=Depends(get_session)) -> Dict[str, str]:
    """
    Create new user account.

    Args:
        data: User registration data
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If user already exists
    """
    try:
        if UserService.get_user_by_email(data.email, session):
                logger.warning(f"Signup attempt with existing email: {data.email}")
                raise HTTPException(
                     status_code=status.HTTP_409_CONFLICT,
                     detail="User with this email already exists"
                )
        hasher = HashPassword()
        hashed_password = hasher.create_hash(data.password)

        new_user = User(username=data.username, email=data.email, password=hashed_password)
        UserService.create_user(new_user, session)

        logger.info(f"New user registered: {data.email}")
        return {"message": "User successfully registered"}
    except HTTPException:
         raise
    except Exception as e:
         logger.error(f"Error during signup: {str(e)}")
         raise HTTPException(
              status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Error creating user"
         )

@auth_route.post(
          '/signin',
          response_model=Dict[str, str],
          summary="User login"
)
async def signin(data: UserSignin, session=Depends(get_session)) -> Dict[str, str]:
    """
    Authenticate existing user.

    Args:
        form_data: User credentials
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If authentication fails
    """
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        logger.warning(f"Login attempt with non-existent email: {data.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if not user.check_password(data.password):
        logger.warning(f"Failed login attempt for user: {data.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed")
    
    return {"message": "User signed in successfully"}

@auth_route.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie(settings.COOKIE_NAME)
    return response