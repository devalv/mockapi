import asyncio
from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Security, WebSocket, status
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate
from pydantic import UUID4

from api.v2.pools.schemas import (
    PoolGetMachineActiveTaskResponseModel,
    PoolGetMachineRequestModel,
    PoolGetMachineResponseModel,
    PoolShortModel,
)
from api.v2.tasks.schemas import TaskShortModel
from core.db import get_user_pools
from core.enums import TaskStatuses
from core.errors import NOT_FOUND_ERR, POOL_EXPAND_FAILED_ERR
from core.schemas import DEFAULT_RESPONSES, User, ValidationErrorModel
from core.unifiers import UnifiedPage
from core.utils import (
    get_current_active_user,
    get_user_active_task,
    get_user_done_task,
    start_pool_connection_data_task,
)

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
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": PoolGetMachineResponseModel},
        status.HTTP_202_ACCEPTED: {"model": PoolGetMachineActiveTaskResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
)
async def pool_connect(
    user: Annotated[User, Security(get_current_active_user)], id: UUID4, request_model: PoolGetMachineRequestModel
) -> JSONResponse:
    """Получение машины из пула.

    Если у пользователя есть права доступа к пулу, но, отсутствует машина - выполняется попытка создания новой и закрепление её за пользователем.
    """
    # TODO: wip
    # TODO: отдельная ручка для каждого вида пулов?

    # TODO: сценарий, когда пул не может расширяться (дополнительный атрибут в "БД")

    user_has_bool: bool = False
    for db_pool in get_user_pools(str(user.id)):
        if db_pool["id"] == id.hex:
            user_has_bool = True
            break

    if not user_has_bool:
        raise NOT_FOUND_ERR

    # TODO: есть уже выполненная задача - возвращаем данные для подключения к пулу
    if done_task := await get_user_done_task(f"{user.id}"):
        if done_task["status"] == TaskStatuses.CANCELLED:
            # задача была отменена и требует повторного запуска
            pass
        elif done_task["status"] == TaskStatuses.COMPLETED:
            # задача выполнена успешно - возвращаем данные для подключения
            # TODO: wip
            # return JSONResponse()  # noqa ERA001
            raise NotImplementedError
        elif done_task["status"] == TaskStatuses.FAILED:
            # задача провалена - предположим, что пул не может расширяться или иметь подключение
            raise POOL_EXPAND_FAILED_ERR

    # пул найден - запускаем расширение
    if active_task := await get_user_active_task(f"{user.id}"):
        return JSONResponse(
            PoolGetMachineActiveTaskResponseModel(data=TaskShortModel(**active_task)).model_dump(mode="json"),
            status_code=status.HTTP_202_ACCEPTED,
        )

    expand_task_id: str = f"{uuid4()}"
    connect_task = asyncio.create_task(start_pool_connection_data_task(f"{user.id}", expand_task_id))
    background_tasks.add(connect_task)
    connect_task.add_done_callback(background_tasks.discard)

    return JSONResponse(
        PoolGetMachineActiveTaskResponseModel(
            data=TaskShortModel(**{
                "status": TaskStatuses.PENDING,
                "created": datetime.now(timezone.utc),
                "started": None,
                "finished": None,
                "id": expand_task_id,
            })
        ).model_dump(mode="json"),
        status_code=status.HTTP_202_ACCEPTED,
    )


@v2_pools_router.websocket("/ws")
async def pools_ws(websocket: WebSocket) -> None:
    # TODO: wip - отправка сообщений о статусе выполнения задачи
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
