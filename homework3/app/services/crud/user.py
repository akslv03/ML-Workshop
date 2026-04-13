from models.user import User
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional

def get_all_users(session: Session) -> List[User]:
    """
    Получает список всех пользователей из базы данных.
    Автоматически подгружает связанные с пользователями задачи и транзакции.

    Args:
        session (Session): Сессия базы данных SQLModel.

    Returns:
        List[User]: Список всех найденных пользователей.
    """
    try:
        statement = select(User).options(
            selectinload(User.tasks),
            selectinload(User.transactions)
        )
        users = session.exec(statement).all()
        return users
    except Exception:
        raise

def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    """
    Ищет пользователя по его уникальному ID.
    Автоматически подгружает связанные задачи и транзакции.

    Args:
        user_id (int): Идентификатор пользователя.
        session (Session): Сессия базы данных SQLModel.

    Returns:
        Optional[User]: Объект пользователя, если он найден, иначе None.
    """
    try:
        statement = select(User).where(User.id == user_id).options(
            selectinload(User.tasks),
            selectinload(User.transactions)
        )
        user = session.exec(statement).first()
        return user
    except Exception:
        raise

def get_user_by_email(email: str, session: Session) -> Optional[User]:
    """
    Ищет пользователя по его email.
    Автоматически подгружает связанные задачи и транзакции.

    Args:
        email (str): Email пользователя для поиска.
        session (Session): Сессия базы данных SQLModel.

    Returns:
        Optional[User]: Объект пользователя, если он найден, иначе None.
    """
    try:
        statement = select(User).where(User.email == email).options(
            selectinload(User.tasks),
            selectinload(User.transactions)
        )
        user = session.exec(statement).first()
        return user
    except Exception:
        raise

def create_user(user: User, session: Session) -> User:
    """
    Сохраняет нового пользователя в базу данных.

    Args:
        user (User): Объект пользователя, который нужно сохранить.
        session (Session): Сессия базы данных SQLModel.

    Returns:
        User: Созданный пользователь с обновленным ID из базы данных.
    """
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise

def delete_user(user_id: int, session: Session) -> bool:
    """
    Удаляет пользователя из базы данных по его ID.

    Args:
        user_id (int): Идентификатор пользователя, которого нужно удалить.
        session (Session): Сессия базы данных SQLModel.

    Returns:
        bool: True, если пользователь успешно удален. False, если пользователь не найден.
    """
    try:
        user = get_user_by_id(user_id, session)
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
