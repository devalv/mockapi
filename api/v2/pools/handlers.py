from fastapi import APIRouter

# TODO: единый формат ответа с ошибкой и без - data, errors - data всегда list?
# TODO: валидация заголовка с access_token пользователя

v2_pools_router = APIRouter(tags=["pools", "v2"], prefix="/pools")


@v2_pools_router.get("/")
async def pools():
    """Список пулов назначенных пользователю."""
    # TODO: ограничение на пользователя
    raise NotImplementedError
