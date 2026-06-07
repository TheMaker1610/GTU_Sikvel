"""
Интеграционные тесты REST API.
"""

import pytest
from fastapi.testclient import TestClient
from server.api.app import create_app
from server.storage.database import Base, engine, SessionLocal
from server.storage.models import User
from server.auth.auth_service import hash_password


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter(User.username == "testadmin").first():
        db.add(User(username="testadmin", hashed_password=hash_password("Test1234!"), role="admin"))
    if not db.query(User).filter(User.username == "testop").first():
        db.add(User(username="testop", hashed_password=hash_password("Op1234!"), role="operator"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_token(client):
    resp = client.post("/token", data={"username": "testadmin", "password": "Test1234!"})
    return resp.json()["access_token"]
