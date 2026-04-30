from models.user import User
from sqlmodel import select

def test_balance_operations(client, session):
    client.post("/auth/signup", json={
        "username": "tester_balance",
        "email": "user@test.ru",
        "password": "password123"
    })
    
    user = session.exec(select(User).where(User.email == "user@test.ru")).first()
    
    topup_response = client.post(f"/api/balance/{user.id}/topup", json={"amount": 150.0})
    assert topup_response.status_code == 200
    assert topup_response.json() == {"message": "Successfully toped up balance by 150.0"}
    
    balance_response = client.get(f"/api/balance/{user.id}")
    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 150.0
