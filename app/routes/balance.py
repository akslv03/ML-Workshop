from fastapi import APIRouter, HTTPException, status, Depends, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database.database import get_session
from models.transaction import Transaction
from services.crud import balance as BalanceService
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

balance_route = APIRouter()

class TopUpRequest(BaseModel):
    amount: float

@balance_route.get(
    "/{user_id}",
    summary="Get user balance"
    )

async def get_balance(user_id: int, session=Depends(get_session)) -> Dict[str, float]:
    """Возвращает текущий баланс пользователя"""
    try:
        current_balance = BalanceService.get_user_balance(user_id, session)
        return {"user_id": user_id, "balance": current_balance}
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting balance")
    
@balance_route.post(
        "/{user_id}/topup",
        summary="Top up balance"
)
async def top_up(user_id: int, request: TopUpRequest, session=Depends(get_session)) -> Dict[str, str]:
    """Пополняет баланс на указанную сумму"""
    try:
        BalanceService.top_up_balance(user_id, request.amount, session)
        return {"message": f"Successfully toped up balance by {request.amount}"}
    except ValueError as ve:
        logger.warning(f"Validation error during topup: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during topup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@balance_route.post(
    "/{user_id}/topup/web",
    summary="Top up balance from web form"
)
async def top_up_web(user_id: int, amount: float = Form(...), session=Depends(get_session)):
    try:
        BalanceService.top_up_balance(user_id, amount, session)
        return RedirectResponse(
            url=f"/private?user_id={user_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as ve:
        logger.warning(f"Validation error during topup: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during topup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



