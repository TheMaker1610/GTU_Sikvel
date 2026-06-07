"""
Тесты сервиса аутентификации.
"""

import pytest
from server.auth.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    pass
