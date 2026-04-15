from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from pydantic import BaseModel, EmailStr
from typing import Dict
import logging

logger = logging.getLogger(__name__)

auth_route = APIRouter()

class UserSignup(BaseModel):
     username: str
     email: str
     password: str

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
        new_user = User(username=data.username, email=data.email, password=data.password)
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
