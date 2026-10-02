from fastapi import HTTPAuthorizationCredentials, HTTPBearer, Depends

from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.models.models import User
from app.repositories import user_repository


security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> User:

    if credentials is None:
        raise InvalidTokenError()

    if credentials.scheme.lower() != "bearer":
        raise InvalidTokenError()

    user_id = decode_access_token(credentials.credentials)

    user = user_repository.find_by_id(user_id)

    if user is None:
        raise InvalidTokenError()

    return user