from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from core.db import get_user
from core.errors import FORBIDEN_ERR, TOKEN_TYPE_ERR
from core.schemas import TokenData, User

api_access_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def authenticate_user(username: str, password: str) -> User | None:
    user = get_user(username)
    if not user or user["disabled"]:
        return None

    # if not verify_password(password, user.hashed_password):
    #     return False  # noqa ERA001

    return User(**user)


async def validate_api_access_key(api_key_header: str = Security(api_access_key_header)):
    """Проверка jwt-access-токена пользователя."""
    try:
        token_type, token_value = api_key_header.split(" ")
        if token_type != "JWT":
            raise TOKEN_TYPE_ERR
        return TokenData.decode(token_value)
    except Exception as e:
        print(e)  # noqa T201

    # TODO: проверка токена в сессиях?
    raise FORBIDEN_ERR


async def get_current_active_user(token: Annotated[TokenData, Depends(validate_api_access_key)]) -> User:
    # https://github.com/devalv/yawm/blob/main/backend/core/services/security/auth.py
    # TODO: прочитать содержимое токена и извлечь пользователя из БД
    user: User | None = authenticate_user(token.username, "")
    if not user:
        raise FORBIDEN_ERR
    return user
