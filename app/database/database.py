from sqlmodel import SQLModel, Session, create_engine, select
from contextlib import contextmanager
from .config import get_settings
from models.user import User, UserRole
from models.ml_model import MLModel
from models.ml_task import MLTask, TaskStatus
from models.transaction import Transaction, TransactionType
from services.crud.balance import top_up_balance

def get_database_engine():
    """
    Create and configure the SQLAlchemy engine.
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    settings = get_settings()
    
    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

engine = get_database_engine()

def get_session():
    with Session(engine) as session:
        yield session
        
def init_db(drop_all: bool = False) -> None:
    try:
        engine = get_database_engine()
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            default_model = session.exec(select(MLModel).where(MLModel.name == "llava:7b")).first()
            if not default_model:
                default_model = MLModel(
                    name="llava:7b",
                    description="Анализирует фото этикетки товара и дополнительный текст для генерации описания товара для маркетплейсов",
                    cost_per_prediction=5.0
                )
                session.add(default_model)
                print("Создана базовая ML-модель: llava:7b")

            admin = session.exec(select(User).where(User.email == "admin@market.com")).first()
            if not admin:
                admin = User(
                    username="AdminUser",
                    email="admin@market.com",
                    password="secure_admin_pass",
                    role=UserRole.ADMIN
                )
                session.add(admin)
                print("Создан демо-администратор.")

            demo_user = session.exec(select(User).where(User.email == "demo@client.com")).first()
            if not demo_user:
                demo_user = User(
                    username="DemoClient",
                    email="demo@client.com",
                    password="demo_password",
                    role=UserRole.CLIENT
                )
                session.add(demo_user)
                session.commit()
                session.refresh(demo_user)
                

                top_up_balance(user_id=demo_user.id, amount=100.0, session=session)
                print(f"Создан демо-пользователь (ID: {demo_user.id}) со стартовым балансом 100.0.")
            
            session.commit()
            print("База данных успешно инициализирована.")
            
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
        raise