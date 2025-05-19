from typing import Generic, TypeVar

from fastapi_pagination import Page
from pydantic import Field

T = TypeVar("T")


class UnifiedPage(Page[T], Generic[T]):
    items: list[T] = Field(..., alias="data")  # type: ignore

    model_config = {
        "populate_by_name": True,
    }
