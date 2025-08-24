from typing import Annotated, Any

from fastapi import APIRouter, Security, status
from pydantic import UUID4

from api.v2.tasks.schemas import TaskIsDoneModel, TaskIsDoneResponseModel, TaskShortModel, TaskShortResponseModel
from core.db import get_user_task
from core.enums import TaskStatuses
from core.errors import NOT_FOUND_ERR
from core.schemas import User, ValidationErrorModel
from core.utils import get_current_active_user

v2_tasks_router = APIRouter(tags=["tasks"], prefix="/tasks")


@v2_tasks_router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": TaskShortResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
    response_model=TaskShortResponseModel,
)
async def task(user: Annotated[User, Security(get_current_active_user)], task_id: UUID4) -> TaskShortResponseModel:
    """Доступна автору задачи и администратору."""
    user_task: dict[str, Any] = get_user_task(f"{user.id}", f"{task_id}")
    if not user_task:
        raise NOT_FOUND_ERR
    return TaskShortResponseModel(data=TaskShortModel(id=task_id, **user_task))


@v2_tasks_router.get(
    "/{task_id}/is-done",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ValidationErrorModel},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ValidationErrorModel},
        status.HTTP_200_OK: {"model": TaskIsDoneResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": ValidationErrorModel},
    },
    response_model=TaskIsDoneResponseModel,
)
async def is_done(user: Annotated[User, Security(get_current_active_user)], task_id: UUID4) -> TaskIsDoneResponseModel:
    """Доступна автору задачи и администратору."""
    user_task: dict[str, Any] = get_user_task(f"{user.id}", f"{task_id}")
    if not user_task:
        raise NOT_FOUND_ERR
    if user_task["status"] in (TaskStatuses.COMPLETED, TaskStatuses.FAILED):
        return TaskIsDoneResponseModel(data=TaskIsDoneModel(is_done=True))
    return TaskIsDoneResponseModel(data=TaskIsDoneModel(is_done=False))
