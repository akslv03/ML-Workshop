from models.user import User
from sqlmodel import select

def test_balance_operations(client, session):
    client.post("/auth/signup", json={
        "username": "tester_balance",
        "email": "user@test.ru",
        "password": "password123"
    })
    
    user = session.exec(select(User).where(User.email == "user@test.ru")).first()
    
    current_balance = client.get(f"/api/balance/{user.id}")
    assert current_balance.status_code == 200
    assert current_balance.json()["balance"] == 0.0