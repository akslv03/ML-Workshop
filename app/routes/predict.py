from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from database.database import get_session
from models.ml_task import MLTask
from models.ml_model import MLModel
from services.crud import balance as BalanceService
from services.crud import ml_task as TaskService
from typing import Optional, List
import logging
from datetime import datetime
from services.rm.rm import send_task

logger = logging.getLogger(__name__)

predict_route = APIRouter()

class PredictRequest(BaseModel):
    user_id: int
    ml_model_id: int
    image_url: str
    manual_text: Optional[str] = None

@predict_route.post(
    "/",
    # response_model=MLTask,
    status_code=status.HTTP_201_CREATED,
    summary="Generate ML task"
)
async def generate_description(request: PredictRequest, session=Depends(get_session)):
    """
    Создает задачу, списывает баланс, отправляет задачу в RabbitMQ
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

        # saved_task.run_task()

        session.add(saved_task)
        session.commit()
        session.refresh(saved_task)

        message = {
            "task_id": saved_task.id,
            "features": {
                "x1": request.image_url,
                "x2": request.manual_text
            },
            "model": model.name,
            "timestamp": datetime.utcnow().isoformat()
        }

        send_task(message)

        logger.info(f"Task {saved_task.id} sent to RabbitMQ successfully for user {request.user_id}")
        return {
            "task_id": saved_task.id, 
            "status": saved_task.status
        }

    except ValueError as ve:
        logger.warning(f"Validation error during task creation: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing task to RabbitMQ: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@predict_route.get(
    "/{task_id}",
    response_model=MLTask,
    summary="Get ML task status by task_id"
)
async def get_task_status(task_id: int, session=Depends(get_session)) -> MLTask:
    """Возвращает информацию по одной ML-задаче по её task_id"""
    try:
        task = session.get(MLTask, task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting task status"
        )