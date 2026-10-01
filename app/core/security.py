from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenError


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {"sub": str(user_id), "iat": now, "exp": expires_at}

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm,)


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm],
            options={
                "require": ["sub", "iat", "exp"],
            },
        )

        user_id = int(payload["sub"])

        return user_id

    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise InvalidTokenError() from exc