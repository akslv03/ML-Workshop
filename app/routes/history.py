from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database.database import get_session
from models.ml_task import MLTask
from models.transaction import Transaction
from services.crud import balance as BalanceService
from services.crud import ml_task as TaskService
from typing import List, Optional
from auth.authenticate import authenticate_cookie
from services.crud import user as UserService
import logging

logger = logging.getLogger(__name__)
history_route = APIRouter()
templates = Jinja2Templates(directory="view")

@history_route.get("/page", response_class=HTMLResponse)
async def history_page(
    request: Request,
    user_email: str = Depends(authenticate_cookie),
    session=Depends(get_session)
):
    user = UserService.get_user_by_email(user_email, session)
    if user is None:
        return RedirectResponse(
            url="/auth/login",
            status_code=303
        )

    transactions = BalanceService.get_user_transactions(user.id, session)
    tasks = TaskService.get_user_tasks(user.id, session)

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "transactions": transactions,
            "tasks": tasks,
            "user_id": user.id,
            "user": user
        }
    )

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