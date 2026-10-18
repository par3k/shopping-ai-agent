from datetime import timedelta

import pytest
from jose import JWTError

from app.services.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plain_and_verifies():
    hashed = hash_password("password1")

    assert hashed != "password1"
    assert verify_password("password1", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_token_roundtrip():
    token = create_access_token({"sub": "1"})

    assert decode_access_token(token)["sub"] == "1"


def test_expired_token_raises():
    token = create_access_token({"sub": "1"}, timedelta(seconds=-1))

    with pytest.raises(JWTError):
        decode_access_token(token)


def test_tampered_token_raises():
    token = create_access_token({"sub": "1"})
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(JWTError):
        decode_access_token(tampered)


def test_each_token_has_unique_jti():
    first = decode_access_token(create_access_token({"sub": "1"}))
    second = decode_access_token(create_access_token({"sub": "1"}))

    assert first["jti"]
    assert first["jti"] != second["jti"]
