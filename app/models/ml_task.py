from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum

if TYPE_CHECKING:
    from .user import User
    from .ml_model import MLModel
    from .transaction import Transaction

class TaskStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class MLTask(SQLModel, table=True):
    """
    Модель для представления задачи на генерацию описания для одного товара.
    
    Attributes:
        id (Optional[int]): Первичный ключ задачи
        user_id (int): Идентификатор пользователя, создавшего задачу
        ml_model_id (int): Идентификатор используемой ML-модели
        image_url (str): Ссылка на фотографию товара
        manual_text (Optional[str]): Дополнительная текстовая подсказка от пользователя
        status (TaskStatus): Текущий статус выполнения задачи (по умолчанию CREATED)
        result_text (Optional[str]): Итоговое сгенерированное описание товара
        created_at (datetime): Дата и время создания задачи
        
    Relationships:
        user (User): Связь с пользователем
        ml_model (MLModel): Связь с используемой моделью
        transactions (List[Transaction]): Список транзакций (списаний средств) по этой задаче
    """
    __tablename__ = "ml_task"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    ml_model_id: int = Field(foreign_key="ml_model.id")
    image_url: str
    manual_text: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.CREATED)
    result_text: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="tasks")
    ml_model: "MLModel" = Relationship(back_populates="tasks")
    transactions: List["Transaction"] = Relationship(back_populates="task")

    def __str__(self) -> str:
        return f"Task Id: {self.id}. Status: {self.status.value}"
    
    def validate_inputs(self) -> bool:
        """Проверяет корректность переданных входных данных перед запуском."""
        if not self.image_url and not self.manual_text:
            raise ValueError("Нужно передать либо image_url, либо manual_text")
        return True

    # def run_task(self) -> None:
    #     """Запускает обработку задачи моделью и обновляет статус."""
    #     self.validate_inputs()
    #     self.status = TaskStatus.IN_PROGRESS
        
    #     self.result_text = "Готовое описание вашего товара."
    #     self.status = TaskStatus.COMPLETED


    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
