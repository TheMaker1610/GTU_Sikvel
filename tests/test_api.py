"""
Интеграционные тесты REST API.
"""

import pytest
from fastapi.testclient import TestClient
from server.api.app import create_app
