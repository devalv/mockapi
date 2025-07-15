from pydantic import BaseModel

from core.schemas import Token


class LoginInputModel(BaseModel):
    username: str
    password: str
    ldap: bool


class TokenResponseModel(BaseModel):
    data: Token
