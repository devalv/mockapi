from typing import Annotated, Any

from fastapi import APIRouter, Security, status

from api.v2.pools.schemas import PoolShortModel
from core.db import get_user_pools
from core.schemas import DEFAULT_RESPONSES, User
from core.utils import get_current_active_user

# TODO: единый формат ответа с ошибкой и без - data, errors - data всегда list?
# TODO: валидация заголовка с access_token пользователя

v2_pools_router = APIRouter(tags=["pools"], prefix="/pools")


@v2_pools_router.get(
    "/", status_code=status.HTTP_200_OK, responses=DEFAULT_RESPONSES, response_model=list[PoolShortModel]
)
async def pools(user: Annotated[User, Security(get_current_active_user)]):
    """Список пулов назначенных пользователю."""
    # TODO: добавить пагинатор
    db_pools: list[dict[str, Any]] = get_user_pools(str(user.id))
    model_pools: list[PoolShortModel] = list()
    for db_pool in db_pools:
        model_pools.append(PoolShortModel(**db_pool))
    return model_pools
