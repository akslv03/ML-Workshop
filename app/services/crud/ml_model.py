from sqlmodel import Session, select
from models.ml_model import MLModel
from typing import List

def get_all_models(session: Session) -> List[MLModel]:
    """Получить все доступные ML модели"""
    return session.exec(select(MLModel)).all()
