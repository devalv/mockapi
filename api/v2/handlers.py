from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose.constants import ALGORITHMS
# from jose import jwt
from pydantic import BaseModel

from core.db import fake_users_db
from .schemas import Token, TokenData

users_router_v2 = APIRouter(tags=["v2/users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# @router_v2.post("/user/login/", response_model=LoginResponseModel)
# async def login():
#     return await Settings().get_settings_v3()


class LoginInputModel(BaseModel):
    username: str
    password: str
    ldap: bool


class User(BaseModel):
    id: str
    username: str
    disabled: bool = False
    roles: list[str] = ["user"]
    email: str | None = None
    full_name: str | None = None


def get_user(db, username: str):
    if username in db:
        return db[username]


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return None
    # if not verify_password(password, user.hashed_password):
    #     return False
    print(f'{user=}')
    return User(**user)


@users_router_v2.post("/login/")
async def login_for_access_token(
    user_input: LoginInputModel
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print(f'{user_input.username=}, {user_input.password=}, {user_input.ldap=}')

    # TODO: дополнительные коды ответа в схеме
    user = authenticate_user(fake_users_db, user_input.username, user_input.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f'{user=}')
    _atd = TokenData(
        username=user.username, 
        sub=str(user.id), 
        roles=user.roles, 
        domain=None, 
        exp=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    print(f'{_atd=}')

    # access_token = create_access_token(
    #     data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    # )
    return Token(access_token=_atd.encode(), refresh_token="")

# TODO: logout
@users_router_v2.post("/logout/")
async def logout():
    pass


# TODO: settings

# TODO: v2/pools router
# TODO: единый формат ответа с ошибкой и без - data, errors - data всегда list?
# TODO: валидация заголовка с access_token пользователя