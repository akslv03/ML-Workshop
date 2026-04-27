import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from api import app
from database.database import get_session
from unittest.mock import patch
from models.ml_model import MLModel

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///testing.db", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_rabbitmq():
    with patch("routes.predict.send_task"):
        yield

@pytest.fixture
def ml_model(session: Session):
    model = MLModel(
        id=1,
        name="test_model",
        description="Test model", 
        cost_per_prediction=5.0
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model