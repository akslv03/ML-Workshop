from models.ml_task import MLTask, TaskStatus
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List

def create_task(task: MLTask, session: Session) -> MLTask:
    """Создает новую задачу на генерацию описания."""
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except Exception:
        session.rollback()
        raise

def get_user_tasks(user_id: int, session: Session) -> List[MLTask]:
    """
    Получение истории задач пользователя.
    Сортировка по дате (от новых к старым) и подгрузка связанной ML-модели.
    """
    try:
        statement = (
            select(MLTask)
            .where(MLTask.user_id == user_id)
            .order_by(MLTask.created_at.desc())
            .options(selectinload(MLTask.ml_model))
        )
        tasks = session.exec(statement).all()
        return tasks
    except Exception:
        raise