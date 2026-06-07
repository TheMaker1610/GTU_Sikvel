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
    def test_hash_and_verify(self):
        password = "SecurePass123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_wrong_password(self):
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_not_plain(self):
        password = "my_password"
        hashed = hash_password(password)
        assert hashed != password


class TestJWT:
    pass
