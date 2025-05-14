from datetime import datetime, timezone
from typing import Any, TypeVar

from jose.constants import ALGORITHMS
from jose import jwt
from pydantic import UUID4, confloat, BaseModel, field_validator

T = TypeVar("T", bound="TokenData")


class TokenData(BaseModel):
    sub: UUID4
    username: str
    exp: float | datetime = confloat(gt=datetime.now(timezone.utc).timestamp())
    roles: list[str]
    domain: str | None

    @classmethod
    def decode(cls, token: str) -> T:
        # TODO: SECRET_KEY точно должен быть частью настроек (https://github.com/devalv/yawm/blob/main/backend/core/schemas/security/oauth2.py)
        decoded_token: dict[str, Any] = jwt.decode(
            token, "super-secret", algorithms=[ALGORITHMS.HS256]
        )

        print(f"{decoded_token=}")
        return cls(**decoded_token)

    def encode(self) -> str:
        return jwt.encode(
            self.model_dump(mode="json"),
            "super-secret", 
            algorithm=ALGORITHMS.HS256
        )


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

    # @field_validator("typ")
    # def typ_check(cls, value: str) -> str:
    #     assert value == "JWT"
    #     return value

    # @field_validator("alg")
    # def alg_check(cls, value: str) -> str:
    #     assert value == ALGORITHMS.HS256
    #     return value

    @field_validator("token_type")
    def token_type_check(cls, value: str) -> str:
        assert value.lower() == "bearer"
        return value