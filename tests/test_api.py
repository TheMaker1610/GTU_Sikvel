"""
Интеграционные тесты REST API.
"""

import pytest
from fastapi.testclient import TestClient
from server.api.app import create_app
from server.storage.database import Base, engine, SessionLocal
from server.storage.models import User
from server.auth.auth_service import hash_password
