from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Response, Security, status

from api.v2.users.schemas import (
    GeneralSettingsModel,
    GlintV1SettingsModel,
    LoginInputModel,
    NetSettingsModel,
    SecuritySettingsModel,
    TokenResponseModel,
    UserClientSettingsDataModel,
    UserClientSettingsResponseModel,
)
from core.db import get_user
from core.errors import (
    CREDENTIALS_ERR,
    MFA_ADFS_REQUIRED_ERR,
    MFA_HARDWARE_TOKEN_REQUIRED_ERR,
    MFA_OTP_REQUIRED_ERR,
    MFA_OTP_VALIDATION_ERR,
)
from core.schemas import DEFAULT_RESPONSES, AuthValidationErrorModel, Token, TokenData, User, ValidationErrorModel
from core.utils import authenticate_user_with_password, get_current_active_user

v2_users_router = APIRouter(tags=["users"], prefix="/users")


@v2_users_router.post(
    "/login/",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": TokenResponseModel},
        status.HTTP_428_PRECONDITION_REQUIRED: {"model": AuthValidationErrorModel},
    },
)
async def login_for_access_token(user_input: LoginInputModel) -> TokenResponseModel:
    """Ручка получения jwt-токенов.

    Если у пользователя включен MFA, вернется 428 Precondition Required.
    Описания err_code:\n
        err_code: 100 - клиент должен отправить код (next_step ведет на эту же ручку)
        err_code: 101 - клиент должен перейти на страницу входа AD FS (next_step)
        err_code: 102 - клиент должен перейти на страницу входа по токену (next_step)
        err_code: 103 - OTP-код не прошел валидацию
    """
    user_obj: dict[str, Any] | None = get_user(user_input.username)
    if not user_obj:
        raise CREDENTIALS_ERR

    if user_obj["otp_enabled"] and not user_input.otp_code:
        # клиент должен отправить код
        raise MFA_OTP_REQUIRED_ERR
    elif user_obj["otp_enabled"] and user_input.otp_code:
        if not user_input.otp_code == datetime.now().strftime("%y%m%d"):
            raise MFA_OTP_VALIDATION_ERR
    if user_obj["adfs_enabled"]:
        # вход выполняется на страницах AD FS, клиент тут передать ничего не сможет, будет сгенерирована отдельная страница входа
        raise MFA_ADFS_REQUIRED_ERR
    if user_obj["hardware_token_enabled"]:
        # клиент должен отправить токен
        raise MFA_HARDWARE_TOKEN_REQUIRED_ERR

    authenticated_user: User | None = authenticate_user_with_password(user_input.username, user_input.password)
    if not authenticated_user:
        raise CREDENTIALS_ERR

    _atd = TokenData(
        username=authenticated_user.username,
        sub=authenticated_user.id,
        roles=authenticated_user.roles,
        domain=None,
        exp=(datetime.now(timezone.utc) + timedelta(hours=24)).timestamp(),
        client_id=f"{authenticated_user.id}",
    )
    return TokenResponseModel(data=Token(access_token=_atd.encode(), refresh_token=""))


@v2_users_router.post(
    "/logout/", status_code=status.HTTP_205_RESET_CONTENT, responses=DEFAULT_RESPONSES, response_class=Response
)
async def logout(user: Annotated[User, Security(get_current_active_user)]):
    print(f"{user=}")  # noqa T201
    return None


@v2_users_router.get("/settings/", responses=DEFAULT_RESPONSES, response_model=UserClientSettingsResponseModel)
async def settings(user: Annotated[User, Security(get_current_active_user)]):
    return UserClientSettingsResponseModel(
        data=UserClientSettingsDataModel(
            general=GeneralSettingsModel(),
            net=NetSettingsModel(),
            security=SecuritySettingsModel(
                otp_enabled=user.otp_enabled,
                adfs_enabled=user.adfs_enabled,
                hardware_token_enabled=user.hardware_token_enabled,
            ),
            protocols=[GlintV1SettingsModel()],
        )
    )
