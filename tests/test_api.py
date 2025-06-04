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
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
