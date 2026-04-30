from models.ml_task import MLTask, TaskStatus
from models.user import User
from services.crud import balance as BalanceService
from sqlmodel import select

def test_create_ml_task(client, session, ml_model):
    client.post("/auth/signup", json={"username": "user1", "email": "user1@test.ru", "password": "1234"})
    user = session.exec(select(User).where(User.email == "user1@test.ru")).first()
    client.post(f"/api/balance/{user.id}/topup", json={"amount": 10.0})
    
    response = client.post("/api/predict/", json={
        "user_id": user.id,
        "ml_model_id": 1,
        "image_url": "test_image.jpg",
        "manual_text": "Тестовое описание"
    })

    assert response.status_code == 201
    assert "task_id" in response.json()

def test_create_ml_task_without_balance(client, session, ml_model):
    client.post("/auth/signup", json={"username": "user2", "email": "user2@test.ru", "password": "1234"})
    user = session.exec(select(User).where(User.email == "user2@test.ru")).first()
    
    response = client.post("/api/predict/", json={
        "user_id": user.id,
        "ml_model_id": 1,
        "image_url": "test_image.jpg"
    })
    
    assert response.status_code == 400
    assert "Недостаточно средств" in response.json()["detail"]

def test_ml_task_with_deduct_balance(client, session, ml_model):
    client.post("/auth/signup", json={"username": "user3", "email": "user3@test.ru", "password": "1234"})
    user = session.exec(select(User).where(User.email == "user3@test.ru")).first()
    client.post(f"/api/balance/{user.id}/topup", json={"amount": 10.0})
    
    response = client.post("/api/predict/", json={
        "user_id": user.id, "ml_model_id": 1, "image_url": "test.jpg"
    })
    task_id = response.json()["task_id"]
    
    task = session.get(MLTask, task_id)
    task.status = TaskStatus.COMPLETED
    session.add(task)

    BalanceService.deduct_balance(user_id=user.id, amount=5.0, task_id=task_id, session=session)
    session.commit()
    
    balance = BalanceService.get_user_balance(user.id, session)
    assert balance == 5.0

def test_create_ml_task_invalid_model(client):
    response = client.post("/api/predict/", json={
        "user_id": 1,
        "ml_model_id": 93,
        "image_url": "test.jpg"
    })
    assert response.status_code == 404
