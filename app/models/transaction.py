from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import enum

if TYPE_CHECKING:
    from .user import User
    from .ml_task import MLTask

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class Transaction(SQLModel, table=True):
    """
    Модель для учета транзакций в системе.

    Attributes:
        id (Optional[int]): Первичный ключ транзакции
        user_id (int): Идентификатор пользователя, которому принадлежит транзакция
        task_id (Optional[int]): Идентификатор задачи, за которую было списание
        amount (float): Сумма транзакции
        type (TransactionType): Тип транзакции (debit - списание, credit - пополнение)
        created_at (datetime): Дата и время проведения транзакции
    Relashionships: 
        user (User): Связь с пользователем, совершившим транзакцию
        task (Optional["MLTask"]): Связь с задачей, если транзакция является списанием за генерацию описания
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    task_id: Optional[int] = Field(default=None, foreign_key="ml_task.id", index=True)
    
    amount: float
    type: TransactionType
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    user: "User" = Relationship(back_populates="transactions")
    task: Optional["MLTask"] = Relationship(back_populates="transactions")
    
    def __str__(self) -> str:
        return f"Transaction Id: {self.id}. Type: {self.type.value}. Amount: {self.amount}"

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
