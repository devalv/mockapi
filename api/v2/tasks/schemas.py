from datetime import datetime

from pydantic import UUID4, BaseModel, PastDatetime

from core.enums import TaskStatuses


class TaskShortModel(BaseModel):
    """Сокращённое описание задачи доступное автору/администратору."""

    id: UUID4
    status: TaskStatuses
    created: PastDatetime
    started: datetime | None
    finished: datetime | None


class TaskShortResponseModel(BaseModel):
    data: TaskShortModel


class TaskIsDoneModel(BaseModel):
    is_done: bool


class TaskIsDoneResponseModel(BaseModel):
    data: TaskIsDoneModel
