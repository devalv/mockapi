from datetime import datetime, timezone
from typing import Any

from jose import jwt
from jose.constants import ALGORITHMS
from pydantic import UUID4, BaseModel, confloat, field_validator


class TokenData(BaseModel):
    sub: UUID4
    username: str
    exp: type[float] | datetime | float = confloat(gt=datetime.now(timezone.utc).timestamp())
    roles: list[str]
    domain: str | None

    @classmethod
    def decode(cls, token: str) -> "TokenData":
        # TODO: SECRET_KEY точно должен быть частью настроек (https://github.com/devalv/yawm/blob/main/backend/core/schemas/security/oauth2.py)
        decoded_token: dict[str, Any] = jwt.decode(token, "super-secret", algorithms=[ALGORITHMS.HS256])

        print(f"{decoded_token=}")  # noqa T201
        return cls(**decoded_token)

    def encode(self) -> str:
        return jwt.encode(self.model_dump(mode="json"), "super-secret", algorithm=ALGORITHMS.HS256)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

    # @field_validator("typ")
    # def typ_check(cls, value: str) -> str:
    #     assert value == "JWT"  # noqa ERA001
    #     return value  # noqa ERA001

    # @field_validator("alg")
    # def alg_check(cls, value: str) -> str:
    #     assert value == ALGORITHMS.HS256  # noqa ERA001
    #     return value  # noqa ERA001

    @field_validator("token_type")
    def token_type_check(cls, value: str) -> str:
        assert value.lower() == "bearer"
        return value


class LoginInputModel(BaseModel):
    username: str
    password: str
    ldap: bool
