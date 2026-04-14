from models.user import User
from models.transaction import Transaction, TransactionType
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List

def top_up_balance(user_id: int, amount: float, session: Session) -> Transaction:
    """
    Пополнение баланса пользователя.
    Создает транзакцию типа CREDIT.
    """
    try:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть больше нуля")
        
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=TransactionType.CREDIT
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception:
        session.rollback()
        raise

def deduct_balance(user_id: int, amount: float, task_id: int, session: Session) -> Transaction:
    """
    Списание кредитов за ML-задачу.
    Проверяет баланс перед списанием.
    """
    try:
        if amount <= 0:
            raise ValueError("Сумма списания должна быть больше нуля")
        
        user = session.get(User, user_id)
        
        if not user:
            raise ValueError("Пользователь не найден")
        
        current_balance = get_user_balance(user_id, session)
        if current_balance < amount:
            raise ValueError(f"Недостаточно средств. Текущий баланс: {current_balance}")
            
        transaction = Transaction(
            user_id=user_id,
            task_id=task_id,
            amount=amount,
            type=TransactionType.DEBIT
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception:
        session.rollback()
        raise

def get_user_transactions(user_id: int, session: Session) -> List[Transaction]:
    """
    Получение истории транзакций пользователя.
    Сортировка по дате (от новых к старым) и подгрузка связанной ML-задачи.
    """
    try:
        statement = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .options(selectinload(Transaction.task))
        )
        transactions = session.exec(statement).all()
        return transactions
    except Exception as e:
        raise

def get_user_balance(user_id: int, session: Session) -> float:
    """
    Вычисление текущего баланса пользователя.
    Суммирует все CREDIT и вычитает все DEBIT.
    """
    credit_query = select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.CREDIT
    )
    sum_credit = session.exec(credit_query).first()

    debit_query = select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.DEBIT
    )
    sum_debit = session.exec(debit_query).first()

    return sum_credit - sum_debit

