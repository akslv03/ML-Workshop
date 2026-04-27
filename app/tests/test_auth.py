from models.user import User
from sqlmodel import select

def test_signup(client, session):
    response = client.post("/auth/signup", json={
        "username": "tester",
        "email": "test@test.ru",
        "password": "password123"
    })
    
    assert response.status_code == 201
    assert response.json() == {"message": "User successfully registered"}
    
    user = session.exec(select(User).where(User.email == "test@test.ru")).first()
    assert user is not None
    assert user.username == "tester"

def test_login_and_get_token(client):
    client.post("/auth/signup", json={
        "username": "tester",
        "email": "test@test.ru",
        "password": "password123"
    })
    
    response = client.post("/auth/token", data={
        "username": "test@test.ru",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert "DESCRIPTION_API" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_signup_short_password(client):
    response = client.post("/auth/signup", json={
        "username": "tester",
        "email": "shortpass@test.ru",
        "password": "123"
    })
    
    assert response.status_code == 422
    assert "detail" in response.json()

