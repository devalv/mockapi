import asyncio
from datetime import datetime, timezone
from random import choice, randint
from typing import Annotated, Any

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from core.db import fake_tasks_db, get_user
from core.enums import TaskStatuses
from core.errors import FORBIDEN_ERR, TOKEN_TYPE_ERR
from core.schemas import TokenData, User
from core.ws import ws_manager

api_access_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def authenticate_user(username: str, password: str) -> User | None:
    user = get_user(username)
    if not user or user["disabled"]:
        return None

    # if not verify_password(password, user.hashed_password):
    #     return False  # noqa ERA001

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

    # TODO: проверка токена в сессиях?
    raise FORBIDEN_ERR


async def get_current_active_user(token: Annotated[TokenData, Depends(validate_api_access_key)]) -> User:
    # https://github.com/devalv/yawm/blob/main/backend/core/services/security/auth.py
    # TODO: прочитать содержимое токена и извлечь пользователя из БД
    user: User | None = authenticate_user(token.username, "")
    if not user:
        raise FORBIDEN_ERR
    return user


async def start_pool_connection_data_task(user_id: str, task_id: str) -> None:
    if fake_tasks_db.get(user_id) is None:
        fake_tasks_db[user_id] = dict()

    fake_tasks_db[user_id][task_id] = {
        "status": TaskStatuses.PENDING,
        "created": datetime.now(timezone.utc),
        "started": None,
        "finished": None,
        "id": task_id,
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


async def get_user_active_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    for task_id, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.PENDING, TaskStatuses.RUNNING):
            return {"id": task_id, **task}
    return None


async def get_user_done_task(user_id: str) -> dict[str, Any] | None:
    # нет информации о задачах
    if user_id not in fake_tasks_db:
        return None

    # задачи в статусе COMPLETED интересуют в первую очередь
    for _, task in fake_tasks_db[user_id].items():
        if task["status"] == TaskStatuses.COMPLETED:
            return task

    for _, task in fake_tasks_db[user_id].items():
        if task["status"] in (TaskStatuses.FAILED, TaskStatuses.CANCELLED):
            return task
    return None
