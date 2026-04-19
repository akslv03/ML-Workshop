from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from typing import List
import logging

logger = logging.getLogger(__name__)

user_route = APIRouter()

@user_route.get(
    "/",
    response_model=List[User],
    summary="Get all users",
    response_description="List of all users"
)
async def get_all_users(session=Depends(get_session)) -> List[User]:
    """
    Get list of all users.

    Args:
        session: Database session

    Returns:
        List[UserResponse]: List of users
    """
    try:
        users = UserService.get_all_users(session)
        logger.info(f"Retrieved {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )
