from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Security, status

from api.v2.users.schemas import LoginInputModel, Token, TokenData
from core.db import fake_users_db
from core.errors import CREDENTIALS_ERR
from core.schemas import User, ValidationErrorModel, default_responses
from core.utils import authenticate_user, get_current_active_user

v2_users_router = APIRouter(tags=["users", "v2"], prefix="/users")


@v2_users_router.post(
    "/login/",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
    },
)
async def login_for_access_token(user_input: LoginInputModel) -> Token:
    print(f"{user_input.username=}, {user_input.password=}, {user_input.ldap=}")  # noqa T201
    user: User | None = authenticate_user(fake_users_db, user_input.username, user_input.password)
    if not user:
        raise CREDENTIALS_ERR

    print(f"{user=}")  # noqa T201
    _atd = TokenData(
        username=user.username,
        sub=user.id,
        roles=user.roles,
        domain=None,
        exp=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    print(f"{_atd=}")  # noqa T201
    return Token(access_token=_atd.encode(), refresh_token="")


@v2_users_router.post("/logout/", status_code=status.HTTP_205_RESET_CONTENT, responses=default_responses)
async def logout(user: Annotated[User, Security(get_current_active_user)]):
    # TODO: валидация токена и определение пользователя
    return


@v2_users_router.get("/settings/")
async def settings():
    # TODO: валидация токена и определение пользователя
    raise NotImplementedError
