from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from api.v2.users.schemas import TokenData
from core.db import get_user
from core.errors import FORBIDEN_ERR
from core.schemas import User

api_access_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or user["disabled"]:
        return None

    # if not verify_password(password, user.hashed_password):
    #     return False  # noqa ERA001

    print(f"{user=}")  # noqa T201
    return User(**user)


async def validate_api_access_key(api_key_header: str = Security(api_access_key_header)):
    """Проверка jwt-access-токена пользователя."""

    print(f"{api_key_header=}")  # noqa T201
    try:
        # TODO: тут может быть исключение на split
        tt, qq = api_key_header.split(" ")
        # TODO: проверить tt
        print(f"{tt=}, {qq=}")  # noqa T201
        _tk = TokenData.decode(qq)
        return _tk
    except Exception as e:
        print(e)  # noqa T201
    # TODO: проверка токена в сессиях?
    raise FORBIDEN_ERR


async def get_current_active_user(token: Annotated[TokenData, Depends(validate_api_access_key)]) -> User:
    print(f"{token=}")  # noqa T201
    # https://github.com/devalv/yawm/blob/main/backend/core/services/security/auth.py
    # TODO: прочитать содержимое токена и извлечь пользователя из БД
    user: User | None = authenticate_user(token.username, "")
    if not user:
        raise FORBIDEN_ERR
    return user


# https://fastapi.tiangolo.com/reference/dependencies/#security
