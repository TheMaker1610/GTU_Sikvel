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
    def test_create_and_decode_token(self):
        data = {"sub": "test_user", "role": "operator"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["role"] == "operator"

    def test_invalid_token(self):
        payload = decode_token("invalid.token.here")
        assert payload is None
