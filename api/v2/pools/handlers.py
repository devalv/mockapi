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
    MachineStartGlintRequestModel,
    MachineStartGlintResponseModel,
    PoolShortModel,
    TaskResponseModel,
)
from api.v2.tasks.schemas import TaskShortModel
from core.db import get_user_machines, get_user_pools
from core.enums import ConnectionTypesMap, EnitityStatuses, PermissionTypes, TaskKinds, TaskStatuses
from core.errors import NO_ELIGIBLE_MACHINE_ERR, NO_PERM_ERR, POOL_EXPAND_FAILED_ERR
from core.schemas import DEFAULT_RESPONSES, User, ValidationErrorModel
from core.unifiers import UnifiedPage
from core.utils import (
    get_current_active_user,
    get_user_pool_active_task,
    get_user_pool_expand_done_task,
    get_user_start_glint_active_task,
    get_user_start_glint_done_task,
    get_ws_connection_active_user,
    start_glint_data_task,
    start_pool_expand_data_task,
)
from core.ws import ws_manager

v2_pools_router = APIRouter(tags=["pools"], prefix="/pools")
background_tasks = set()


# TODO: избавиться от дублирования


@v2_pools_router.get(
    "/", status_code=status.HTTP_200_OK, responses=DEFAULT_RESPONSES, response_model=UnifiedPage[PoolShortModel]
)
async def pools(
    user: Annotated[User, Security(get_current_active_user)], is_favorite: bool = False
) -> UnifiedPage[PoolShortModel]:
    """Список пулов назначенных пользователю.

    Если задача завершилась неуспешно - вернется провал.
    Если задача выполнена - вернутся данные на подключение.
    Если задача ещё выполняется - вернется активная задача.
    """
    db_pools: list[dict[str, Any]] = get_user_pools(str(user.id))
    model_pools: list[PoolShortModel] = list()
    for db_pool in db_pools:
        if is_favorite and not db_pool["is_favorite"]:
            continue
        model_pools.append(PoolShortModel(**db_pool))
    return paginate(model_pools)


@v2_pools_router.get(
    "/{id}/connect/",
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": TaskResponseModel},
        status.HTTP_202_ACCEPTED: {"model": TaskResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
)
async def pool_connect_stage1(user: Annotated[User, Security(get_current_active_user)], id: UUID4) -> JSONResponse:
    """Запрос на получение машины из пула готовой к старту сессии/подключению."""

    user_has_bool: bool = False
    for db_pool in get_user_pools(str(user.id)):
        if db_pool["id"] == id.hex:
            user_has_bool = True
            break

    if not user_has_bool:
        raise NO_PERM_ERR

    if done_task := await get_user_pool_expand_done_task(f"{user.id}"):
        if done_task["status"] == TaskStatuses.CANCELLED:
            # задача была отменена и требует повторного запуска
            pass
        elif done_task["status"] == TaskStatuses.COMPLETED:
            # задача выполнена успешно - можно делать запрос на подключение (Шаг 2)
            return JSONResponse(
                TaskResponseModel(data=TaskShortModel(**done_task)).model_dump(mode="json"),
                status_code=status.HTTP_200_OK,
            )
        elif done_task["status"] == TaskStatuses.FAILED:
            # задача провалена - предположим, что пул не может расширяться или иметь подключение
            raise POOL_EXPAND_FAILED_ERR

    # пул найден - запускаем расширение
    if active_task := await get_user_pool_active_task(f"{user.id}"):
        return JSONResponse(
            TaskResponseModel(data=TaskShortModel(**active_task)).model_dump(mode="json"),
            status_code=status.HTTP_202_ACCEPTED,
        )

    expand_task_id: str = f"{uuid4()}"
    _task = asyncio.create_task(start_pool_expand_data_task(f"{user.id}", expand_task_id, pool_id=f"{id}"))
    background_tasks.add(_task)
    _task.add_done_callback(background_tasks.discard)

    return JSONResponse(
        TaskResponseModel(
            data=TaskShortModel(**{
                "status": TaskStatuses.PENDING,
                "created": datetime.now(timezone.utc),
                "started": None,
                "finished": None,
                "id": expand_task_id,
                "kind": TaskKinds.POOL_EXPAND,
            })
        ).model_dump(mode="json"),
        status_code=status.HTTP_202_ACCEPTED,
    )


@v2_pools_router.post(
    "/{id}/connect/",
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_409_CONFLICT: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": MachineStartGlintResponseModel},
        status.HTTP_202_ACCEPTED: {"model": TaskResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
)
async def pool_connect_stage2(
    user: Annotated[User, Security(get_current_active_user)], id: UUID4, request_model: MachineStartGlintRequestModel
) -> JSONResponse:
    """Запрос на подключение к пулу после выполненной задачи.

    Если задача завершилась неуспешно || отменена - будет перезапуск.
    Если задача выполнена - вернутся данные на подключение.
    Если задача ещё выполняется - вернется активная задача.
    Тут при подключении пересылаются данные для подключения лаунчером.
    """

    user_has_bool: bool = False
    for db_pool in get_user_pools(str(user.id)):
        if db_pool["id"] == id.hex:
            user_has_bool = True
            break

    if not user_has_bool:
        raise NO_PERM_ERR

    user_machines: list[dict[str, Any]] = get_user_machines(f"{user.id}")
    eligible_machine_found: bool = False
    for user_machine in user_machines:
        if user_machine["pool_id"] == f"{id}":
            eligible_machine_found = True
            break
    if not eligible_machine_found:
        raise NO_ELIGIBLE_MACHINE_ERR

    # на реальных данных, тут есть проверка статуса ВМ/ФМ
    if done_task := await get_user_start_glint_done_task(f"{user.id}"):
        if done_task["status"] in (TaskStatuses.CANCELLED, TaskStatuses.FAILED):
            # задача была отменена/провалена и требует повторного запуска
            pass
        elif done_task["status"] == TaskStatuses.COMPLETED:
            # задача выполнена успешно - возвращаем данные для подключения
            return JSONResponse(
                MachineStartGlintResponseModel(
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

    # машина найдена - запускаем расширение
    if active_task := await get_user_start_glint_active_task(f"{user.id}"):
        return JSONResponse(
            TaskResponseModel(data=TaskShortModel(**active_task)).model_dump(mode="json"),
            status_code=status.HTTP_202_ACCEPTED,
        )

    start_glint_task_id: str = f"{uuid4()}"
    connect_task = asyncio.create_task(start_glint_data_task(f"{user.id}", start_glint_task_id, pool_id=f"{id}"))
    background_tasks.add(connect_task)
    connect_task.add_done_callback(background_tasks.discard)

    return JSONResponse(
        TaskResponseModel(
            data=TaskShortModel(**{
                "status": TaskStatuses.PENDING,
                "created": datetime.now(timezone.utc),
                "started": None,
                "finished": None,
                "id": start_glint_task_id,
                "kind": TaskKinds.GLINT_START,
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
