import time

import jwt
import pytest

from app.core.config import settings
from app.core.exceptions import InvalidTokenError
from app.core.security import create_access_token, decode_access_token


def test_create_and_decode_access_token():
    user_id = 123

    token = create_access_token(user_id)

    decoded_user_id = decode_access_token(token)

    assert isinstance(token, str)
    assert decoded_user_id == user_id


def test_decode_invalid_access_token():
    with pytest.raises(InvalidTokenError):
        decode_access_token("invalid.token.value")


def test_decode_expired_access_token():
    now = int(time.time())

    payload = {
        "sub": "123",
        "iat": now - 120,
        "exp": now - 60,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)