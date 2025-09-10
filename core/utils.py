import asyncio
from datetime import datetime, timezone
from random import choice, randint
from typing import Annotated, Any, Union
from uuid import UUID, uuid4

from fastapi import Depends, Header, Security
from fastapi.security import APIKeyHeader

from core.db import fake_tasks_db, get_user, fake_machines_db, fake_users_machines_db
from core.enums import EnitityStatuses, TaskKinds, TaskStatuses
from core.errors import FORBIDEN_ERR, TOKEN_TYPE_ERR
from core.schemas import TokenData, User
from core.ws import ws_manager

api_access_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def authenticate_user(username: str, password: str) -> User | None:
    user = get_user(username)
    if not user or user["disabled"]:
        return None

    # TODO: проверка пароля

    return User(**user)


async def validate_api_access_key(api_key_header: str = Security(api_access_key_header)):
    """Проверка jwt-access-токена пользователя."""
    try:
        token_type, token_value = api_key_header.split(" ")
        if token_type != "JWT":
            raise TOKEN_TYPE_ERR
        return TokenData.decode(token_value)
    except Exception as e:
        print(e)  # noqa T201

    # TODO: проверка токена в сессиях

    raise FORBIDEN_ERR


async def get_current_active_user(token: Annotated[TokenData, Depends(validate_api_access_key)]) -> User:
    # https://github.com/devalv/yawm/blob/main/backend/core/services/security/auth.py
    # TODO: прочитать содержимое токена и извлечь пользователя из БД

    user: User | None = authenticate_user(token.username, "")
    if not user:
        raise FORBIDEN_ERR
    return user


async def get_user_token_key(cookie: Annotated[Union[str, None], Header()] = None):
    return cookie


async def validate_ws_api_access_key(api_key_header: str = Security(get_user_token_key)):
    """Проверка jwt-access-токена пользователя."""
    try:
        token_type, token_value = api_key_header.split(" ")
        if token_type != "JWT":
            raise TOKEN_TYPE_ERR
        return TokenData.decode(token_value)
    except Exception as e:
        print(e)  # noqa T201

    # TODO: проверка токена в сессиях

    raise FORBIDEN_ERR


async def get_ws_connection_active_user(token: Annotated[TokenData, Depends(validate_ws_api_access_key)]) -> User:
    user: User | None = authenticate_user(token.username, "")
    if not user:
        raise FORBIDEN_ERR
    return user


async def start_pool_expand_data_task(user_id: str, task_id: str, pool_id: str) -> None:
    if fake_tasks_db.get(user_id) is None:
        fake_tasks_db[user_id] = dict()

    fake_tasks_db[user_id][task_id] = {
        "status": TaskStatuses.PENDING,
        "created": datetime.now(timezone.utc),
        "started": None,
        "finished": None,
        "id": task_id,
        "kind": TaskKinds.POOL_EXPAND,
    }
    await asyncio.sleep(3)
    fake_tasks_db[user_id][task_id]["status"] = TaskStatuses.RUNNING
    fake_tasks_db[user_id][task_id]["started"] = datetime.now(timezone.utc)
    await ws_manager.broadcast(fake_tasks_db[user_id][task_id])
    await asyncio.sleep(randint(5, 60))
    fake_tasks_db[user_id][task_id]["status"] = choice((
        TaskStatuses.CANCELLED,
        TaskStatuses.COMPLETED,
    ))

    # если задача выполнена успешно - создаём машину и крепим её за пользователем
    if fake_tasks_db[user_id][task_id]["status"] == TaskStatuses.COMPLETED:
        new_machine_id: UUID = uuid4()
        new_machine: dict[str, Any] = {
            "id": new_machine_id.hex,
            "name": f"machine-{new_machine_id.hex[:4]}",
            "status": EnitityStatuses.ACTIVE,
            "pool_id": pool_id,
            "address": "127.0.0.1",
        }
        fake_machines_db[f"{new_machine_id}"] = new_machine
        if not fake_machines_db.get(user_id):
            fake_users_machines_db[user_id] = set()
        fake_users_machines_db[user_id].add(f"{new_machine_id}")

    fake_tasks_db[user_id][task_id]["finished"] = datetime.now(timezone.utc)
    await ws_manager.broadcast(fake_tasks_db[user_id][task_id])
    return None


async def get_user_pool_active_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    for task_id, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.PENDING, TaskStatuses.RUNNING) and task["kind"] == TaskKinds.POOL_EXPAND:
            return {"id": task_id, **task}
    return None


async def get_user_pool_expand_done_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    # задачи в статусе COMPLETED интересуют в первую очередь
    for _, task in fake_tasks_db[user_id].items():
        if task["status"] == TaskStatuses.COMPLETED and task["kind"] == TaskKinds.POOL_EXPAND:
            return task

    for _, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.FAILED, TaskStatuses.CANCELLED) and task["kind"] == TaskKinds.POOL_EXPAND:
            return task
    return None


async def get_user_start_glint_done_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    # задачи в статусе COMPLETED интересуют в первую очередь
    for _, task in fake_tasks_db[user_id].items():
        if task["status"] == TaskStatuses.COMPLETED and task["kind"] == TaskKinds.GLINT_START:
            return task

    for _, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.FAILED, TaskStatuses.CANCELLED) and task["kind"] == TaskKinds.GLINT_START:
            return task
    return None


async def get_user_start_glint_active_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    for task_id, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.PENDING, TaskStatuses.RUNNING) and task["kind"] == TaskKinds.GLINT_START:
            return {"id": task_id, **task}
    return None


async def start_glint_data_task(user_id: str, task_id: str, pool_id: str) -> None:
    if fake_tasks_db.get(user_id) is None:
        fake_tasks_db[user_id] = dict()

    fake_tasks_db[user_id][task_id] = {
        "status": TaskStatuses.PENDING,
        "created": datetime.now(timezone.utc),
        "started": None,
        "finished": None,
        "id": task_id,
        "kind": TaskKinds.GLINT_START,
    }
    await asyncio.sleep(3)
    fake_tasks_db[user_id][task_id]["status"] = TaskStatuses.RUNNING
    fake_tasks_db[user_id][task_id]["started"] = datetime.now(timezone.utc)
    await ws_manager.broadcast(fake_tasks_db[user_id][task_id])
    await asyncio.sleep(randint(5, 60))
    fake_tasks_db[user_id][task_id]["status"] = choice((
        TaskStatuses.CANCELLED,
        TaskStatuses.COMPLETED,
        TaskStatuses.FAILED,
    ))

    fake_tasks_db[user_id][task_id]["finished"] = datetime.now(timezone.utc)
    await ws_manager.broadcast(fake_tasks_db[user_id][task_id])
    return None
