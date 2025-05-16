from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import status
from jose import jwt
from jose.constants import ALGORITHMS
from pydantic import UUID4, BaseModel, field_validator

from core.enums import ErrorCodes


class TokenData(BaseModel):
    sub: UUID4
    username: str
    exp: float
    roles: list[str]
    domain: str | None

    @classmethod
    def decode(cls, token: str) -> "TokenData":
        # TODO: SECRET_KEY точно должен быть частью настроек (https://github.com/devalv/yawm/blob/main/backend/core/schemas/security/oauth2.py)
        decoded_token: dict[str, Any] = jwt.decode(token, "super-secret", algorithms=[ALGORITHMS.HS256])
        return cls(**decoded_token)

    def encode(self) -> str:
        return jwt.encode(self.model_dump(mode="json"), "super-secret", algorithm=ALGORITHMS.HS256)

    @field_validator("exp")
    def exp_check(cls, value: float) -> float:
        assert value > datetime.now(timezone.utc).timestamp()
        return value


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "JWT"

    @field_validator("token_type")
    def token_type_check(cls, value: str) -> str:
        assert value.lower() == "jwt"
        return value


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


DEFAULT_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
}
