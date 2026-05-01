from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session
from database.database import get_session
from services.crud import balance as BalanceService
from auth.authenticate import authenticate_cookie
from services.crud import user as UserService
from services.crud import ml_task as TaskService
from models.ml_model import MLModel
from services.crud import ml_model as MLModelService

home_route = APIRouter()
templates = Jinja2Templates(directory="view")

@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@home_route.get("/private", response_class=HTMLResponse)
async def private_page(
    request: Request,
    user_email: str = Depends(authenticate_cookie),
    error: Optional[str] = None,
    success: Optional[str] = None,
    session: Session = Depends(get_session)
):
    user = UserService.get_user_by_email(user_email, session)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=303)

    balance = BalanceService.get_user_balance(user.id, session)
    tasks = TaskService.get_user_tasks(user.id, session)
    last_task = tasks[0] if tasks else None
    ml_models = MLModelService.get_all_models(session)

    return templates.TemplateResponse(
        request=request,
        name="private.html",
        context={
            "user": user,
            "balance": balance,
            "error": error,
            "success": success,
            "last_task": last_task,
            "ml_models": ml_models
        }
    )

@home_route.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={}
    )

@home_route.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check endpoint",
    description="Returns service health status"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Dict[str, str]: Health status message
    
    Raises:
        HTTPException: If service is unhealthy
    """
    try:
        return {"status":"healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )