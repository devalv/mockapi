from pydantic import BaseModel


class LoginInputModel(BaseModel):
    username: str
    password: str
    ldap: bool
