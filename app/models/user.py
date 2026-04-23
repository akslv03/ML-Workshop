from sqlmodel import SQLModel, Field, Relationship
from auth.hash_password import HashPassword
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum
import re

if TYPE_CHECKING:
    from .ml_task import MLTask
    from .transaction import Transaction

class UserRole(str, enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"

class User(SQLModel, table=True):
    """
    Модель для представления пользователя в системе.

    Attributes:
        id (Optional[int]): Первчиный ключ пользователя
        username (str): Имя пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        role (UserRole): Роль в системе
        created_at (datetime): Дата и время регистрации пользователя
    Relationships:
        tasks (List[MLTask]): Список задач на генерацию описаний, созданных пользователем
        transactions (List[Transaction]): История пополнений и списаний баланса пользователя
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True) 
    email: str = Field(
        ...,
        unique=True,
        index=True,
        min_length=5,
        max_length=255
    )
    password: str = Field(..., min_length=4)
    role: UserRole = Field(default=UserRole.CLIENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["MLTask"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )
    transactions: List["Transaction"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )

    def __str__(self) -> str:
        return f"Id: {self.id}. Username: {self.username}. Email: {self.email}"

    def _validate_email(self) -> bool:
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not pattern.match(self.email):
            raise ValueError("Invalid email format")
        return True

    def check_password(self, input_password: str) -> bool:
        """Проверяет пароль при авторизации пользователя."""
        return HashPassword().verify_hash(input_password, self.password)
        
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
