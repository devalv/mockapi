import asyncio
from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Security, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate
from pydantic import UUID4

from api.v2.pools.schemas import (
    MachineShortResponseModel,
    PoolGetMachineActiveTaskResponseModel,
    PoolGetMachineRequestModel,
    PoolGetMachineResponseModel,
    PoolShortModel,
)
from api.v2.tasks.schemas import TaskShortModel
from core.db import get_user_pools
from core.enums import ConnectionTypesMap, EnitityStatuses, PermissionTypes, TaskStatuses
from core.errors import NO_PERM_ERR, POOL_EXPAND_FAILED_ERR
from core.schemas import DEFAULT_RESPONSES, User, ValidationErrorModel
from core.unifiers import UnifiedPage
from core.utils import (
    get_current_active_user,
    get_user_active_task,
    get_user_done_task,
    get_ws_connection_active_user,
    start_pool_connection_data_task,
)
from core.ws import ws_manager

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


# TODO: @v2_pools_router.get(
# "/{id}/", status_code=status.HTTP_202_ACCEPTED, responses=DEFAULT_RESPONSES, response_model=PoolShortResponseModel)
# TODO: в этой ручке мы готовим ВМ и пул для подключения?


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
    """Запрос на подключение к пулу после выполненной задачи.

    Если нет выполненной задачи или задача завершилась неуспешно - вернется провал.
    Если задача выполнена - вернутся данные на подключение.
    Если задача ещё выполняется - вернется активная задача?
    Тут при подключении пересылаются данные для подключения лаунчером.
    TODO: Подключаясь к пулу, лаунчер должен запустить задачу на подключение (отдельную - тут мы будем вощварщать её результат?).
    """

    user_has_bool: bool = False
    for db_pool in get_user_pools(str(user.id)):
        if db_pool["id"] == id.hex:
            user_has_bool = True
            break

    if not user_has_bool:
        raise NO_PERM_ERR

    if done_task := await get_user_done_task(f"{user.id}"):
        if done_task["status"] == TaskStatuses.CANCELLED:
            # задача была отменена и требует повторного запуска
            pass
        elif done_task["status"] == TaskStatuses.COMPLETED:
            # задача выполнена успешно - возвращаем данные для подключения
            return JSONResponse(
                PoolGetMachineResponseModel(
                    data=MachineShortResponseModel(**{
                        "id": "fd19c462-b8f1-43cc-81a8-31abc9ff4877",
                        "verbose_name": "mock-glint-server",
                        "permissions": [PermissionTypes.VM_POWER_CONTROL],
                        "host": "10.254.150.133",
                        "port": 39897,
                        "status": EnitityStatuses.ACTIVE,
                        "protocol_id": ConnectionTypesMap.GLINTV1,
                    })
                ).model_dump(mode="json"),
                status_code=status.HTTP_200_OK,
            )
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


# TODO: @app.websocket("/ws/{client_id}")?
# TODO: async def websocket_endpoint(websocket: WebSocket, client_id: int):
@v2_pools_router.websocket("/ws/")
async def pools_update_ws(websocket: WebSocket, user: Annotated[User, Security(get_ws_connection_active_user)]) -> None:
    # TODO: client_id должен храниться в JWTтокене, тогда можно будет персонализировать сообщения конкретному клиенту
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_personal_message(f"User {user.username} sent: {data}", websocket)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
