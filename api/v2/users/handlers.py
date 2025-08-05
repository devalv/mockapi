from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Response, Security, status

from api.v2.users.schemas import (
    GlintV1SettingsModel,
    LoginInputModel,
    MainSettingsModel,
    SecuritySettingsModel,
    ServiceSettingsModel,
    TokenResponseModel,
    UserClientSettingsDataModel,
    UserClientSettingsModel,
)
from core.errors import CREDENTIALS_ERR
from core.schemas import DEFAULT_RESPONSES, Token, TokenData, User, ValidationErrorModel
from core.utils import authenticate_user, get_current_active_user

v2_users_router = APIRouter(tags=["users"], prefix="/users")


@v2_users_router.post(
    "/login/",
    response_model=TokenResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
    },
)
async def login_for_access_token(user_input: LoginInputModel) -> TokenResponseModel:
    user: User | None = authenticate_user(user_input.username, user_input.password)
    if not user:
        raise CREDENTIALS_ERR

    _atd = TokenData(
        username=user.username,
        sub=user.id,
        roles=user.roles,
        domain=None,
        exp=(datetime.now(timezone.utc) + timedelta(hours=24)).timestamp(),
    )
    # TODO: дополнительный тип ответа требующий OTP, ADFS, TOKEN
    return TokenResponseModel(data=Token(access_token=_atd.encode(), refresh_token=""))


@v2_users_router.post(
    "/logout/", status_code=status.HTTP_205_RESET_CONTENT, responses=DEFAULT_RESPONSES, response_class=Response
)
async def logout(user: Annotated[User, Security(get_current_active_user)]):
    print(f"{user=}")  # noqa T201
    return None


@v2_users_router.get("/settings/", responses=DEFAULT_RESPONSES, response_model=UserClientSettingsModel)
async def settings(user: Annotated[User, Security(get_current_active_user)]):
    return UserClientSettingsModel(
        data=UserClientSettingsDataModel(
            service=ServiceSettingsModel(),
            security=SecuritySettingsModel(),
            main=MainSettingsModel(),
            glint_v1=GlintV1SettingsModel(),
        )
    )
