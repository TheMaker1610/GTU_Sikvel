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


@pytest.fixture(scope="module")
def operator_token(client):
    resp = client.post("/token", data={"username": "testop", "password": "Op1234!"})
    return resp.json()["access_token"]


class TestAuth:
    def test_login_success(self, client):
        resp = client.post("/token", data={"username": "testadmin", "password": "Test1234!"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        resp = client.post("/token", data={"username": "testadmin", "password": "wrong"})
        assert resp.status_code == 401

    def test_status_without_token(self, client):
        resp = client.get("/status")
        assert resp.status_code == 401


class TestStatus:
    def test_status_with_token(self, client, operator_token):
        resp = client.get("/status", headers={"Authorization": f"Bearer {operator_token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert "mode_label" in body
        assert "anomalies" in body


class TestUsers:
    def test_create_user_as_admin(self, client, admin_token):
        resp = client.post(
            "/users",
            json={"username": "new_operator", "password": "NewOp123!", "role": "operator"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
