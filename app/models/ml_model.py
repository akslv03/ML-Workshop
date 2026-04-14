from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .ml_task import MLTask

class MLModel(SQLModel, table=True):
    """
    Модель для представления доступных ML-моделей для генерации описаний.
    
    Attributes:
        id (int): Первичный ключ
        name (str): Уникальное название модели
        description (str): Описание возможностей модели
        cost_per_prediction (float): Стоимость одной генерации в кредитах
        tasks (List[MLTask]): Список задач, выполненных этой моделью
    """
    __tablename__ = "ml_model"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    cost_per_prediction: float

    tasks: List["MLTask"] = Relationship(back_populates="ml_model")
    
    def __str__(self) -> str:
        return f"Model Id: {self.id}. Name: {self.name}"
    
    def predict(self, image_url: str, manual_text: Optional[str] = None) -> str:
        """
        Выполняет генерацию описания по входным данным. 
        Принимает на вход фотографию этикетки + название товара текстом (если требуется).
        """
        if manual_text:
            return f"Описание сгенерировано по картинке ({image_url}) с учетом ручной подсказки: '{manual_text}'"
        else:
            return f"Описание сгенерировано по картинке ({image_url})"

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
