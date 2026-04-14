from database.config import get_settings
from database.database import init_db, get_database_engine
from services.crud.user import get_all_users, create_user
from services.crud.balance import top_up_balance, deduct_balance, get_user_balance
from services.crud.ml_task import create_task
from sqlmodel import Session, select
from models.user import User, UserRole
from models.ml_model import MLModel
from models.ml_task import MLTask, TaskStatus
from models.transaction import Transaction, TransactionType

if __name__ == "__main__":
    settings = get_settings()
    print(settings.APP_NAME)
    print(settings.API_VERSION)
    print(f'Debug: {settings.DEBUG}')
    
    print(settings.DB_HOST)
    print(settings.DB_NAME)
    print(settings.DB_USER)
    
    init_db(drop_all=True)
    print('Init db has been success')
    
    # test_user = User(username='test1', email='test1@gmail.com', password='test', role=UserRole.CLIENT)
    test_user_2 = User(username='test2', email='test2@gmail.com', password='test', role=UserRole.CLIENT)
    test_user_3 = User(username='test3', email='test3@gmail.com', password='test', role=UserRole.CLIENT)
    
    engine = get_database_engine()
    
    with Session(engine) as session:
        # create_user(test_user, session)
        create_user(test_user_2, session)
        create_user(test_user_3, session)
        
        base_model = session.exec(select(MLModel)).first()
        test_user = session.exec(select(User).where(User.email == "demo@client.com")).first()
        
        test_task = MLTask(
            user_id=test_user.id,
            ml_model_id=base_model.id,
            image_url='test_url',
            manual_text='test_manual_input',
            status=TaskStatus.COMPLETED,
            result_text='test_generated_description'
        )
        create_task(test_task, session)
        
        deduct_balance(user_id=test_user.id, amount=base_model.cost_per_prediction, task_id=test_task.id, session=session)
        
        users = get_all_users(session)
        
    print('-------')
    print(f'Id локального пользователя: {id(test_user)}')
    
    db_user = next(u for u in users if u.email == 'demo@client.com')
    print(f'Id пользователя из БД: {id(db_user)}')
    print(f'Id одинаковые: {id(test_user) == id(db_user)}')

    print('-------')
    print('Пользователи из БД:')        
    for user in users:
        print(user)
        print(f"Баланс: {get_user_balance(user.id, session)}")
        
        print('Пользовательские задачи:')
        if len(user.tasks) == 0:
            print('Пользователь не имеет задач')
        else:
            for task in user.tasks:
                print(task)
                
        print('Пользовательские транзакции:')
        if len(user.transactions) == 0:
            print('Пользователь не имеет транзакций')
        else:
            for transaction in user.transactions:
                print(transaction)