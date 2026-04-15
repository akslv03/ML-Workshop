from fastapi import APIRouter, HTTPException, Depends
from database.database import get_session
from models.ml_task import MLTask
from models.transaction import Transaction
from services.crud import balance as BalanceService
from services.crud import ml_task as TaskService
from typing import List
import logging

logger = logging.getLogger(__name__)
history_route = APIRouter()

@history_route.get(
    "/{user_id}/transactions",
    response_model=List[Transaction],
    summary="Get transaction history",
)
async def get_transaction_history(user_id: int, session=Depends(get_session)) -> List[Transaction]:
    """Возвращает историю всех транзакций пользователя"""
    try:
        return BalanceService.get_user_transactions(user_id, session)
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting transaction history")
    
@history_route.get(
    "/{user_id}/tasks",
    response_model=List[MLTask],
    summary="Get user ML tasks history"
)
async def get_tasks_history(user_id: int, session=Depends(get_session)) -> List[MLTask]:
    """Возвращает историю всех задач на генерацию описаний для пользователя"""
    try:
        return TaskService.get_user_tasks(user_id, session)
    except Exception as e:
        logger.error(f"Error getting tasks history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting tasks history")