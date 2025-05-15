from core.db import get_user
from core.schemas import User

# oauth2_scheme = HTTPBearer(tokenUrl="/api/v2/users/login/")  # noqa ERA005


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user or user["disabled"]:
        return None

    # if not verify_password(password, user.hashed_password):
    #     return False  # noqa ERA001

    print(f"{user=}")  # noqa T201
    return User(**user)


async def get_current_active_user(
    access_token: str | None = None,
    refresh_token: str | None = None,
    # *args, **kwargs
) -> User:
    print(f"{access_token=}\n{refresh_token=}")  # noqa T201
    # https://github.com/devalv/yawm/blob/main/backend/core/services/security/auth.py
    pass


# https://fastapi.tiangolo.com/reference/dependencies/#security
