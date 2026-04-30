from sqlmodel import select
from models.transaction import TransactionType
from models.user import User

def test_get_history(client, session, ml_model):
    client.post("/auth/signup", json={"username": "user", "email": "user@test.ru", "password": "1234"})
    user = session.exec(select(User).where(User.email == "user@test.ru")).first()
    client.post(f"/api/balance/{user.id}/topup", json={"amount": 20.0})
    
    predict_response = client.post("/api/predict/", json={
        "user_id": user.id, "ml_model_id": ml_model.id, "image_url": "test.jpg"
    })
    task_id = predict_response.json()["task_id"]

    tasks_response = client.get(f"/api/history/{user.id}/tasks")
    assert tasks_response.status_code == 200
    assert len(tasks_response.json()) == 1
    assert tasks_response.json()[0]["id"] == task_id

    transaction_response = client.get(f"/api/history/{user.id}/transactions")
    assert transaction_response.status_code == 200
    transactions = transaction_response.json()
    assert len(transactions) >= 1
    assert transactions[0]["type"] == TransactionType.CREDIT.value
