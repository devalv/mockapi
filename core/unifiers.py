from typing import Generic, TypeVar

from fastapi_pagination import Page
from pydantic import Field

T = TypeVar("T")


class UnifiedPage(Page[T], Generic[T]):
    items: list[T] = Field(..., alias="data")  # type: ignore

    model_config = {
        "populate_by_name": True,
    }


def singleton(cls):
    """Декоратор превращающий класс в синглтон (с учётом аргумента db)."""
    __instances = {}

    def get_instance(*args, **kwargs):
        _ins_n: str = f"{cls.__name__}"
        if _ins_n not in __instances:
            __instances[_ins_n] = cls(*args, **kwargs)

        return __instances[_ins_n]

    return get_instance
