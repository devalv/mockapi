from typing import Any
from uuid import UUID

from fastapi import status
from pydantic import BaseModel

from core.enums import ErrorCodes


class User(BaseModel):
    id: UUID
    username: str
    disabled: bool
    roles: list[str]
    email: str | None = None
    full_name: str | None = None


class DetailContent(BaseModel):
    """Детаем ошибку в виде стандартного ответа валидатора Fastapi
    Пример:
    {
        "detail": [
        {
            "type": "missing",
            "loc": [
                "body",
                "username"
            ],
            "msg": "Field required",
            "err": 123,
            "input": {
                "password": "Bazalt1!",
                "ldap": false
            }
        }
        ]
    }
    """

    msg: str
    err_code: ErrorCodes = ErrorCodes.UNKNOWN
    type: str = "default"


class ValidationErrorModel(BaseModel):
    detail: list[DetailContent]


# TODO: ответа может быть 2 вида - для входа это 401 и 422, для остальных - 403 и 422
default_responses: dict[int, dict[str, Any]] = {
    status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
}
