from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from database.database import get_session
from models.ml_task import MLTask
from models.ml_model import MLModel
from services.crud import balance as BalanceService
from services.crud import ml_task as TaskService
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

predict_route = APIRouter()

class PredictRequest(BaseModel):
    user_id: int
    ml_model_id: int
    image_url: str
    manual_text: Optional[str] = None

@predict_route.post(
    "/generate",
    response_model=MLTask,
    status_code=status.HTTP_201_CREATED,
    summary="Generate product description"
)
async def generate_description(request: PredictRequest, session=Depends(get_session)) -> MLTask:
    """
    Создает задачу на генерацию, списывает баланс и запускает заглушку ML-модели.
    """
    try:
        model = session.get(MLModel, request.ml_model_id)
        if not model:
            logger.warning(f"Model with ID {request.ml_model_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")

        new_task = MLTask(
            user_id=request.user_id,
            ml_model_id=request.ml_model_id,
            image_url=request.image_url,
            manual_text=request.manual_text
        )

        saved_task = TaskService.create_task(new_task, session)

        BalanceService.deduct_balance(
            user_id=request.user_id, 
            amount=model.cost_per_prediction, 
            task_id=saved_task.id, 
            session=session
        )

        saved_task.run_task()

        session.add(saved_task)
        session.commit()
        session.refresh(saved_task)

        logger.info(f"Task {saved_task.id} completed successfully for user {request.user_id}")
        return saved_task

    except ValueError as ve:
        logger.warning(f"Validation error during generation: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")