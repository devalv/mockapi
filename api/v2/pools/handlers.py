import asyncio
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Security, WebSocket, status
from fastapi_pagination import paginate
from pydantic import UUID4

from api.v2.pools.schemas import (
    PoolGetMachineRequestModel,
    PoolGetMachineResponseModel,
    PoolShortModel,
    PoolShortResponseModel,
)
from core.db import get_user_pools
from core.errors import NOT_FOUND_ERR
from core.schemas import DEFAULT_RESPONSES, User, ValidationErrorModel
from core.unifiers import UnifiedPage
from core.utils import get_current_active_user, start_pool_connection_data_task

v2_pools_router = APIRouter(tags=["pools"], prefix="/pools")
background_tasks = set()


@v2_pools_router.get(
    "/", status_code=status.HTTP_200_OK, responses=DEFAULT_RESPONSES, response_model=UnifiedPage[PoolShortModel]
)
async def pools(
    user: Annotated[User, Security(get_current_active_user)], is_favorite: bool = False
) -> UnifiedPage[PoolShortModel]:
    """Список пулов назначенных пользователю."""
    db_pools: list[dict[str, Any]] = get_user_pools(str(user.id))
    model_pools: list[PoolShortModel] = list()
    for db_pool in db_pools:
        if is_favorite and not db_pool["is_favorite"]:
            continue
        model_pools.append(PoolShortModel(**db_pool))
    return paginate(model_pools)


@v2_pools_router.post(
    "/{id}/connect/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_201_CREATED: {"model": PoolGetMachineResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
    response_model=PoolGetMachineResponseModel,
)
async def pool_connect(
    user: Annotated[User, Security(get_current_active_user)], id: UUID4, request_model: PoolGetMachineRequestModel
) -> PoolShortResponseModel:
    """Получение машины из пула.

    Если у пользователя есть права доступа к пулу, но, отсутствует машина - выполняется попытка создания новой и закрепление её за пользователем.
    """
    # TODO: отдельная ручка для каждого вида пулов?
    # TODO: отдельная ручка для получения машины (когда она уже есть?) Если машины нет - отвечаем, что машины нет - надо попробовать получить.
    # TODO: wip

    # TODO: вынести на уровень Dependency Injection
    db_pools: list[dict[str, Any]] = get_user_pools(str(user.id))
    user_pool: PoolShortModel | None = None
    for db_pool in db_pools:
        if db_pool["id"] == id.hex:
            user_pool = PoolShortModel(**db_pool)
            break
    if not user_pool:
        raise NOT_FOUND_ERR
    # пул найден - запускаем расширение
    # TODO: проверить нет ли у пользователя уже задачи на подключение к этому пулу?

    # TODO: как в случае ошибки пользователю будет показана информация? Можно показывать статус выполнения завершенной задачи как сообщение об ошибке?
    # TODO: например, через код ошибки
    expand_task_id: str = f"{uuid4()}"
    connect_task = asyncio.create_task(start_pool_connection_data_task(f"{user.id}", expand_task_id))
    background_tasks.add(connect_task)
    connect_task.add_done_callback(background_tasks.discard)

    return PoolShortResponseModel(data=user_pool)


@v2_pools_router.websocket("/ws")
async def pools_ws(websocket: WebSocket) -> None:
    # TODO: wip - отправка сообщений о статусе выполнения задачи
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
